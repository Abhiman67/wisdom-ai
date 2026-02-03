"""
SQLAlchemy models for Wisdom AI chat logging.
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())


class Query(Base):
    """Stores user queries/questions."""
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), default=generate_session_id, nullable=False, index=True)
    question = Column(Text, nullable=False)
    temperature = Column(Float, default=0.6)
    max_tokens = Column(Integer, default=300)
    rag_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    response = relationship("Response", back_populates="query", uselist=False, cascade="all, delete-orphan")
    retrievals = relationship("Retrieval", back_populates="query", cascade="all, delete-orphan")
    errors = relationship("ErrorLog", back_populates="query", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "question": self.question,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "rag_enabled": self.rag_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Response(Base):
    """Stores model responses/answers."""
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("queries.id", ondelete="CASCADE"), nullable=False, unique=True)
    answer = Column(Text, nullable=False)
    latency_ms = Column(Integer, nullable=True)  # Response time in milliseconds
    tokens_generated = Column(Integer, nullable=True)
    detected_mood = Column(String(50), nullable=True)
    verse_id = Column(String(20), nullable=True)
    verse_text = Column(Text, nullable=True)
    verse_source = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    query = relationship("Query", back_populates="response")

    def to_dict(self):
        return {
            "id": self.id,
            "query_id": self.query_id,
            "answer": self.answer,
            "latency_ms": self.latency_ms,
            "tokens_generated": self.tokens_generated,
            "detected_mood": self.detected_mood,
            "verse_id": self.verse_id,
            "verse_text": self.verse_text,
            "verse_source": self.verse_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Retrieval(Base):
    """Stores RAG retrieval results for each query."""
    __tablename__ = "retrievals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("queries.id", ondelete="CASCADE"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    similarity_score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=False)  # 1, 2, 3... for retrieval order
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    query = relationship("Query", back_populates="retrievals")

    def to_dict(self):
        return {
            "id": self.id,
            "query_id": self.query_id,
            "chunk_text": self.chunk_text,
            "source": self.source,
            "similarity_score": self.similarity_score,
            "rank": self.rank,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ErrorLog(Base):
    """Stores errors that occur during query processing."""
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("queries.id", ondelete="CASCADE"), nullable=True)  # Nullable for startup errors
    error_type = Column(String(100), nullable=False)  # e.g., "ValueError", "RuntimeError"
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    phase = Column(String(50), nullable=True)  # e.g., "rag_retrieval", "model_generation", "response_parsing"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    query = relationship("Query", back_populates="errors")

    def to_dict(self):
        return {
            "id": self.id,
            "query_id": self.query_id,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "phase": self.phase,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
