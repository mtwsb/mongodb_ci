from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.errors import DuplicateKeyError
import pytest
import uuid
import time

MONGO_URI = "mongodb+srv://admin:admin@cluster0.tmhpxbi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
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


def test_insert_one_with_extra_fields(mongo_collection):
    doc = {
        "name": "Tomasz",
        "destination": "Tokyo",
        "age": 30,
        "email": "tomasz@example.com",
        "phone": "+48123123123",
        "message": "Chcę odwiedzić Tokyo w maju",
    }
    result = mongo_collection.insert_one(doc)
    assert result.inserted_id is not None

    found = mongo_collection.find_one({"_id": result.inserted_id})
    assert found["email"] == "tomasz@example.com"
    assert found["phone"] == "+48123123123"
    assert found["message"] == "Chcę odwiedzić Tokyo w maju"


def test_find_by_destination(mongo_collection):
    destinations = ["Tokyo", "Berlin", "Paris", "Tokyo"]
    for d in destinations:
        mongo_collection.insert_one({"name": "Test", "destination": d})

    tokyo_docs = list(mongo_collection.find({"destination": "Tokyo"}))
    assert len(tokyo_docs) == 2
    for doc in tokyo_docs:
        assert doc["destination"] == "Tokyo"


def test_bulk_insert_performance_large(mongo_collection):
    docs = [{"_id": str(uuid.uuid4()), "x": i} for i in range(10_000)]
    start = time.perf_counter()
    mongo_collection.insert_many(docs)
    duration = time.perf_counter() - start
    print(f"Wstawiono 10 000 dokumentów w {duration:.4f} sekundy")
    assert duration < 10


def test_insert_unique_constraint(mongo_collection):
    unique_id = str(uuid.uuid4())
    mongo_collection.insert_one({"_id": unique_id, "name": "A"})
    with pytest.raises(DuplicateKeyError):
        mongo_collection.insert_one({"_id": unique_id, "name": "B"})


def test_find_by_id_benchmark(mongo_collection, benchmark):
    docs = [
        {"_id": str(uuid.uuid4()), "destination": f"City{i % 100}"} for i in range(5000)
    ]
    mongo_collection.insert_many(docs)
    sample_id = docs[2500]["_id"]

    def find_by_id():
        mongo_collection.find_one({"_id": sample_id})

    benchmark(find_by_id)


def test_find_by_destination_benchmark(mongo_collection, benchmark):
    docs = [
        {"_id": str(uuid.uuid4()), "destination": f"City{i % 100}"} for i in range(5000)
    ]
    mongo_collection.insert_many(docs)
    sample_destination = docs[2500]["destination"]

    def find_by_destination():
        list(mongo_collection.find({"destination": sample_destination}))

    benchmark(find_by_destination)


def test_transaction_insert_and_rollback():
    client = MongoClient(MONGO_URI)
    session = client.start_session()
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    try:
        with session.start_transaction():
            collection.insert_one({"_id": "txn_test", "value": 1}, session=session)
            raise RuntimeError("Rollback test")
    except RuntimeError:
        pass

    result = collection.find_one({"_id": "txn_test"})
    assert result is None
    session.end_session()
    client.close()


