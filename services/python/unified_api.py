"""
Unified Mental Wellness API Gateway
Combines LLM, Intent Classification, and Analytics into a single FastAPI service
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from datetime import datetime, timedelta
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
import re
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================
# REQUEST/RESPONSE MODELS
# =============================================

class ChatRequest(BaseModel):
    message: str
    user_id: int
    conversation_history: List[Dict[str, str]] = []
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    confidence: float
    model_used: str
    tokens_used: Optional[int] = None

class IntentRequest(BaseModel):
    message: str
    user_id: int
    session_history: List[str] = []

class IntentResponse(BaseModel):
    intent: str
    confidence: float
    suggested_service: str
    reasoning: str

class MoodEntry(BaseModel):
    user_id: int
    mood_score: int  # 0-100 scale
    session_type: str
    feedback_text: Optional[str] = None

class AnalyticsResponse(BaseModel):
    user_id: int
    average_mood: float
    mood_trend: str
    total_sessions: int
    mood_data: List[dict]
    chart_url: Optional[str] = None

# =============================================
# GLOBAL VARIABLES
# =============================================

# LLM Model variables
tokenizer = None
model = None
device = None

# Intent classification patterns
INTENT_PATTERNS = {
    "stress": {
        "keywords": ["stress", "overwhelmed", "pressure", "tension", "burden", "exhausted"],
        "patterns": [r"feel.*stress", r"so much pressure", r"can't handle", r"overwhelmed"],
        "service": "stress-management",
        "confidence": 0.8
    },
    "anxiety": {
        "keywords": ["anxious", "worried", "panic", "nervous", "fear", "afraid"],
        "patterns": [r"feel.*anxious", r"panic.*attack", r"worried.*about", r"afraid.*of"],
        "service": "anxiety-support",
        "confidence": 0.8
    },
    "depression": {
        "keywords": ["sad", "depressed", "hopeless", "empty", "worthless", "lonely"],
        "patterns": [r"feel.*sad", r"feel.*empty", r"feel.*hopeless", r"don't.*care"],
        "service": "depression-support",
        "confidence": 0.8
    },
    "crisis": {
        "keywords": ["suicide", "kill myself", "end it", "hurt myself", "die"],
        "patterns": [r"want.*die", r"kill.*myself", r"end.*it.*all", r"hurt.*myself"],
        "service": "crisis-intervention",
        "confidence": 0.9
    },
    "navigation": {
        "keywords": ["help", "support", "where", "how", "what", "find"],
        "patterns": [r"how.*do", r"where.*can", r"what.*should", r"need.*help"],
        "service": "navigation-assistance",
        "confidence": 0.6
    }
}

# =============================================
# UTILITY FUNCTIONS
# =============================================

def get_db_connection():
    """Get SQLite database connection"""
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'wellness_platform.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initialize database tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create mood_history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mood_score INTEGER NOT NULL,
            session_type TEXT,
            feedback_text TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def load_phi3_model():
    """Load Phi-3-mini model with CUDA - NO FALLBACKS"""
    global tokenizer, model, device
    
    # Force CUDA usage - fail if not available
    if not torch.cuda.is_available():
        raise RuntimeError("❌ CUDA is required but not available! Install CUDA-enabled PyTorch.")
    
    device = torch.device("cuda")
    print(f"🚀 Using GPU: {torch.cuda.get_device_name(0)}")
    print(f"🔧 CUDA Version: {torch.version.cuda}")
    print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    model_name = "microsoft/Phi-3-mini-4k-instruct"
    model_path = os.path.join("..", "..", "models", "phi-3-mini-4k-instruct")
    
    try:
        # Load model from local path if exists, otherwise from HuggingFace
        if os.path.exists(model_path):
            print(f"📁 Loading Phi-3-mini from: {model_path}")
            tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        else:
            print(f"🌐 Loading Phi-3-mini from HuggingFace: {model_name}")
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            model_path = model_name
        
        # Load with 4-bit quantization for GPU
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        
        print("🔄 Loading model with 4-bit quantization...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=bnb_config,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        print("✅ Phi-3-mini loaded successfully on GPU!")
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR loading Phi-3 model: {e}")
        raise RuntimeError(f"Failed to load Phi-3 model: {e}")  # No fallbacks!

def classify_intent(message: str) -> Dict:
    """Classify user message intent"""
    message_lower = message.lower()
    best_intent = "navigation"
    best_confidence = 0.3
    best_service = "navigation-assistance"
    reasoning_parts = []
    
    for intent_name, config in INTENT_PATTERNS.items():
        score = 0
        matched_keywords = []
        matched_patterns = []
        
        # Check keywords
        for keyword in config["keywords"]:
            if keyword in message_lower:
                matched_keywords.append(keyword)
                score += 1
        
        # Check patterns
        for pattern in config["patterns"]:
            if re.search(pattern, message_lower):
                matched_patterns.append(pattern)
                score += 2
        
        if score > 0:
            confidence = min(config["confidence"], score * 0.2)
            if confidence > best_confidence:
                best_intent = intent_name
                best_confidence = confidence
                best_service = config["service"]
                reasoning_parts = [
                    f"Found {len(matched_keywords)} relevant keywords" if matched_keywords else "",
                    f"Matched {len(matched_patterns)} patterns" if matched_patterns else ""
                ]
    
    reasoning = "; ".join(filter(None, reasoning_parts)) or "Default classification"
    
    return {
        "intent": best_intent,
        "confidence": round(best_confidence, 2),
        "suggested_service": best_service,
        "reasoning": reasoning
    }

# =============================================
# LIFESPAN EVENT HANDLER
# =============================================

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup services"""
    print("🚀 Starting Mental Wellness Platform API...")
    initialize_database()
    load_phi3_model()
    print("✅ All services initialized successfully!")
    yield
    print("🔄 Shutting down Mental Wellness Platform API...")

