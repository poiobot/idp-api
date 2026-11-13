"""GenericDAO.describe(): one entity's scheme, or the whole database's when no entity is given."""
import sqlite3
from typing import Optional

import pytest
from pydantic import BaseModel, Field

from api import settings
from data.generic_dao import GenericDAO


class Shipper(BaseModel):
    id: Optional[int] = Field(default=None, alias="_id", json_schema_extra={"table": "Shippers"})
    CompanyName: Optional[str] = None


@pytest.fixture
def dao(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "DB_CONNECTION_STRING", None)
    db = tmp_path / "shop.db"
    con = sqlite3.connect(db)
    con.executescript("""
        CREATE TABLE Shippers (ShipperID INTEGER PRIMARY KEY, CompanyName TEXT);
        CREATE TABLE Orders (OrderID INTEGER PRIMARY KEY, ShipVia INTEGER REFERENCES Shippers (ShipperID));
    """)
    con.close()
    dao = GenericDAO(dbtype="sqlite", dbname=str(db))
    yield dao
    dao.handler.engine.dispose()


def test_describe_without_an_entity_returns_every_table(dao):
    schema = dao.describe()

    assert sorted(schema) == ["Orders", "Shippers"]
    assert schema["Orders"]["references"] == {"ShipVia": {"table": "Shippers", "is_array": False}}


def test_describe_with_an_entity_returns_that_entity(dao):
    assert dao.describe(Shipper)["table"] == "Shippers"


# Pages and counts go through to the database.

def add_shippers(dao):
    with dao.handler.engine.begin() as conn:
        conn.exec_driver_sql("INSERT INTO Shippers VALUES (1, 'Speedy Express'), (2, 'United Package'), "
                             "(3, 'Federal Shipping')")


def test_fetch_reads_one_page(dao):
    add_shippers(dao)
    assert [shipper.CompanyName for shipper in dao.fetch(Shipper, skip=1, limit=1)] == ["United Package"]


def test_count_counts_the_matching_rows(dao):
    add_shippers(dao)
    assert dao.count(Shipper) == 3
    assert dao.count(Shipper, query=[("CompanyName", "like", "Express")]) == 1
