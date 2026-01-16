"""
Database Service

MongoDB connection and database initialization.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

# Database configuration
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "taskmanager"

# Global database client
_client: Optional[AsyncIOMotorClient] = None
_database = None


async def connect_db():
    """
    Establish connection to MongoDB.

    Should be called on application startup.
    """
    global _client, _database

    _client = AsyncIOMotorClient(MONGODB_URL)
    _database = _client[DATABASE_NAME]

    # Verify connection
    await _client.admin.command("ping")
    print(f"Connected to MongoDB: {DATABASE_NAME}")


async def close_db():
    """
    Close the MongoDB connection.

    Should be called on application shutdown.
    """
    global _client

    if _client:
        _client.close()
        print("MongoDB connection closed")


async def get_db():
    """
    Get the database instance.

    Returns:
        The MongoDB database instance.

    Raises:
        RuntimeError: If database is not initialized.
    """
    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _database


async def init_db():
    """
    Initialize database with required collections and indexes.

    Creates collections and indexes if they don't exist.
    """
    await connect_db()
    db = await get_db()

    # Create indexes for users collection
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)
    await db.users.create_index("id", unique=True)

    # Create indexes for tasks collection
    await db.tasks.create_index("id", unique=True)
    await db.tasks.create_index("user_id")
    await db.tasks.create_index([("user_id", 1), ("status", 1)])
    await db.tasks.create_index([("user_id", 1), ("due_date", 1)])

    print("Database indexes created")


class DatabaseSession:
    """
    Context manager for database transactions.

    Usage:
        async with DatabaseSession() as session:
            await session.tasks.insert_one(...)
    """

    def __init__(self):
        self.session = None

    async def __aenter__(self):
        db = await get_db()
        self.session = await db.client.start_session()
        self.session.start_transaction()
        return db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.abort_transaction()
        else:
            await self.session.commit_transaction()
        await self.session.end_session()
