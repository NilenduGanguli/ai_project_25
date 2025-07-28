import os
from pymongo import AsyncMongoClient
from beanie import init_beanie
from .models import DocumentSchema


class Database:
    client: AsyncMongoClient = None
    database = None


db = Database()


async def connect_to_mongo():
    mongodb_url = os.getenv(
        "MONGODB_URL", "mongodb://admin:password123@localhost:27017/image_extractor?authSource=admin")

    db.client = AsyncMongoClient(
        mongodb_url,
    )

    database_name = "image_extractor"
    db.database = db.client[database_name]

    await init_beanie(
        database=db.database,
        document_models=[DocumentSchema]
    )

    print(f"Connected to MongoDB database: {database_name}")


async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")


async def init_db():
    await connect_to_mongo()
