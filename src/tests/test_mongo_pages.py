"""MongoDAO pages: skip and limit run inside the aggregation, and count() counts what a query matches."""
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from services.database.impl.mongo_dao import MongoDAO

TEAMS = {"class": "User", "references": {"team": {"table": "teams", "is_array": False}}}


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
    dao.db["teams"].insert_many([{"_id": "t1", "name": "Blue"}, {"_id": "t2", "name": "Amber"},
                                 {"_id": "t3", "name": "Crimson"}])
    # Inserted out of _id order: an unsorted collection scan returns them in insertion order
    dao.db["users"].insert_many([{"_id": 3, "name": "Cid", "team": "t3"}, {"_id": 1, "name": "Ann", "team": "t1"},
                                 {"_id": 4, "name": "Dee", "team": "t1"}, {"_id": 2, "name": "Bob", "team": "t2"}])
    yield dao
    client.drop_database(dbname)
    dao.handler.close()
    client.close()


def test_a_page_follows_sort_by(dao):
    assert [user["name"] for user in dao.fetch("users", sort_by=[("name", -1)], skip=1, limit=2)] == ["Cid", "Bob"]


def test_a_page_follows_the_id_when_no_sort_is_given(dao):
    assert [user["_id"] for user in dao.fetch("users", skip=1, limit=2)] == [2, 3]


def test_a_page_expands_its_references(dao):
    page = dao.fetch("users", expand=["team"], meta=TEAMS, skip=2, limit=1)
    assert list(page) == [{"_id": 3, "name": "Cid", "team": {"_id": "t3", "name": "Crimson"}}]


def test_a_page_sorted_on_an_expanded_field_is_cut_after_expanding(dao):
    page = dao.fetch("users", expand=["team"], meta=TEAMS, sort_by=[("team.name", 1), ("_id", 1)], skip=1, limit=2)
    assert [user["name"] for user in page] == ["Ann", "Dee"]


def test_count_counts_the_documents_a_query_matches(dao):
    assert dao.count("users") == 4
    assert dao.count("users", query=[("team", "==", "t1")]) == 2
