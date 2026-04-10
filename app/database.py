from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.mongo_url)
    db = client[settings.mongo_db]
    await db.urls.create_index("alias", unique=True)
    await db.urls.create_index("original_url")
    print(f"[DB] Connected to MongoDB: {settings.mongo_db}")

async def close_db():
    global client
    if client:
        client.close()

def get_db():
    return db