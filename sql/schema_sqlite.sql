-- Mental Wellness Platform Database Schema - SQLite Version

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    preferred_language TEXT DEFAULT 'en',
    total_sessions INTEGER DEFAULT 0
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_type TEXT CHECK(session_type IN ('navigation', 'stress', 'anxiety', 'depression', 'crisis')) NOT NULL,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NULL,
    message_count INTEGER DEFAULT 0,
    satisfaction_rating INTEGER CHECK (satisfaction_rating BETWEEN 1 AND 5),
    session_notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    sender TEXT CHECK(sender IN ('user', 'assistant')) NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    message_type TEXT CHECK(message_type IN ('text', 'voice', 'system')) DEFAULT 'text',
    emotion_score REAL,
    confidence_score REAL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);

-- Progress tracking table
CREATE TABLE IF NOT EXISTS mood_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mood_score INTEGER CHECK (mood_score BETWEEN 1 AND 10) NOT NULL,
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10) NOT NULL,
    anxiety_level INTEGER CHECK (anxiety_level BETWEEN 1 AND 10) NOT NULL,
    notes TEXT,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Session analytics table
CREATE TABLE IF NOT EXISTS session_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_date DATE NOT NULL,
    session_duration_minutes INTEGER NOT NULL,
    session_type TEXT NOT NULL,
    improvement_score REAL,
    engagement_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session_type ON conversations(session_type);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_mood_history_user_id ON mood_history(user_id);
CREATE INDEX IF NOT EXISTS idx_mood_history_date ON mood_history(recorded_at);
CREATE INDEX IF NOT EXISTS idx_session_analytics_user_date ON session_analytics(user_id, session_date);

-- Insert sample data for testing
INSERT OR IGNORE INTO users (user_id, username, email, password_hash) VALUES 
(1, 'test_user', 'test@example.com', 'hashed_password_123');

INSERT OR IGNORE INTO conversations (conversation_id, user_id, session_type) VALUES 
(1, 1, 'navigation');

INSERT OR IGNORE INTO messages (conversation_id, sender, content) VALUES 
(1, 'user', 'Hello, I need help with stress management'),
(1, 'assistant', 'I understand you are looking for help with stress. Let me connect you with our stress management specialist.');

INSERT OR IGNORE INTO mood_history (user_id, mood_score, stress_level, anxiety_level, notes) VALUES 
(1, 6, 7, 5, 'Feeling better after morning meditation');

INSERT OR IGNORE INTO session_analytics (user_id, session_date, session_duration_minutes, session_type, improvement_score, engagement_score) VALUES 
(1, date('now'), 15, 'stress-management', 0.75, 0.85);