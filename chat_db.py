"""
Team Chat Database Manager
Handles all database operations for the team chat system
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

class ChatDatabase:
    def __init__(self, db_path='team_chat.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                channel TEXT NOT NULL DEFAULT 'general',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                pinned BOOLEAN DEFAULT 0,
                deleted BOOLEAN DEFAULT 0
            )
        ''')
        
        # Channels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Initialize default channels if they don't exist
        default_channels = [
            ('general', 'General team discussion'),
            ('game-day', 'Game day coordination and updates'),
            ('schedule', 'Schedule changes and announcements'),
            ('carpools', 'Carpool coordination'),
            ('equipment', 'Equipment sharing and questions')
        ]
        
        for channel_name, description in default_channels:
            cursor.execute('''
                INSERT OR IGNORE INTO channels (name, description)
                VALUES (?, ?)
            ''', (channel_name, description))
        
        conn.commit()
        conn.close()
    
    def post_message(self, username, message, channel='general'):
        """Post a new message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (username, message, channel)
            VALUES (?, ?, ?)
        ''', (username, message, channel))
        
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        
        return message_id
    
    def get_messages(self, channel='general', limit=50, include_deleted=False):
        """Get messages for a channel"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT id, username, message, channel, timestamp, pinned
            FROM messages
            WHERE channel = ? AND deleted = ?
            ORDER BY pinned DESC, timestamp DESC
            LIMIT ?
        '''
        
        deleted_flag = 1 if include_deleted else 0
        df = pd.read_sql_query(query, conn, params=(channel, deleted_flag, limit))
        conn.close()
        
        # Reverse to show oldest first (except pinned messages stay at top)
        pinned = df[df['pinned'] == 1]
        unpinned = df[df['pinned'] == 0].iloc[::-1]
        df = pd.concat([pinned, unpinned])
        
        return df
    
    def get_all_channels(self):
        """Get all available channels"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('SELECT * FROM channels ORDER BY name', conn)
        conn.close()
        return df
    
    def pin_message(self, message_id):
        """Pin a message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE messages
            SET pinned = 1
            WHERE id = ?
        ''', (message_id,))
        
        conn.commit()
        conn.close()
    
    def unpin_message(self, message_id):
        """Unpin a message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE messages
            SET pinned = 0
            WHERE id = ?
        ''', (message_id,))
        
        conn.commit()
        conn.close()
    
    def delete_message(self, message_id):
        """Soft delete a message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE messages
            SET deleted = 1
            WHERE id = ?
        ''', (message_id,))
        
        conn.commit()
        conn.close()
    
    def get_message_count(self, channel='general'):
        """Get total message count for a channel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM messages
            WHERE channel = ? AND deleted = 0
        ''', (channel,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_recent_activity(self, minutes=60):
        """Get recent activity across all channels"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT channel, COUNT(*) as count
            FROM messages
            WHERE timestamp >= datetime('now', '-' || ? || ' minutes')
            AND deleted = 0
            GROUP BY channel
            ORDER BY count DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(minutes,))
        conn.close()
        
        return df


if __name__ == '__main__':
    # Test the database
    db = ChatDatabase()
    print("Database initialized successfully!")
    print("\nChannels:")
    print(db.get_all_channels())
    
    # Post a test message
    db.post_message("System", "Welcome to DSX Team Chat! 🎉⚽", "general")
    print("\nTest message posted!")
    
    # Get messages
    print("\nMessages:")
    print(db.get_messages())

