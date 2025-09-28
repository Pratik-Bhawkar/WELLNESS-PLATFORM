"""
Mental Wellness Platform - Database Setup Script
Creates SQLite database and initializes schema
"""

import sqlite3
import os
from pathlib import Path

def setup_database():
    """Set up SQLite database with schema"""
    try:
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Database path
        db_path = data_dir / "wellness_platform.db"
        
        print(f"Setting up database at: {db_path}")
        
        # Connect to database (creates if doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read and execute schema
        schema_path = Path("sql/schema_sqlite.sql")
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
            
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema (split by semicolon for multiple statements)
        for statement in schema_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        
        # Test database by querying sample data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conversation_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages")
        message_count = cursor.fetchone()[0]
        
        print(f"✅ Database setup successful!")
        print(f"   - Users: {user_count}")
        print(f"   - Conversations: {conversation_count}")
        print(f"   - Messages: {message_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_database_connection():
    """Test database connectivity"""
    try:
        db_path = Path("data/wellness_platform.db")
        if not db_path.exists():
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT username, email FROM users LIMIT 1")
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            print(f"✅ Database connection test passed")
            print(f"   Sample user: {result[0]} ({result[1]})")
            return True
        else:
            print("❌ Database connection test failed - no data")
            return False
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Mental Wellness Platform Database Setup ===")
    
    if setup_database():
        if test_database_connection():
            print("\n🎉 Database ready for Mental Wellness Platform!")
        else:
            print("\n⚠️ Database created but connection test failed")
    else:
        print("\n❌ Database setup failed")