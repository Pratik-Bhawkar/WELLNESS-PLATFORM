"""
Local LLM Inference Service
Handles navigation chatbot and basic conversation using lightweight models
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Local LLM Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: int
    conversation_history: List[Dict[str, str]] = []
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    confidence: float
    model_used: str
    tokens_used: int

# Global model variables
tokenizer = None
model = None
generator = None
model_type = "none"  # Track which model is loaded

# Navigation prompts and responses
NAVIGATION_TEMPLATES = {
    "greeting": "Hello! I'm your wellness assistant. I'm here to help you navigate our mental health support system. How are you feeling today?",
    "stress_routing": "I understand you're dealing with stress. Let me connect you with our stress management specialist who can provide personalized coping strategies.",
    "anxiety_routing": "I hear that you're feeling anxious. Our anxiety support service offers evidence-based techniques to help manage these feelings. Would you like me to start a session?",
    "depression_routing": "Thank you for sharing how you're feeling. Our depression support service provides compassionate, professional guidance. Let me connect you right away.",
    "crisis_routing": "I'm concerned about what you're going through. This sounds urgent - let me immediately connect you with our crisis intervention team who are specially trained to help.",
    "help": "I can help you with:\n1. Starting a therapy session\n2. Scheduling appointments\n3. Tracking your progress\n4. Providing resources\n5. Connecting you with the right specialist\n\nWhat would you like to do?",
    "schedule": "I can help you schedule sessions. What type of support are you looking for? We have stress management, anxiety support, and depression counseling available.",
    "progress": "Let me check your progress. I can show you mood trends, session history, and improvement metrics. What would you like to see?"
}

def load_model():
    """Load the local language model - Phase 2 Enhanced with Phi-3-mini"""
    global tokenizer, model, generator, model_type
    
    try:
        # Phase 2: Try to load Phi-3-mini first (best model for RTX 4060)
        phi3_path = "./models/phi-3-mini-4k-instruct"
        
        if os.path.exists(phi3_path):
            print("🤖 Loading Phi-3-mini-4k-instruct model...")
            
            # Configure 4-bit quantization for RTX 4060 optimization
            from transformers import BitsAndBytesConfig
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            tokenizer = AutoTokenizer.from_pretrained(phi3_path, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(
                phi3_path,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True
            )
            print("✅ Phi-3-mini loaded successfully with 4-bit quantization")
            model_type = "phi3"
            return "phi3"
            
        else:
            # Fallback to DialoGPT if Phi-3 not available
            print("⚠️ Phi-3-mini not found, using DialoGPT fallback...")
            model_name = "microsoft/DialoGPT-medium"
            
            print(f"Loading model: {model_name}")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Add padding token if it doesn't exist
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            model_type = "dialogpt"
            return "dialogpt"
        
        # Create pipeline for easier inference
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1,
            max_length=100,
            do_sample=True,
            temperature=0.7
        )
        
        print("Model loaded successfully!")
        
    except Exception as e:
        print(f"Error loading model: {e}")
        # Fallback to template-based responses
        generator = None

def generate_phi3_response(message: str, context: str = None) -> Dict:
    """Generate response using Phi-3-mini model with mental wellness prompts"""
    
    if model is None or tokenizer is None:
        return {"response": "Model not loaded", "confidence": 0.0, "method": "error"}
    
    # Craft a mental wellness-focused prompt for Phi-3
    system_prompt = "You are a compassionate mental wellness assistant. Provide helpful, supportive responses to help users navigate their mental health journey."
    
    if context:
        full_prompt = f"System: {system_prompt}\nContext: {context}\nUser: {message}\nAssistant:"
    else:
        full_prompt = f"System: {system_prompt}\nUser: {message}\nAssistant:"
    
    try:
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract just the assistant's response
        response = response.split("Assistant:")[-1].strip()
        
        return {
            "response": response,
            "confidence": 0.85,
            "method": "phi3_generation"
        }
        
    except Exception as e:
        print(f"Phi-3 generation error: {e}")
        return {"response": "I'm having trouble processing that. Could you rephrase?", "confidence": 0.3, "method": "error"}

def generate_navigation_response(message: str, context: str = None) -> Dict:
    """Generate navigation response using templates, Phi-3, or fallback"""
    global model_type
    
    message_lower = message.lower()
    
    # Template-based responses for common navigation queries (fastest)
    if any(word in message_lower for word in ["hello", "hi", "start", "begin"]):
        return {
            "response": NAVIGATION_TEMPLATES["greeting"],
            "confidence": 0.9,
            "method": "template"
        }
    
    if "help" in message_lower or "what can you do" in message_lower:
        return {
            "response": NAVIGATION_TEMPLATES["help"],
            "confidence": 0.9,
            "method": "template"
        }
    
    if any(word in message_lower for word in ["schedule", "appointment", "book"]):
        return {
            "response": NAVIGATION_TEMPLATES["schedule"],
            "confidence": 0.8,
            "method": "template"
        }
    
    if "progress" in message_lower or "how am i doing" in message_lower:
        return {
            "response": NAVIGATION_TEMPLATES["progress"],
            "confidence": 0.8,
            "method": "template"
        }
    
    # Context-aware routing responses
    if context:
        if "stress" in context:
            return {
                "response": NAVIGATION_TEMPLATES["stress_routing"],
                "confidence": 0.85,
                "method": "context_routing"
            }
        elif "anxiety" in context:
            return {
                "response": NAVIGATION_TEMPLATES["anxiety_routing"],
                "confidence": 0.85,
                "method": "context_routing"
            }
        elif "depression" in context:
            return {
                "response": NAVIGATION_TEMPLATES["depression_routing"],
                "confidence": 0.85,
                "method": "context_routing"
            }
        elif "crisis" in context:
            return {
                "response": NAVIGATION_TEMPLATES["crisis_routing"],
                "confidence": 0.95,
                "method": "context_routing"
            }
    
    # Use model if available, otherwise fallback
    if generator:
        try:
            # Format conversation for the model
            prompt = f"User: {message}\nAssistant:"
            
            result = generator(
                prompt,
                max_length=len(prompt.split()) + 30,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )
            
            response = result[0]['generated_text']
            # Extract only the assistant's response
            assistant_response = response.split("Assistant:")[-1].strip()
            
            return {
                "response": assistant_response,
                "confidence": 0.7,
                "method": "model_generation"
            }
            
        except Exception as e:
            print(f"Model generation error: {e}")
    
    # Final fallback
    return {
        "response": "I understand you're looking for help. Let me connect you with the right specialist. Could you tell me a bit more about what you're experiencing?",
        "confidence": 0.6,
        "method": "fallback"
    }

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    load_model()

@app.get("/health")
async def health_check():
    model_status = "loaded" if generator else "template_only"
    return {
        "status": "healthy",
        "service": "local-llm",
        "model_status": model_status,
        "cuda_available": torch.cuda.is_available(),
        "timestamp": datetime.now()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Generate response for navigation and general chat
    """
    try:
        result = generate_navigation_response(
            request.message,
            request.context
        )
        
        return ChatResponse(
            response=result["response"],
            confidence=result["confidence"],
            model_used=result["method"],
            tokens_used=len(result["response"].split())
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation error: {str(e)}")

@app.get("/model/info")
async def model_info():
    """Get information about the loaded model"""
    return {
        "model_loaded": generator is not None,
        "model_name": "microsoft/DialoGPT-medium" if generator else "Template-based",
        "cuda_available": torch.cuda.is_available(),
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)