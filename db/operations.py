"""
CRUD operations for Wisdom AI database.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List, Dict, Any
from datetime import datetime
import traceback

from .models import Query, Response, Retrieval, ErrorLog


# -------------------------
# Query Operations
# -------------------------

def create_query(
    db: Session,
    question: str,
    session_id: Optional[str] = None,
    temperature: float = 0.6,
    max_tokens: int = 300,
    rag_enabled: bool = True,
) -> Query:
    """Create a new query record."""
    query = Query(
        question=question,
        session_id=session_id,
        temperature=temperature,
        max_tokens=max_tokens,
        rag_enabled=rag_enabled,
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


def get_query_by_id(db: Session, query_id: int) -> Optional[Query]:
    """Get a query by its ID with related response."""
    return db.query(Query).filter(Query.id == query_id).first()


def get_recent_queries(db: Session, limit: int = 10, offset: int = 0) -> List[Query]:
    """Get recent queries ordered by creation time (newest first)."""
    return (
        db.query(Query)
        .order_by(desc(Query.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_queries_by_session(db: Session, session_id: str) -> List[Query]:
    """Get all queries for a specific session."""
    return (
        db.query(Query)
        .filter(Query.session_id == session_id)
        .order_by(Query.created_at)
        .all()
    )


# -------------------------
# Response Operations
# -------------------------

def create_response(
    db: Session,
    query_id: int,
    answer: str,
    latency_ms: Optional[int] = None,
    tokens_generated: Optional[int] = None,
    detected_mood: Optional[str] = None,
    verse_id: Optional[str] = None,
    verse_text: Optional[str] = None,
    verse_source: Optional[str] = None,
) -> Response:
    """Create a response record for a query."""
    response = Response(
        query_id=query_id,
        answer=answer,
        latency_ms=latency_ms,
        tokens_generated=tokens_generated,
        detected_mood=detected_mood,
        verse_id=verse_id,
        verse_text=verse_text,
        verse_source=verse_source,
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    return response


# -------------------------
# Retrieval Operations
# -------------------------

def create_retrieval(
    db: Session,
    query_id: int,
    chunk_text: str,
    rank: int,
    source: Optional[str] = None,
    similarity_score: Optional[float] = None,
) -> Retrieval:
    """Create a retrieval record for a query."""
    retrieval = Retrieval(
        query_id=query_id,
        chunk_text=chunk_text,
        rank=rank,
        source=source,
        similarity_score=similarity_score,
    )
    db.add(retrieval)
    db.commit()
    db.refresh(retrieval)
    return retrieval


def create_retrievals_batch(
    db: Session,
    query_id: int,
    retrievals: List[Dict[str, Any]],
) -> List[Retrieval]:
    """Create multiple retrieval records at once."""
    retrieval_objs = []
    for i, r in enumerate(retrievals):
        retrieval = Retrieval(
            query_id=query_id,
            chunk_text=r.get("chunk_text", ""),
            rank=r.get("rank", i + 1),
            source=r.get("source"),
            similarity_score=r.get("similarity_score"),
        )
        db.add(retrieval)
        retrieval_objs.append(retrieval)
    db.commit()
    for r in retrieval_objs:
        db.refresh(r)
    return retrieval_objs


# -------------------------
# Error Log Operations
# -------------------------

def create_error_log(
    db: Session,
    error_type: str,
    error_message: str,
    query_id: Optional[int] = None,
    stack_trace: Optional[str] = None,
    phase: Optional[str] = None,
) -> ErrorLog:
    """Create an error log record."""
    error = ErrorLog(
        query_id=query_id,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        phase=phase,
    )
    db.add(error)
    db.commit()
    db.refresh(error)
    return error


def log_exception(
    db: Session,
    exception: Exception,
    query_id: Optional[int] = None,
    phase: Optional[str] = None,
) -> ErrorLog:
    """Convenience function to log an exception."""
    return create_error_log(
        db=db,
        error_type=type(exception).__name__,
        error_message=str(exception),
        query_id=query_id,
        stack_trace=traceback.format_exc(),
        phase=phase,
    )


def get_recent_errors(db: Session, limit: int = 10, offset: int = 0) -> List[ErrorLog]:
    """Get recent errors ordered by creation time (newest first)."""
    return (
        db.query(ErrorLog)
        .order_by(desc(ErrorLog.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )


# -------------------------
# Statistics
# -------------------------

def get_db_stats(db: Session) -> Dict[str, Any]:
    """Get database statistics."""
    total_queries = db.query(func.count(Query.id)).scalar() or 0
    total_responses = db.query(func.count(Response.id)).scalar() or 0
    total_errors = db.query(func.count(ErrorLog.id)).scalar() or 0
    
    # Average latency (only for responses with latency data)
    avg_latency = db.query(func.avg(Response.latency_ms)).filter(
        Response.latency_ms.isnot(None)
    ).scalar()
    
    # Queries today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    queries_today = db.query(func.count(Query.id)).filter(
        Query.created_at >= today_start
    ).scalar() or 0
    
    # RAG usage percentage
    rag_enabled_count = db.query(func.count(Query.id)).filter(
        Query.rag_enabled == True
    ).scalar() or 0
    rag_percentage = (rag_enabled_count / total_queries * 100) if total_queries > 0 else 0
    
    return {
        "total_queries": total_queries,
        "total_responses": total_responses,
        "total_errors": total_errors,
        "avg_latency_ms": round(avg_latency, 2) if avg_latency else None,
        "queries_today": queries_today,
        "rag_usage_percentage": round(rag_percentage, 1),
    }
