from pymongo import MongoClient
import pytest
import os

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://admin:admin@cluster0.tmhpxbi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
)
DB_NAME = "Users"
COLLECTION_NAME = "users_request"


@pytest.fixture
def mongo_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    collection.delete_many({})
    yield collection
    collection.delete_many({})
    client.close()
