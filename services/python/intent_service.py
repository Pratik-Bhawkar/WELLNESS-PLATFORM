"""
Intent Classification Service
Routes user messages to appropriate therapy specialists
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Intent Classification Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    message: str
    user_id: int
    session_history: List[str] = []

class IntentResponse(BaseModel):
    intent: str
    confidence: float
    suggested_service: str
    reasoning: str

# Intent classification rules (simple rule-based for now)
INTENT_PATTERNS = {
    "stress": {
        "keywords": ["stress", "overwhelmed", "pressure", "tension", "burden", "exhausted"],
        "patterns": [r"feel.*stress", r"so much pressure", r"can't handle", r"overwhelmed"],
        "service": "stress-management"
    },
    "anxiety": {
        "keywords": ["anxious", "worry", "nervous", "panic", "fear", "scared"],
        "patterns": [r"feel.*anxious", r"worry.*about", r"panic attack", r"so scared"],
        "service": "anxiety-support"
    },
    "depression": {
        "keywords": ["sad", "depressed", "hopeless", "empty", "worthless", "lonely"],
        "patterns": [r"feel.*sad", r"so depressed", r"no point", r"feel empty"],
        "service": "depression-support"
    },
    "crisis": {
        "keywords": ["suicide", "kill myself", "end it all", "hurt myself", "no hope"],
        "patterns": [r"want.*die", r"end.*life", r"hurt.*myself", r"no.*hope"],
        "service": "crisis-intervention",
        "priority": "urgent"
    },
    "navigation": {
        "keywords": ["help", "start", "begin", "how", "what", "schedule", "appointment"],
        "patterns": [r"how.*work", r"get started", r"need help", r"what.*do"],
        "service": "navigation-assistant"
    }
}

def classify_intent(message: str, history: List[str] = None) -> Dict:
    """
    Classify user intent based on message content
    """
    message_lower = message.lower()
    scores = {}
    
    for intent, config in INTENT_PATTERNS.items():
        score = 0
        reasoning_parts = []
        
        # Check keywords
        keyword_matches = sum(1 for keyword in config["keywords"] if keyword in message_lower)
        if keyword_matches > 0:
            score += keyword_matches * 0.3
            reasoning_parts.append(f"Found {keyword_matches} relevant keywords")
        
        # Check patterns
        pattern_matches = sum(1 for pattern in config["patterns"] if re.search(pattern, message_lower))
        if pattern_matches > 0:
            score += pattern_matches * 0.5
            reasoning_parts.append(f"Matched {pattern_matches} patterns")
        
        # Context from history
        if history:
            context_score = 0
            for prev_message in history[-3:]:  # Last 3 messages
                prev_lower = prev_message.lower()
                context_matches = sum(1 for keyword in config["keywords"] if keyword in prev_lower)
                context_score += context_matches * 0.1
            score += context_score
            if context_score > 0:
                reasoning_parts.append(f"Context support: {context_score:.1f}")
        
        scores[intent] = {
            "score": score,
            "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "No specific indicators"
        }
    
    # Find best match
    best_intent = max(scores.keys(), key=lambda x: scores[x]["score"])
    best_score = scores[best_intent]["score"]
    
    # Default to navigation if no strong match
    if best_score < 0.3:
        best_intent = "navigation"
        best_score = 0.5
        scores[best_intent]["reasoning"] = "Default routing - no specific intent detected"
    
    return {
        "intent": best_intent,
        "confidence": min(best_score, 1.0),
        "service": INTENT_PATTERNS[best_intent]["service"],
        "reasoning": scores[best_intent]["reasoning"],
        "all_scores": {k: v["score"] for k, v in scores.items()}
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "intent-classification", "timestamp": datetime.now()}

@app.post("/classify", response_model=IntentResponse)
async def classify_message(request: MessageRequest):
    """
    Classify user message intent
    """
    try:
        result = classify_intent(request.message, request.session_history)
        
        return IntentResponse(
            intent=result["intent"],
            confidence=result["confidence"],
            suggested_service=result["service"],
            reasoning=result["reasoning"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

@app.get("/intents")
async def get_available_intents():
    """
    Get list of available intents and their services
    """
    return {
        intent: {
            "service": config["service"],
            "keywords": config["keywords"][:5],  # First 5 keywords
            "priority": config.get("priority", "normal")
        }
        for intent, config in INTENT_PATTERNS.items()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)