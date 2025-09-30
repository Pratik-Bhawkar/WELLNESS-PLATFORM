"""
Model Context Protocol (MCP) for Mental Wellness Platform
Provides dynamic context management and adaptive prompting for Phi-3 model
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


class ContextType(Enum):
    """Types of context that can be provided to the model"""
    CRISIS = "crisis"
    ANXIETY = "anxiety"
    DEPRESSION = "depression"
    STRESS = "stress"
    GENERAL_WELLNESS = "general_wellness"
    MOTIVATION = "motivation"
    SLEEP = "sleep"
    RELATIONSHIPS = "relationships"
    WORK_LIFE = "work_life"
    THERAPY = "therapy"


class UserState(Enum):
    """Current emotional/mental state of the user"""
    CALM = "calm"
    ANXIOUS = "anxious"
    DEPRESSED = "depressed"
    STRESSED = "stressed"
    ANGRY = "angry"
    CONFUSED = "confused"
    HOPEFUL = "hopeful"
    OVERWHELMED = "overwhelmed"


@dataclass
class ConversationContext:
    """Holds context information for a conversation"""
    user_id: int
    session_id: str
    context_type: ContextType
    user_state: UserState
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    crisis_indicators: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class MCPContextManager:
    """Model Context Protocol Manager for dynamic prompt generation"""
    
    def __init__(self):
        self.context_templates = self._load_context_templates()
        self.crisis_keywords = [
            "suicide", "kill myself", "end it all", "not worth living",
            "hurt myself", "self harm", "can't go on", "hopeless",
            "want to die", "ending everything"
        ]
        # Conversation memory storage - in production, use Redis or database
        self.conversation_memory = {}  # user_id -> ConversationContext
        
    def _load_context_templates(self) -> Dict[str, str]:
        """Load context-specific system prompts"""
        return {
            ContextType.CRISIS.value: """You are an emergency mental health AI assistant. This is a CRISIS situation.

CRITICAL PRIORITIES:
1. Express immediate care and concern
2. Encourage the user to seek professional help immediately
3. Provide crisis hotline numbers
4. Stay with the user and keep them talking
5. Do NOT minimize their feelings
6. Validate their pain while promoting safety

Crisis Resources:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Emergency Services: 911

Your response should be compassionate, urgent, and focused on immediate safety.""",

            ContextType.ANXIETY.value: """You are a specialized anxiety support AI assistant powered by Phi-3.

Your expertise includes:
1. Understanding anxiety triggers and symptoms
2. Teaching grounding techniques (5-4-3-2-1 method, deep breathing)
3. Cognitive behavioral therapy principles
4. Progressive muscle relaxation
5. Mindfulness and present-moment awareness

Approach:
- Validate their anxiety as real and understandable
- Offer practical, evidence-based coping strategies
- Encourage gradual exposure when appropriate
- Recognize when professional help is needed""",

            ContextType.DEPRESSION.value: """You are a depression-aware mental wellness AI assistant.

Your understanding includes:
1. Depression symptoms and their impact on daily life
2. Behavioral activation techniques
3. Cognitive restructuring for negative thought patterns
4. Self-care and routine building
5. Social connection importance

Response Style:
- Acknowledge the weight of their feelings
- Offer gentle, manageable suggestions
- Focus on small, achievable steps
- Emphasize hope and recovery possibility
- Monitor for suicidal ideation""",

            ContextType.STRESS.value: """You are a stress management AI specialist.

Your toolkit includes:
1. Stress identification and source analysis
2. Time management and prioritization strategies
3. Relaxation techniques and stress reduction
4. Work-life balance principles
5. Physical wellness connection to mental health

Focus Areas:
- Help identify stress sources
- Provide practical stress reduction techniques
- Suggest lifestyle modifications
- Encourage healthy coping mechanisms""",

            ContextType.GENERAL_WELLNESS.value: """You are a comprehensive mental wellness AI assistant powered by Phi-3.

Your role encompasses:
1. General mental health education and support
2. Wellness strategy development
3. Healthy habit formation
4. Emotional intelligence building
5. Preventive mental health practices