# Update app initialization to use lifespan
app = FastAPI(
    title="Mental Wellness Platform API",
    description="Unified API for LLM, Intent Classification, and Analytics",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================
# HEALTH CHECK ENDPOINTS
# =============================================

@app.get("/health")
async def health_check():
    """Overall system health check"""
    try:
        # Check database
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except Exception:
        db_status = "error"
    
    return {
        "status": "healthy",
        "service": "unified-wellness-api",
        "components": {
            "database": db_status,
            "llm_model": "loaded" if model is not None else "template_only",
            "cuda_available": torch.cuda.is_available(),
            "matplotlib": "available"
        },
        "timestamp": datetime.now().isoformat()
    }

# =============================================
# LLM ENDPOINTS
# =============================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_llm(request: ChatRequest):
    """Chat with Phi-3-mini LLM - NO FALLBACKS"""
    global tokenizer, model, device
    
    # Ensure model is loaded
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Phi-3-mini model not loaded. Server startup failed.")
    
    try:
        # Create comprehensive mental wellness prompt
        conversation_history = ""
        if request.conversation_history:
            for msg in request.conversation_history[-5:]:  # Last 5 messages for context
                role = "User" if msg.get("role") == "user" else "Assistant"
                conversation_history += f"{role}: {msg.get('content', '')}\n"
        
        system_prompt = """You are Phi-3-mini, a compassionate AI mental wellness assistant. You provide empathetic, helpful responses for mental health support.

GUIDELINES:
- Be warm, understanding, and non-judgmental
- Provide practical mental health advice and coping strategies  
- Suggest professional help when appropriate for serious issues
- Keep responses concise (2-3 sentences) but caring
- Focus on emotional support and wellness techniques
- Use encouraging, hopeful language

CONVERSATION CONTEXT:
{history}

USER MESSAGE: {message}

RESPONSE:"""

        full_prompt = system_prompt.format(
            history=conversation_history if conversation_history else "This is the start of a new conversation.",
            message=request.message
        )

        # Tokenize input
        inputs = tokenizer(
            full_prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=1024,
            padding=True
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate response with optimized parameters
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs.get('attention_mask'),
                max_new_tokens=200,
                temperature=0.8,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=False  # Fix for DynamicCache compatibility
            )
        
        # Decode and clean response
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the new response (after "RESPONSE:")
        if "RESPONSE:" in full_response:
            response = full_response.split("RESPONSE:")[-1].strip()
        else:
            # Fallback: take text after the input prompt
            response = full_response[len(full_prompt):].strip()
        
        # Clean up response
        response = response.split("USER:")[0].split("User:")[0].strip()
        
        if not response or len(response) < 10:
            raise ValueError("Generated response too short or empty")
            
        return ChatResponse(
            response=response,
            confidence=0.95,
            model_used="phi-3-mini-4k-instruct",
            tokens_used=len(outputs[0])
        )
            
    except Exception as e:
        print(f"❌ Chat generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Phi-3-mini chat generation failed: {str(e)}")

# =============================================
# INTENT CLASSIFICATION ENDPOINTS
# =============================================

@app.post("/api/classify", response_model=IntentResponse)
async def classify_message_intent(request: IntentRequest):
    """Classify the intent of a user message"""
    try:
        result = classify_intent(request.message)
        return IntentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent classification failed: {str(e)}")

# =============================================
# ANALYTICS ENDPOINTS
# =============================================

@app.post("/api/mood/record")
async def record_mood(mood_entry: MoodEntry):
    """Record a mood entry"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO mood_history (user_id, mood_score, session_type, feedback_text, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            mood_entry.user_id,
            mood_entry.mood_score,
            mood_entry.session_type,
            mood_entry.feedback_text,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        mood_id = cursor.lastrowid
        conn.close()
        
        return {
            "success": True,
            "mood_id": mood_id,
            "message": "Mood recorded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record mood: {str(e)}")

@app.get("/api/analytics/{user_id}", response_model=AnalyticsResponse)
async def get_user_analytics(user_id: int, days: int = 30):
    """Get user analytics and mood trends"""
    try:
        conn = get_db_connection()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor = conn.execute("""
            SELECT mood_score, session_type, timestamp, feedback_text
            FROM mood_history 
            WHERE user_id = ? AND datetime(timestamp) >= datetime(?)
            ORDER BY timestamp ASC
        """, (user_id, cutoff_date.isoformat()))
        
        mood_data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not mood_data:
            return AnalyticsResponse(
                user_id=user_id,
                average_mood=50.0,
                mood_trend="no_data",
                total_sessions=0,
                mood_data=[],
                chart_url=None
            )
        
        # Calculate analytics
        scores = [entry['mood_score'] for entry in mood_data]
        average_mood = sum(scores) / len(scores)
        total_sessions = len(mood_data)
        
        # Determine trend
        if len(scores) > 1:
            recent_avg = sum(scores[-7:]) / min(7, len(scores))
            older_avg = sum(scores[:-7]) / max(1, len(scores) - 7) if len(scores) > 7 else average_mood
            
            if recent_avg > older_avg + 5:
                trend = "improving"
            elif recent_avg < older_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return AnalyticsResponse(
            user_id=user_id,
            average_mood=round(average_mood, 2),
            mood_trend=trend,
            total_sessions=total_sessions,
            mood_data=mood_data,
            chart_url=None  # Chart generation can be added later if needed
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")

# =============================================
# MAIN ENTRY POINT
# =============================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")