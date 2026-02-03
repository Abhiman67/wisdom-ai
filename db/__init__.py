"""
Database module for Wisdom AI chat logging.
"""
from .database import engine, SessionLocal, get_db, init_db
from .models import Base, Query, Response, Retrieval, ErrorLog
from .operations import (
    create_query,
    create_response,
    create_retrieval,
    create_error_log,
    log_exception,
    get_query_by_id,
    get_recent_queries,
    get_recent_errors,
    get_db_stats,
)

__all__ = [
    # Database
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    # Models
    "Base",
    "Query",
    "Response",
    "Retrieval",
    "ErrorLog",
    # Operations
    "create_query",
    "create_response",
    "create_retrieval",
    "create_error_log",
    "log_exception",
    "get_query_by_id",
    "get_recent_queries",
    "get_recent_errors",
    "get_db_stats",
]