Approach:
- Maintain a warm, supportive tone
- Provide evidence-based information
- Encourage self-reflection and growth
- Promote overall well-being
- Connect mental and physical health""",

            ContextType.MOTIVATION.value: """You are a motivational mental wellness AI coach.

Your specialties:
1. Goal setting and achievement strategies
2. Overcoming procrastination and self-doubt
3. Building self-efficacy and confidence
4. Creating sustainable motivation systems
5. Celebrating progress and small wins

Style:
- Be encouraging without being dismissive
- Help break down overwhelming goals
- Acknowledge setbacks as normal
- Focus on personal growth and progress""",

            ContextType.SLEEP.value: """You are a sleep and mental health specialist AI.

Your knowledge covers:
1. Sleep hygiene and healthy sleep habits
2. Connection between sleep and mental health
3. Managing sleep anxiety and racing thoughts
4. Circadian rhythm optimization
5. Sleep disorders and when to seek help

Guidance Focus:
- Provide practical sleep improvement tips
- Address sleep-related anxiety
- Explain sleep's role in mental wellness
- Suggest relaxation techniques for bedtime""",

            ContextType.RELATIONSHIPS.value: """You are a relationship and social wellness AI counselor.

Your expertise includes:
1. Communication skills and conflict resolution
2. Boundary setting and healthy relationships
3. Social anxiety and connection building
4. Family dynamics and relationship patterns
5. Self-worth in relationships

Support Style:
- Help users understand relationship dynamics
- Provide communication strategies
- Encourage healthy boundaries
- Support social skill development""",

            ContextType.WORK_LIFE.value: """You are a work-life balance and career wellness AI advisor.

Your focus areas:
1. Work-related stress and burnout prevention
2. Career transitions and professional anxiety
3. Workplace relationships and communication
4. Work-life balance strategies
5. Professional growth and mental health

Approach:
- Address work-specific mental health challenges
- Provide practical workplace coping strategies
- Help separate work stress from personal life
- Encourage professional development""",

            ContextType.THERAPY.value: """You are a therapy-informed mental wellness AI assistant.

Your understanding includes:
1. Basic therapeutic principles and techniques
2. When and how to seek professional therapy
3. Different therapy types and their benefits
4. Preparing for therapy sessions
5. Complementing professional treatment

