"""
Unified Mental Wellness API Gateway
Combines LLM, Intent Classification, and Analytics into a single FastAPI service
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
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
from faster_whisper import WhisperModel
import tempfile
# librosa removed - not needed
from dotenv import load_dotenv

# RAG System imports
from rag_system import MentalWellnessRAG

# Load environment variables from root .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

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

class VoiceTranscriptionRequest(BaseModel):
    user_id: int
    language: Optional[str] = "auto"  # auto-detect or specify language code

class VoiceTranscriptionResponse(BaseModel):
    transcription: str
    language: str
    confidence: float
    emotional_tone: Optional[str] = None
    duration: float

# =============================================
# GLOBAL VARIABLES
# =============================================

# LLM Model variables
tokenizer = None
model = None
device = None

# Whisper Model variables
whisper_model = None

# RAG System variable
rag_system = None

# LangChain imports and setup
from langchain.llms.base import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import Any, List, Optional

# Import Model Context Protocol
import sys
import os
# Add current directory to Python path for importing mcp_context
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from mcp_context import mcp_manager, ConversationContext

# LangChain custom LLM wrapper for Phi-3
class Phi3LLM(LLM):
    """Custom LangChain LLM wrapper for Phi-3 model"""
    
    @property
    def _llm_type(self) -> str:
        return "phi3"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the Phi-3 model with MCP context awareness"""
        try:
            if model is None or tokenizer is None:
                return "I apologize, but the AI model is not currently available."
            
            # Extract MCP context from kwargs if available
            mcp_context = kwargs.get('mcp_context')
            user_message = kwargs.get('user_message', prompt)
            
            if mcp_context:
                # Use MCP-generated dynamic prompt
                system_prompt = mcp_manager.generate_dynamic_prompt(mcp_context, user_message)
            else:
                # Fallback to basic prompt if no MCP context
                system_prompt = "You are a compassionate mental wellness AI assistant. Provide helpful, empathetic responses."
            
            formatted_prompt = f"<|system|>\n{system_prompt}<|end|>\n<|user|>\n{prompt}<|end|>\n<|assistant|>\n"
            
            # Tokenize and generate
            inputs = tokenizer(formatted_prompt, return_tensors="pt", truncate=True, max_length=512)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=256,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    use_cache=False
                )
            
            # Decode response
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract assistant response
            if "<|assistant|>" in response:
                response = response.split("<|assistant|>")[-1].strip()
            
            return response
            
        except Exception as e:
            print(f"❌ Phi-3 LLM call error: {e}")
            return f"I'm experiencing technical difficulties. Please try again. ({str(e)})"

# Global LangChain components
phi3_llm = None
conversation_memory = None
conversation_chain = None

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

def get_db_path():
    """Get the database file path from environment variable"""
    # Get database path from environment variable
    db_path_env = os.getenv("DB_PATH", "data/wellness_platform.db")
    
    # If relative path, make it relative to project root
    if not os.path.isabs(db_path_env):
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        db_path = os.path.join(project_root, db_path_env)
    else:
        db_path = db_path_env
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path

def get_db_connection():
    """Get SQLite database connection"""
    db_path = get_db_path()
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
    
    # Get model configuration from environment variables
    model_name = os.getenv("MODEL_NAME", "microsoft/Phi-3-mini-4k-instruct")
    model_path_env = os.getenv("MODEL_PATH", "models/phi-3-mini-4k-instruct")
    
    # If relative path, make it relative to project root
    if not os.path.isabs(model_path_env):
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        model_path = os.path.join(project_root, model_path_env)
    else:
        model_path = model_path_env
    
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

def load_whisper_model():
    """Load Faster-Whisper model for voice processing"""
    global whisper_model
    
    try:
        # Get voice configuration from environment variables
        voice_model = os.getenv("VOICE_MODEL", "tiny")  # tiny for speed, base for accuracy
        voice_device = os.getenv("VOICE_DEVICE", "cuda")
        
        print(f"🎤 Loading Faster-Whisper model: {voice_model}")
        print(f"🔧 Voice device: {voice_device}")
        
        # Load the Whisper model with environment configuration
        whisper_model = WhisperModel(voice_model, device=voice_device, compute_type="float16")
        print("✅ Faster-Whisper model loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading Whisper model: {e}")
        whisper_model = None
        return False

