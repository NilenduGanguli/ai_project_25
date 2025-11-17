import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from .models import Base


class Database:
    engine = None
    async_session_factory = None


db = Database()


async def connect_to_database():
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://admin:password123@postgres:5432/document_extraction")

    db.engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )

    db.async_session_factory = async_sessionmaker(
        db.engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create tables
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print(f"Connected to PostgreSQL database")


async def close_database_connection():
    if db.engine:
        await db.engine.dispose()
        print("Disconnected from PostgreSQL database")


async def get_session() -> AsyncSession:
    """Get database session for dependency injection"""
    async with db.async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    await connect_to_database()
