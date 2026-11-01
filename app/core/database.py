from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import settings
from app.modules.note.models import Note
from app.modules.user.models import User


class MongoDB:
    def __init__(self):
        self.client: AsyncMongoClient | None = None

    async def connect(self):
        self.client = AsyncMongoClient(settings.DATABASE_URL)
        await self.client.admin.command("ping")

        await init_beanie(
            database=self.client[settings.DATABASE_NAME], document_models=[User, Note]
        )

        print(f"Connected to MongoDB: {settings.DATABASE_NAME}")

    async def disconnect(self):
        if self.client is not None:
            await self.client.close()
            print("MongoDB connection closed")


mongodb = MongoDB()