def initialize_langchain():
    """Initialize LangChain components with Phi-3"""
    global phi3_llm, conversation_memory, conversation_chain
    
    try:
        print("🔗 Initializing LangChain components...")
        
        # Initialize custom Phi-3 LLM
        phi3_llm = Phi3LLM()
        
        # Create conversation memory
        conversation_memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=True,
            max_token_limit=1000
        )
        
        # Create conversation template
        template = """You are a compassionate mental wellness AI assistant powered by Phi-3. Your role is to:

1. Listen empathetically to users' concerns
2. Provide supportive and helpful responses
3. Offer practical coping strategies when appropriate
4. Recognize when professional help might be needed
5. Maintain a warm, non-judgmental tone

Previous conversation:
{history}

Current user message: {input}

Please respond with empathy and provide helpful guidance."""

        # Create prompt template
        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=template
        )
        
        # Create conversation chain
        conversation_chain = ConversationChain(
            llm=phi3_llm,
            prompt=prompt,
            memory=conversation_memory,
            verbose=False
        )
        
        print("✅ LangChain components initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing LangChain: {e}")
        return False

def initialize_rag_system():
    """Initialize RAG system with mental wellness documents"""
    global rag_system
    
    try:
        print("📚 Initializing RAG system...")
        
        # Get documents directory path
        documents_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'documents')
        
        # Initialize RAG system
        rag_system = MentalWellnessRAG(documents_dir)
        
        if rag_system.initialize():
            stats = rag_system.get_statistics()
            print(f"✅ RAG system initialized successfully!")
            print(f"📊 Loaded {stats['total_chunks']} chunks from {len(stats['documents_by_source'])} documents")
            return True
        else:
            print("❌ Failed to initialize RAG system")
            rag_system = None
            return False
            
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        rag_system = None
        return False

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

def process_audio_file(audio_file_path: str, language: str = "auto") -> Dict:
    """Process uploaded audio file with Faster-Whisper"""
    if whisper_model is None:
        raise HTTPException(status_code=503, detail="Voice processing unavailable - Whisper model not loaded")
    
    try:
        print(f"🎤 Transcribing audio file: {audio_file_path}")
        
        # Use Faster-Whisper to transcribe
        if language == "auto":
            segments, info = whisper_model.transcribe(audio_file_path)
        else:
            segments, info = whisper_model.transcribe(audio_file_path, language=language)
        
        # Combine all segments into full transcription
        transcription = " ".join(segment.text for segment in segments)
        
        # Skip emotion analysis for faster processing
        emotional_tone = "neutral"
        
        return {
            "transcription": transcription.strip(),
            "language": info.language,
            "confidence": round(info.language_probability, 2),
            "emotional_tone": emotional_tone,
            "duration": 0.0  # Will be calculated from audio file
        }
        
    except Exception as e:
        print(f"❌ Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")

