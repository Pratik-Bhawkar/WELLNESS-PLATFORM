from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Analytics Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class MoodEntry(BaseModel):
    user_id: int
    mood_score: int  # 0-100 scale
    session_type: str
    feedback_text: Optional[str] = None

class AnalyticsRequest(BaseModel):
    user_id: int
    days: int = 30

class AnalyticsResponse(BaseModel):
    user_id: int
    average_mood: float
    mood_trend: str
    total_sessions: int
    mood_data: List[dict]
    chart_url: Optional[str] = None

# Database connection
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'wellness_platform.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {
            "status": "healthy",
            "service": "analytics",
            "database": "connected",
            "matplotlib": "available",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/mood/record")
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

@app.get("/analytics/{user_id}")
async def get_user_analytics(user_id: int, days: int = 30) -> AnalyticsResponse:
    """Get user analytics and mood trends"""
    try:
        conn = get_db_connection()
        
        # Get mood data for the specified period
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
            recent_avg = sum(scores[-7:]) / min(7, len(scores))  # Last 7 entries
            older_avg = sum(scores[:-7]) / max(1, len(scores) - 7) if len(scores) > 7 else average_mood
            
            if recent_avg > older_avg + 5:
                trend = "improving"
            elif recent_avg < older_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Generate chart
        chart_url = None
        try:
            chart_url = generate_mood_chart(mood_data, user_id)
        except Exception as e:
            print(f"Chart generation failed: {e}")
        
        return AnalyticsResponse(
            user_id=user_id,
            average_mood=round(average_mood, 2),
            mood_trend=trend,
            total_sessions=total_sessions,
            mood_data=mood_data,
            chart_url=chart_url
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")

def generate_mood_chart(mood_data: List[dict], user_id: int) -> str:
    """Generate a mood trend chart and return as base64 encoded image"""
    try:
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(mood_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(df['timestamp'], df['mood_score'], marker='o', linestyle='-', linewidth=2, markersize=6)
        plt.title(f'Mood Trend - User {user_id}', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Mood Score (0-100)', fontsize=12)
        plt.ylim(0, 100)
        plt.grid(True, alpha=0.3)
        
        # Add trend line
        if len(df) > 1:
            z = np.polyfit(range(len(df)), df['mood_score'], 1)
            p = np.poly1d(z)
            plt.plot(df['timestamp'], p(range(len(df))), "r--", alpha=0.8, linewidth=2, label='Trend')
            plt.legend()
        
        # Color code the mood ranges
        plt.axhspan(80, 100, alpha=0.1, color='green', label='Great')
        plt.axhspan(60, 80, alpha=0.1, color='yellow', label='Good')
        plt.axhspan(40, 60, alpha=0.1, color='orange', label='Okay')
        plt.axhspan(0, 40, alpha=0.1, color='red', label='Concerning')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{chart_base64}"
        
    except Exception as e:
        print(f"Chart generation error: {e}")
        return None

@app.get("/mood/summary")
async def get_mood_summary():
    """Get overall mood statistics across all users"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total_entries,
                AVG(mood_score) as average_mood,
                MIN(mood_score) as min_mood,
                MAX(mood_score) as max_mood,
                COUNT(DISTINCT user_id) as active_users
            FROM mood_history 
            WHERE datetime(timestamp) >= datetime('now', '-30 days')
        """)
        
        summary = dict(cursor.fetchone())
        conn.close()
        
        return {
            "period": "30_days",
            "statistics": summary,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import numpy as np  # Import numpy here for chart generation
    uvicorn.run(app, host="0.0.0.0", port=8002)