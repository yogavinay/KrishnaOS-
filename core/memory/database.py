"""
MAHABHARATA SYSTEM - Database Models & Connection
PostgreSQL database for conversations, sessions, user profiles, and user facts.
"""

import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

Base = declarative_base()


class Conversation(Base):
    """Stores every conversation exchange."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, nullable=True)
    user_input = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    agent_used = Column(String(50), nullable=False, default="krishna")
    intent = Column(String(100), nullable=True)
    sentiment = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    metadata_ = Column("metadata", JSON, nullable=True)


class Session(Base):
    """Tracks user sessions."""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)
    total_interactions = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class UserProfile(Base):
    """Persistent user profile with preferences and habits."""
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), default="Yogavinay")
    preferences = Column(JSON, default=dict)
    habits = Column(JSON, default=dict)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    total_sessions = Column(Integer, default=0)
    mood_history = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class UserFact(Base):
    """Structured long-term knowledge extracted from conversations."""
    __tablename__ = "user_facts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fact_type = Column(String(50), nullable=False)  # preference, project, schedule, person, interest, skill
    fact_key = Column(String(200), nullable=False)   # e.g., "favorite_language", "current_project"
    fact_value = Column(Text, nullable=False)         # e.g., "Python", "Mahabharata System"
    confidence = Column(Float, default=0.8)           # 0.0 - 1.0
    source_conversation_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Database:
    """Database connection manager."""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialized = False

    def initialize(self):
        """Initialize database connection and create tables."""
        try:
            self.engine = create_engine(settings.database_url, echo=settings.debug)
            self.SessionLocal = sessionmaker(bind=self.engine)
            Base.metadata.create_all(self.engine)
            self._initialized = True
            print("[DATABASE] ✅ PostgreSQL connected and tables created.")
        except Exception as e:
            print(f"[DATABASE] ⚠️ PostgreSQL connection failed: {e}")
            print("[DATABASE] 📝 Falling back to SQLite...")
            self.engine = create_engine("sqlite:///mahabharata.db", echo=settings.debug)
            self.SessionLocal = sessionmaker(bind=self.engine)
            Base.metadata.create_all(self.engine)
            self._initialized = True
            print("[DATABASE] ✅ SQLite fallback connected.")

    def get_session(self):
        """Get a new database session."""
        if not self._initialized:
            self.initialize()
        return self.SessionLocal()

    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()


# Singleton
db = Database()
