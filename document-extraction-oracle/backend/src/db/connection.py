import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from .models import Base
import oracledb


class Database:
    engine = None
    session_factory = None


db = Database()


def connect_to_database():
    """Connect to Oracle database using environment variables"""
    oracle_user = os.getenv("ORACLE_USER", "admin")
    oracle_password = os.getenv("ORACLE_PASSWORD", "password123")
    oracle_dsn = os.getenv("ORACLE_DSN", "localhost:1521/XEPDB1")
    
    # Construct Oracle connection string for SQLAlchemy
    # Format: oracle+oracledb://user:password@host:port/?service_name=service
    database_url = f"oracle+oracledb://{oracle_user}:{oracle_password}@{oracle_dsn}"
    
    # Initialize thick mode if needed (for better compatibility)
    try:
        oracledb.init_oracle_client()
    except Exception:
        pass  # Thin mode will be used
    
    db.engine = create_engine(
        database_url,
        echo=False,
        poolclass=NullPool,  # Oracle handles connection pooling
        connect_args={
            "encoding": "UTF-8",
            "nencoding": "UTF-8",
        }
    )
    
    db.session_factory = sessionmaker(
        bind=db.engine,
        expire_on_commit=False,
    )
    
    # Create tables if they don't exist
    Base.metadata.create_all(db.engine)
    
    print(f"Connected to Oracle database: {oracle_dsn}")


def close_database_connection():
    if db.engine:
        db.engine.dispose()
        print("Disconnected from Oracle database")


def get_session() -> Session:
    """Get database session for dependency injection"""
    session = db.session_factory()
    try:
        yield session
    finally:
        session.close()


def init_db():
    connect_to_database()
