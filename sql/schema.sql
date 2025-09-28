-- Mental Wellness Platform Database Schema

-- Users table
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    preferred_language VARCHAR(10) DEFAULT 'en',
    total_sessions INT DEFAULT 0
);

-- Conversations table
CREATE TABLE conversations (
    conversation_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_type ENUM('navigation', 'stress', 'anxiety', 'depression', 'crisis') NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    message_count INT DEFAULT 0,
    satisfaction_rating INT NULL CHECK (satisfaction_rating BETWEEN 1 AND 5),
    session_notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Messages table
CREATE TABLE messages (
    message_id INT PRIMARY KEY AUTO_INCREMENT,
    conversation_id INT NOT NULL,
    sender ENUM('user', 'assistant') NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_type ENUM('text', 'voice', 'system') DEFAULT 'text',
    emotion_score DECIMAL(3,2) NULL,
    confidence_score DECIMAL(3,2) NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);

-- Progress tracking table
CREATE TABLE mood_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    mood_score INT NOT NULL CHECK (mood_score BETWEEN 1 AND 10),
    stress_level INT NOT NULL CHECK (stress_level BETWEEN 1 AND 10),
    anxiety_level INT NOT NULL CHECK (anxiety_level BETWEEN 1 AND 10),
    notes TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Session analytics table
CREATE TABLE session_analytics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_date DATE NOT NULL,
    session_duration_minutes INT NOT NULL,
    session_type VARCHAR(50) NOT NULL,
    improvement_score DECIMAL(3,2),
    engagement_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_session_type ON conversations(session_type);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_mood_history_user_id ON mood_history(user_id);
CREATE INDEX idx_mood_history_date ON mood_history(recorded_at);
CREATE INDEX idx_session_analytics_user_date ON session_analytics(user_id, session_date);