"""
Database for crowd-sourced player tagging
SQLite database to store user tags and consensus
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib

class TaggingDatabase:
    def __init__(self, db_path: str = None):
        """Initialize tagging database
        
        Args:
            db_path: Path to database file. If None, uses Streamlit Cloud persistent storage
                    or local 'data/tagging.db' as fallback
        """
        if db_path is None:
            # Try Streamlit Cloud persistent storage first
            import os
            if os.path.exists("/mount/src"):
                # Streamlit Cloud - use persistent storage
                db_path = "/mount/src/data/tagging.db"
            else:
                # Local development
                db_path = "data/tagging.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # User tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                frame_num INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                player_name TEXT NOT NULL,
                user_id TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                session_id TEXT,
                device_info TEXT,
                UNIQUE(video_id, frame_num, track_id, user_id)
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_video_frame_track 
            ON user_tags(video_id, frame_num, track_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user 
            ON user_tags(user_id)
        ''')
        
        # Consensus tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consensus_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                frame_num INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                player_name TEXT NOT NULL,
                confidence_score REAL DEFAULT 0.0,
                vote_count INTEGER DEFAULT 0,
                agreement_rate REAL DEFAULT 0.0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                alternatives TEXT,
                UNIQUE(video_id, frame_num, track_id)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_consensus_video_frame 
            ON consensus_tags(video_id, frame_num)
        ''')
        
        # User reputation table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_reputation (
                user_id TEXT PRIMARY KEY,
                total_tags INTEGER DEFAULT 0,
                agreed_tags INTEGER DEFAULT 0,
                disputed_tags INTEGER DEFAULT 0,
                reputation_score REAL DEFAULT 0.5,
                expertise_level TEXT DEFAULT 'beginner',
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tag conflicts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tag_conflicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                frame_num INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                conflicting_tags TEXT,
                resolution TEXT DEFAULT 'pending',
                resolved_by TEXT,
                resolved_at DATETIME,
                UNIQUE(video_id, frame_num, track_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_tag(self, video_id: str, frame_num: int, track_id: int, 
                player_name: str, user_id: str, confidence: float = 1.0,
                ip_address: str = None, session_id: str = None) -> int:
        """Add a user tag"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO user_tags 
                (video_id, frame_num, track_id, player_name, user_id, confidence, 
                 ip_address, session_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (video_id, frame_num, track_id, player_name, user_id, confidence,
                  ip_address, session_id, datetime.now()))
            
            tag_id = cursor.lastrowid
            conn.commit()
            
            # Update user reputation
            self._update_user_stats(user_id)
            
            return tag_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_tags(self, video_id: str, frame_num: int, track_id: Optional[int] = None) -> List[Dict]:
        """Get all tags for a specific player in a frame, or all tags in frame if track_id is None"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if track_id is not None:
            cursor.execute('''
                SELECT * FROM user_tags
                WHERE video_id = ? AND frame_num = ? AND track_id = ?
                ORDER BY timestamp DESC
            ''', (video_id, frame_num, track_id))
        else:
            cursor.execute('''
                SELECT * FROM user_tags
                WHERE video_id = ? AND frame_num = ?
                ORDER BY track_id, timestamp DESC
            ''', (video_id, frame_num))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_consensus(self, video_id: str, frame_num: int, track_id: int) -> Optional[Dict]:
        """Get consensus tag for a player"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM consensus_tags
            WHERE video_id = ? AND frame_num = ? AND track_id = ?
        ''', (video_id, frame_num, track_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            if result.get('alternatives'):
                result['alternatives'] = json.loads(result['alternatives'])
            return result
        return None
    
    def get_frame_consensus(self, video_id: str, frame_num: int) -> List[Dict]:
        """Get all consensus tags for a frame"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM consensus_tags
            WHERE video_id = ? AND frame_num = ?
            ORDER BY track_id
        ''', (video_id, frame_num))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = dict(row)
            if result.get('alternatives'):
                result['alternatives'] = json.loads(result['alternatives'])
            results.append(result)
        
        return results
    
    def update_consensus(self, video_id: str, frame_num: int, track_id: int,
                        consensus_data: Dict):
        """Update consensus tag"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        alternatives_json = json.dumps(consensus_data.get('alternatives', []))
        
        cursor.execute('''
            INSERT OR REPLACE INTO consensus_tags
            (video_id, frame_num, track_id, player_name, confidence_score,
             vote_count, agreement_rate, status, alternatives, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (video_id, frame_num, track_id, consensus_data['player_name'],
              consensus_data['confidence_score'], consensus_data['vote_count'],
              consensus_data['agreement_rate'], consensus_data.get('status', 'pending'),
              alternatives_json, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def _update_user_stats(self, user_id: str):
        """Update user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get user's total tags
        cursor.execute('SELECT COUNT(*) FROM user_tags WHERE user_id = ?', (user_id,))
        total_tags = cursor.fetchone()[0]
        
        # Calculate agreed tags (tags that match consensus)
        cursor.execute('''
            SELECT COUNT(*) FROM user_tags ut
            JOIN consensus_tags ct ON 
                ut.video_id = ct.video_id AND
                ut.frame_num = ct.frame_num AND
                ut.track_id = ct.track_id AND
                ut.player_name = ct.player_name
            WHERE ut.user_id = ?
        ''', (user_id,))
        agreed_tags = cursor.fetchone()[0]
        
        # Calculate reputation score
        reputation_score = (agreed_tags / total_tags) if total_tags > 0 else 0.5
        
        # Determine expertise level
        if total_tags < 10:
            expertise = 'beginner'
        elif total_tags < 50:
            expertise = 'intermediate'
        else:
            expertise = 'expert'
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_reputation
            (user_id, total_tags, agreed_tags, reputation_score, expertise_level, last_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, total_tags, agreed_tags, reputation_score, expertise, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_user_reputation(self, user_id: str) -> Optional[Dict]:
        """Get user reputation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_reputation WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_user_tags(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get user's recent tags"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_tags
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_tagging_stats(self, video_id: str = None) -> Dict:
        """Get tagging statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if video_id:
                cursor.execute('SELECT COUNT(*) FROM user_tags WHERE video_id = ?', (video_id,))
                total_tags = cursor.fetchone()[0] if cursor.fetchone() else 0
                
                cursor.execute('SELECT COUNT(*) FROM consensus_tags WHERE video_id = ?', (video_id,))
                consensus_count = cursor.fetchone()[0] if cursor.fetchone() else 0
                
                cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_tags WHERE video_id = ?', (video_id,))
                unique_users = cursor.fetchone()[0] if cursor.fetchone() else 0
            else:
                cursor.execute('SELECT COUNT(*) FROM user_tags')
                result = cursor.fetchone()
                total_tags = result[0] if result else 0
                
                cursor.execute('SELECT COUNT(*) FROM consensus_tags')
                result = cursor.fetchone()
                consensus_count = result[0] if result else 0
                
                cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_tags')
                result = cursor.fetchone()
                unique_users = result[0] if result else 0
        except Exception as e:
            # Return defaults on error
            total_tags = 0
            consensus_count = 0
            unique_users = 0
        finally:
            conn.close()
        
        return {
            'total_tags': total_tags,
            'consensus_count': consensus_count,
            'unique_users': unique_users
        }

