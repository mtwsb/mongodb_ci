from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.errors import DuplicateKeyError
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://admin:admin@cluster0.tmhpxbi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = "Users"
COLLECTION_NAME = "users_request"