# Emotion analysis removed for faster processing

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
    load_whisper_model()
    initialize_langchain()
    initialize_rag_system()
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
    """Chat with Phi-3-mini LLM - Enhanced with Model Context Protocol (MCP)"""
    global tokenizer, model, device, conversation_chain
    
    # Ensure model is loaded
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Phi-3-mini model not loaded. Server startup failed.")
    
    try:
        # Format conversation history - simple approach
        conversation_history = ""
        if request.conversation_history:
            for msg in request.conversation_history[-3:]:  # Last 3 messages only
                role = "User" if msg.get("role") == "user" else "Assistant"
                conversation_history += f"{role}: {msg.get('content', '')}\n"
        
        # Get RAG context if available
        rag_context = ""
        if rag_system:
            try:
                # Detect context type for better RAG retrieval
                context_type = None
                message_lower = request.message.lower()
                if any(word in message_lower for word in ["anxious", "anxiety", "worry", "panic"]):
                    context_type = "anxiety"
                elif any(word in message_lower for word in ["sad", "depressed", "depression", "hopeless"]):
                    context_type = "depression"
                elif any(word in message_lower for word in ["stress", "overwhelmed", "pressure"]):
                    context_type = "stress"
                elif any(word in message_lower for word in ["mindful", "meditation", "breathing"]):
                    context_type = "therapy"
                
                # Retrieve relevant context
                rag_context = rag_system.get_rag_response_context(request.message, context_type)
                if rag_context:
                    print(f"📚 RAG Context Retrieved: {len(rag_context)} characters")
                else:
                    print("📚 No relevant RAG context found")
                    
            except Exception as e:
                print(f"⚠️ RAG retrieval error: {e}")
                rag_context = ""
        
        # Create enhanced prompt with RAG context
        system_prompt = "You are a friendly mental wellness companion. Respond naturally and helpfully."
        
        if rag_context:
            system_prompt += f"\n\n{rag_context}\nUse this information to provide more helpful and accurate responses, but keep your response conversational and natural."
        
        if conversation_history:
            full_prompt = f"{system_prompt}\n\n{conversation_history}User: {request.message}\nAssistant:"
        else:
            full_prompt = f"{system_prompt}\n\nUser: {request.message}\nAssistant:"

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
        
        # Extract only the new response
        response = full_response[len(full_prompt):].strip()
        
        # Clean up response
        response = response.split("USER:")[0].split("User:")[0].strip()
        
        if not response or len(response) < 10:
            raise ValueError("Generated response too short or empty")
        
        # Log response with RAG status
        rag_status = "with RAG context" if rag_context else "without RAG context"
        print(f"✅ Response Generated ({rag_status}) | Length: {len(response)}")
        
        # Determine model name based on RAG usage
        model_name = "phi-3-mini-4k-instruct-rag" if rag_context else "phi-3-mini-4k-instruct"
        
        return ChatResponse(
            response=response,
            confidence=0.95,
            model_used=model_name,
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
# VOICE PROCESSING ENDPOINTS
# =============================================

@app.post("/api/voice/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    user_id: int = Form(1),
    language: str = Form("auto")
):
    """
    Transcribe uploaded audio file using OpenAI Whisper
    
    Supports multiple audio formats: wav, mp3, flac, m4a, ogg
    Language can be 'auto' for auto-detection or specific language codes (en, es, fr, etc.)
    """
    
    print(f"🎤 Voice transcription request: file={audio_file.filename}, user_id={user_id}, language={language}")
    
    if whisper_model is None:
        raise HTTPException(
            status_code=503, 
            detail="Voice processing service unavailable - Whisper model not loaded"
        )
    
    # Check file format
    allowed_formats = {'.wav', '.mp3', '.flac', '.m4a', '.ogg', '.webm'}
    file_extension = os.path.splitext(audio_file.filename)[1].lower()
    
    if file_extension not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format. Allowed: {', '.join(allowed_formats)}"
        )
    
    # Create temporary file to store uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        try:
            # Save uploaded file
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
            
            print(f"🎤 Processing audio file: {audio_file.filename} ({len(content)} bytes)")
            
            # Process audio with Whisper
            result = process_audio_file(temp_file_path, language)
            
            # Set estimated duration (faster than calculating)
            result["duration"] = len(content) / 16000.0  # Rough estimate
            
            # Skip database storage for voice transcriptions - not needed
            
            print(f"✅ Audio transcribed successfully: '{result['transcription'][:50]}...'")
            
            return VoiceTranscriptionResponse(**result)
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Voice transcription error: {e}")
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass

@app.post("/api/voice/chat")
async def voice_chat(
    audio_file: UploadFile = File(...),
    user_id: int = 1,
    language: str = "auto"
):
    """
    Complete voice-to-voice workflow: transcribe audio, process with LLM, return text response
    """
    
    # First transcribe the audio
    transcription_response = await transcribe_audio(audio_file, user_id, language)
    
    # Process transcription with chat API
    chat_request = ChatRequest(
        message=transcription_response.transcription,
        user_id=user_id,
        conversation_history=[],
        context=f"Voice message (emotional tone: {transcription_response.emotional_tone})"
    )
    
    # Get LLM response using the existing chat endpoint function
    try:
        chat_response = await chat_with_llm(chat_request)
        
        return {
            "transcription": transcription_response,
            "llm_response": chat_response,
            "processing_time": f"{transcription_response.duration + 2.0:.2f}s"  # Estimate
        }
    except Exception as e:
        print(f"❌ Voice chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice chat failed: {str(e)}")

# =============================================
# MAIN ENTRY POINT
# =============================================

if __name__ == "__main__":
    import uvicorn
    
    # Get server configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"🌐 Starting Mental Wellness Platform API")
    print(f"📡 Host: {host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📝 Log level: {log_level}")
    print(f"🔄 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Only use reload in development mode and when running as script
    if debug and __name__ == "__main__":
        uvicorn.run("unified_api:app", host=host, port=port, log_level=log_level, reload=True)
    else:
        uvicorn.run(app, host=host, port=port, log_level=log_level)