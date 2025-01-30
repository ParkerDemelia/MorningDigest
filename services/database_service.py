import sqlite3
from datetime import datetime
import json

class DatabaseService:
    def __init__(self, db_path='data/morning_digest.db'):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        """Initialize the database with necessary tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    email_from TEXT,
                    query TEXT,
                    response TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_digests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE,
                    health_data TEXT,
                    calendar_events TEXT,
                    weather_info TEXT,
                    news_updates TEXT,
                    assignments TEXT
                )
            ''')
            
            conn.commit()

    def store_digest(self, health_data, calendar_events, weather_info, news_updates, assignments):
        """Store the daily digest information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            today = datetime.now().date()
            
            cursor.execute('''
                INSERT OR REPLACE INTO daily_digests 
                (date, health_data, calendar_events, weather_info, news_updates, assignments)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                today.isoformat(),
                json.dumps(health_data),
                json.dumps(calendar_events),
                json.dumps(weather_info),
                json.dumps(news_updates),
                json.dumps(assignments)
            ))

    def store_query(self, email_from, query, response):
        """Store a user query and its response."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_queries (email_from, query, response)
                VALUES (?, ?, ?)
            ''', (email_from, query, response))

    def get_recent_digests(self, days=7):
        """Retrieve recent daily digests."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM daily_digests
                ORDER BY date DESC
                LIMIT ?
            ''', (days,))
            return cursor.fetchall()

    def get_user_history(self, email):
        """Retrieve query history for a specific user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, query, response 
                FROM user_queries
                WHERE email_from = ?
                ORDER BY timestamp DESC
            ''', (email,))
            return cursor.fetchall() 