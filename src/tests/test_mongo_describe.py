"""MongoDAO.describe(): the whole database schema, inferred from the documents themselves."""
import uuid
from datetime import datetime

import pytest
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from services.database.impl.mongo_dao import MongoDAO

ANN, BOB, CORE = (str(ObjectId()) for _ in range(3))


@pytest.fixture
def dao():
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=1000)
    try:
        client.admin.command("ping")
    except PyMongoError:
        client.close()
        pytest.skip("needs MongoDB on localhost:27017")
    dbname = f"spore_test_{uuid.uuid4().hex[:8]}"
    dao = MongoDAO(dbname)
    dao.db["teams"].insert_one({"_id": CORE, "name": "Core", "members": [ANN, BOB]})
    dao.db["users"].insert_many([
        {"_id": ANN, "name": "Ann", "age": 41, "team": CORE, "tags": ["a"],
         "address": {"city": "León"}, "active": True, "nickname": None},
        {"_id": BOB, "name": "Bob", "team": CORE, "joined": datetime(2026, 1, 1)},
    ])
    dao.db.create_collection("archive")
    yield dao
    client.drop_database(dbname)
    dao.handler.close()
    client.close()


def test_describe_lists_every_collection_including_empty_ones(dao):
    assert sorted(dao.describe()) == ["archive", "teams", "users"]


def test_describe_merges_the_fields_of_every_sampled_document(dao):
    assert dao.describe()["users"]["properties"] == {
        "_id": "string", "name": "string", "age": "integer", "team": "string", "tags": "array",
        "address": "object", "active": "boolean", "nickname": "null", "joined": "datetime",
    }


def test_describe_finds_references_by_looking_ids_up(dao):
    schema = dao.describe()

    assert schema["users"]["references"] == {"team": {"table": "teams", "is_array": False}}
    assert schema["teams"]["references"] == {"members": {"table": "users", "is_array": True}}


def test_describe_keys_collections_by_id(dao):
    assert dao.describe()["archive"] == {"table": "archive", "properties": {}, "primary_key": ["_id"],
                                         "references": {}}
