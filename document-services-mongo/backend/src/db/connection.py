import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .models import DocumentSchema


class Database:
    client: AsyncIOMotorClient = None
    db_name: str = "document_extraction"


db = Database()


async def connect_to_database():
    mongodb_url = os.getenv(
        "MONGODB_URL", "mongodb://admin:password123@mongodb:27017")

    db.client = AsyncIOMotorClient(mongodb_url)
    
    # Initialize Beanie with the document models
    await init_beanie(
        database=db.client[db.db_name],
        document_models=[DocumentSchema]
    )

    print(f"Connected to MongoDB database: {db.db_name}")


async def close_database_connection():
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB database")


async def get_database():
    """Get database instance for dependency injection"""
    return db.client[db.db_name]


async def init_db():
    await connect_to_database()