Important Notes:
- You are NOT a replacement for professional therapy
- Always encourage professional help when appropriate
- Provide psychoeducation and support
- Help users maximize their therapy experience"""
        }
    
    def detect_context_type(self, message: str, history: List[Dict[str, str]]) -> ContextType:
        """Simplified context detection focusing on current message"""
        message_lower = message.lower()
        
        # Crisis detection - highest priority
        if any(keyword in message_lower for keyword in self.crisis_keywords):
            return ContextType.CRISIS
        
        # Simple keyword matching for main contexts
        if any(word in message_lower for word in ["anxious", "anxiety", "worry", "panic", "nervous"]):
            return ContextType.ANXIETY
        
        if any(word in message_lower for word in ["depressed", "depression", "sad", "hopeless", "down"]):
            return ContextType.DEPRESSION
        
        if any(word in message_lower for word in ["stressed", "stress", "pressure", "overwhelmed"]):
            return ContextType.STRESS
        
        # Default to general wellness
        return ContextType.GENERAL_WELLNESS
    
    def detect_user_state(self, message: str, history: List[Dict[str, str]]) -> UserState:
        """Simplified user state detection"""
        message_lower = message.lower()
        
        # Crisis state
        if any(keyword in message_lower for keyword in self.crisis_keywords):
            return UserState.OVERWHELMED
        
        # Basic emotional state detection
        if any(word in message_lower for word in ["anxious", "nervous", "worry", "panic"]):
            return UserState.ANXIOUS
        
        if any(word in message_lower for word in ["sad", "depressed", "hopeless", "down"]):
            return UserState.DEPRESSED
        
        if any(word in message_lower for word in ["stressed", "pressure", "overwhelmed"]):
            return UserState.STRESSED
        
        if any(word in message_lower for word in ["angry", "mad", "frustrated"]):
            return UserState.ANGRY
        
        if any(word in message_lower for word in ["better", "good", "positive", "hopeful", "grateful"]):
            return UserState.HOPEFUL
        
        if any(word in message_lower for word in ["confused", "don't know", "uncertain"]):
            return UserState.CONFUSED
        
        # Default to calm
        return UserState.CALM
    
    def generate_dynamic_prompt(self, context: ConversationContext, current_message: str) -> str:
        """Generate very simple prompt"""
        return "You are a friendly mental wellness companion. Respond naturally and helpfully."
    
    def _extract_recent_topics(self, history: List[Dict[str, str]], limit: int = 3) -> List[str]:
        """Extract key topics from recent conversation history"""
        topics = []
        for entry in history[-limit:]:
            if entry.get('role') == 'user':
                message = entry.get('content', '').lower()
                # Simple topic extraction - could be enhanced with NLP
                if 'anxiety' in message or 'anxious' in message:
                    topics.append('anxiety')
                elif 'depression' in message or 'depressed' in message:
                    topics.append('depression')
                elif 'stress' in message or 'stressed' in message:
                    topics.append('stress')
                elif 'sleep' in message:
                    topics.append('sleep issues')
                elif 'work' in message or 'job' in message:
                    topics.append('work concerns')
                elif 'relationship' in message:
                    topics.append('relationships')
        
        return list(set(topics))  # Remove duplicates
    
    def _update_user_preferences(self, context: ConversationContext, message: str, history: List[Dict[str, str]]):
        """Extract and update user preferences from conversation"""
        message_lower = message.lower()
        
        # Detect communication preferences
        if any(word in message_lower for word in ["brief", "short", "quick", "concise"]):
            context.user_preferences["communication_style"] = "brief"
        elif any(word in message_lower for word in ["detailed", "explain", "elaborate", "more info"]):
            context.user_preferences["communication_style"] = "detailed"
        
        # Detect coping strategy preferences
        if any(word in message_lower for word in ["breathing", "meditation", "mindfulness"]):
            context.user_preferences["preferred_techniques"] = context.user_preferences.get("preferred_techniques", []) + ["mindfulness"]
        
        if any(word in message_lower for word in ["exercise", "walk", "physical", "activity"]):
            context.user_preferences["preferred_techniques"] = context.user_preferences.get("preferred_techniques", []) + ["physical_activity"]
        
        # Track recurring topics
        context.user_preferences["conversation_count"] = context.user_preferences.get("conversation_count", 0) + 1
        context.user_preferences["last_context"] = context.context_type.value
    
    def create_context(self, user_id: int, message: str, history: List[Dict[str, str]] = None) -> ConversationContext:
        """Create or retrieve conversation context with persistent memory"""
        if history is None:
            history = []
        
        # Check if we have existing context for this user
        existing_context = self.conversation_memory.get(user_id)
        
        if existing_context:
            # Update existing context with new message
            existing_context.conversation_history = history
            existing_context.context_type = self.detect_context_type(message, history)
            existing_context.user_state = self.detect_user_state(message, history)
            existing_context.timestamp = datetime.now()
            
            # Extract user preferences from conversation
            self._update_user_preferences(existing_context, message, history)
            
            print(f"🔄 Updated existing context for user {user_id} | History length: {len(history)}")
            return existing_context
        else:
            # Create new context
            context_type = self.detect_context_type(message, history)
            user_state = self.detect_user_state(message, history)
            
            # Generate session ID
            session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            new_context = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                context_type=context_type,
                user_state=user_state,
                conversation_history=history,
                timestamp=datetime.now()
            )
            
            # Store in memory
            self.conversation_memory[user_id] = new_context
            
            print(f"🆕 Created new context for user {user_id} | Context: {context_type.value} | State: {user_state.value}")
            return new_context
    
    def update_context(self, context: ConversationContext, new_message: str, response: str) -> ConversationContext:
        """Update context with new conversation turn"""
        # Add new exchange to history
        context.conversation_history.extend([
            {"role": "user", "content": new_message},
            {"role": "assistant", "content": response}
        ])
        
        # Re-evaluate context type and user state
        context.context_type = self.detect_context_type(new_message, context.conversation_history)
        context.user_state = self.detect_user_state(new_message, context.conversation_history)
        context.timestamp = datetime.now()
        
        return context


# Global MCP instance
mcp_manager = MCPContextManager()