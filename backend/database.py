"""
database.py
MongoDB database connection and management
"""

import os
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
DATABASE_NAME = "insurspeak"

# Global database client
_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def get_database() -> Database:
    """
    Get or create MongoDB database connection

    Returns:
        MongoDB database instance
    """
    global _client, _database

    if _database is None:
        try:
            _client = MongoClient(MONGODB_URL)
            _database = _client[DATABASE_NAME]

            # Test connection
            _client.server_info()
            print(f"Connected to MongoDB: {DATABASE_NAME}")

        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            print("Running in no-database mode. User data will not be persisted.")
            # Return None or mock database for development without MongoDB
            _database = None

    return _database


def get_collection(collection_name: str) -> Optional[Collection]:
    """
    Get a specific collection from the database

    Args:
        collection_name: Name of the collection

    Returns:
        MongoDB collection instance or None if database not available
    """
    db = get_database()
    if db is not None:
        return db[collection_name]
    return None


def close_database():
    """Close database connection"""
    global _client, _database
    if _client is not None:
        _client.close()
        _client = None
        _database = None
        print("Database connection closed")


# Collection getters
def get_users_collection() -> Optional[Collection]:
    """Get users collection"""
    return get_collection("users")


def get_policies_collection() -> Optional[Collection]:
    """Get policies collection"""
    return get_collection("policies")


def get_conversations_collection() -> Optional[Collection]:
    """Get conversations collection"""
    return get_collection("conversations")


def get_claims_collection() -> Optional[Collection]:
    """Get claims collection"""
    return get_collection("claims")


# Database initialization
def init_database():
    """
    Initialize database with indexes and constraints
    """
    db = get_database()
    if db is None:
        print("Database not available. Skipping initialization.")
        return

    try:
        # Users collection indexes
        users = get_users_collection()
        if users is not None:
            users.create_index("email", unique=True)
            users.create_index("created_at")

        # Policies collection indexes
        policies = get_policies_collection()
        if policies is not None:
            policies.create_index("user_id")
            policies.create_index([("user_id", 1), ("created_at", -1)])
            policies.create_index("insurance_type")
            policies.create_index("status")

        # Conversations collection indexes
        conversations = get_conversations_collection()
        if conversations is not None:
            conversations.create_index("user_id")
            conversations.create_index("policy_id")
            conversations.create_index([("user_id", 1), ("created_at", -1)])

        # Claims collection indexes
        claims = get_claims_collection()
        if claims is not None:
            claims.create_index("user_id")
            claims.create_index("policy_id")
            claims.create_index([("user_id", 1), ("created_at", -1)])

        print("Database initialized successfully")

    except Exception as e:
        print(f"Error initializing database: {e}")
