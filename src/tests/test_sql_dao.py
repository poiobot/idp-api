"""SqlDAO against plain SQL schemas like Northwind, and against Spore-shaped tables.

Plain schemas have integer keys the database assigns, composite keys, table names with
spaces, and none of Spore's _version/_created/_updated/_state columns. Spore-shaped
tables (a text _id plus those columns) must keep working as before.
"""
import sqlite3
import types
from datetime import datetime, timezone

import pytest
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from api import settings
from services.database.impl.sql_dao import SqlDAO

SCHEMA = """
CREATE TABLE Shippers (ShipperID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, CompanyName TEXT NOT NULL, Phone TEXT);
INSERT INTO Shippers VALUES (1, 'Speedy Express', '(503) 555-9831'), (2, 'United Package', '(503) 555-3199');

CREATE TABLE Orders (OrderID INTEGER PRIMARY KEY, ShipVia INTEGER REFERENCES Shippers (ShipperID));
INSERT INTO Orders VALUES (10248, 2);

CREATE TABLE OrderLines (OrderID INTEGER NOT NULL, ProductID INTEGER NOT NULL, Quantity INTEGER,
                         PRIMARY KEY (OrderID, ProductID));
INSERT INTO OrderLines VALUES (10248, 11, 12), (10248, 42, 10), (10249, 14, 9);

CREATE TABLE "Order Details" (OrderID INTEGER NOT NULL, ProductID INTEGER NOT NULL, Quantity INTEGER,
                              PRIMARY KEY (OrderID, ProductID));
INSERT INTO "Order Details" VALUES (10248, 11, 12), (10248, 42, 10), (10249, 14, 9);

CREATE TABLE notes (_id TEXT PRIMARY KEY, text TEXT, _version INTEGER, _created TEXT, _updated TEXT, _state TEXT);
INSERT INTO notes VALUES ('n1', 'hello', 1, '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00', NULL);
"""


@pytest.fixture
def path(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "DB_CONNECTION_STRING", None)
    db = tmp_path / "northwind.db"
    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    con.close()
    return db


@pytest.fixture
def dao(path):
    dao = SqlDAO(dbname=str(path), dbtype="sqlite")
    yield dao
    dao.engine.dispose()


def rows(path, sql, *args):
    """Read the database directly, without going through SqlDAO."""
    con = sqlite3.connect(path)
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


# Reads that already work keep working.

def test_find_by_id_returns_the_row_for_an_integer_key(dao):
    assert dao.find_by_id("Shippers", 2) == {"ShipperID": 2, "CompanyName": "United Package", "Phone": "(503) 555-3199"}


# ?expand= replaces a reference key with the row it points to, as MongoDAO's $lookup does.

SHIP_VIA = {"references": {"ShipVia": {"table": "Shippers", "is_array": False}}}
REPORTS_TO = {"references": {"ReportsTo": {"table": "Employees", "is_array": False}}}


def add_employees(path):
    """Employees report to another employee (a self-reference); the top of the chain reports to NULL."""
    con = sqlite3.connect(path)
    con.executescript("""
        CREATE TABLE Employees (EmployeeID INTEGER PRIMARY KEY, LastName TEXT,
                                ReportsTo INTEGER REFERENCES Employees (EmployeeID));
        INSERT INTO Employees VALUES (1, 'Davolio', 2), (2, 'Fuller', NULL);
    """)
    con.close()


def test_expand_nests_the_referenced_row_under_its_key(dao):
    assert list(dao.fetch("Orders", expand=["ShipVia"], meta=SHIP_VIA)) == [
        {"OrderID": 10248, "ShipVia": {"ShipperID": 2, "CompanyName": "United Package", "Phone": "(503) 555-3199"}}]


def test_expand_follows_a_self_reference(dao, path):
    add_employees(path)
    [davolio] = dao.fetch("Employees", query=[("EmployeeID", "==", 1)], expand=["ReportsTo"], meta=REPORTS_TO)
    assert davolio["ReportsTo"] == {"EmployeeID": 2, "LastName": "Fuller", "ReportsTo": None}


def test_expand_leaves_a_null_reference_as_none(dao, path):
    add_employees(path)
    [fuller] = dao.fetch("Employees", query=[("EmployeeID", "==", 2)], expand=["ReportsTo"], meta=REPORTS_TO)
    assert fuller["ReportsTo"] is None


def test_expand_reads_referenced_rows_in_batches(dao, path, monkeypatch):
    con = sqlite3.connect(path)
    con.execute("INSERT INTO Orders VALUES (10249, 1)")
    con.commit()
    con.close()
    monkeypatch.setattr(dao, "expand_batch", 1)
    found = dao.fetch("Orders", expand=["ShipVia"], meta=SHIP_VIA, sort_by=[("OrderID", 1)])
    assert [order["ShipVia"] for order in found] == [
        {"ShipperID": 2, "CompanyName": "United Package", "Phone": "(503) 555-3199"},
        {"ShipperID": 1, "CompanyName": "Speedy Express", "Phone": "(503) 555-9831"}]


def test_expand_keeps_the_key_when_the_referenced_row_is_missing(dao, path):
    con = sqlite3.connect(path)
    con.execute("INSERT INTO Orders VALUES (10249, 99)")
    con.commit()
    con.close()
    assert list(dao.fetch("Orders", query=[("OrderID", "==", 10249)], expand=["ShipVia"], meta=SHIP_VIA)) == [
        {"OrderID": 10249, "ShipVia": 99}]


# Multi-row reads yield rows as the cursor produces them; they never build the whole result first.

def sql_statements(dao):
    """Every statement dao sends to the database from now on."""
    statements = []
    event.listen(dao.engine, "before_cursor_execute", lambda conn, cursor, statement, *rest: statements.append(statement))
    return statements


def add_orders(path, *orders):
    con = sqlite3.connect(path)
    con.executemany("INSERT INTO Orders VALUES (?, ?)", orders)
    con.commit()
    con.close()


@pytest.mark.parametrize("read", [
    lambda dao: dao.fetch("Shippers"),
    lambda dao: dao.find_objects_list("Shippers", [1, 2]),
    lambda dao: dao.find_by_key_value("Shippers", "ShipperID", ">", 0),
    lambda dao: dao.find_by_key_value_like("Shippers", "Phone", "555"),
], ids=["fetch", "find_objects_list", "find_by_key_value", "find_by_key_value_like"])
def test_multi_row_reads_yield_their_rows(dao, read):
    found = read(dao)
    assert isinstance(found, types.GeneratorType)
    assert [row["ShipperID"] for row in found] == [1, 2]


def test_fetch_reads_nothing_until_its_rows_are_consumed(dao):
    list(dao.fetch("Shippers"))  # the first read reflects the table; reflection isn't the read under test
    statements = sql_statements(dao)
    found = dao.fetch("Shippers")
    assert statements == []
    next(found)
    assert len(statements) == 1


def test_fetch_reads_and_expands_rows_one_batch_at_a_time(dao, path, monkeypatch):
    add_orders(path, (10249, 1), (10250, 2), (10251, 1), (10252, 2))
    monkeypatch.setattr(dao, "fetch_batch", 2, raising=False)
    list(dao.fetch("Shippers"))  # reflect the table the expansion reads before counting its reads
    statements = sql_statements(dao)
    found = iter(dao.fetch("Orders", expand=["ShipVia"], meta=SHIP_VIA))
    next(found)
    after_first_row = sum('FROM "Shippers"' in s for s in statements)
    list(found)
    assert (after_first_row, sum('FROM "Shippers"' in s for s in statements)) == (1, 3)


def test_a_partly_read_fetch_holds_its_connection_until_closed(dao):
    found = iter(dao.fetch("Shippers"))
    next(found)
    assert dao.engine.pool.checkedout() == 1
    found.close()
    assert dao.engine.pool.checkedout() == 0


# Pages: skip and limit go into the SQL, so a page reads only its own rows.

def add_regions(path):
    """Text keys inserted out of key order: SQLite returns unordered rows in insertion order."""
    con = sqlite3.connect(path)
    con.executescript("""
        CREATE TABLE Regions (Code TEXT PRIMARY KEY, Name TEXT);
        INSERT INTO Regions VALUES ('c', 'Central'), ('a', 'Atlantic'), ('d', 'Desert'), ('b', 'Boreal');
    """)
    con.close()


def test_a_page_follows_the_primary_key_when_no_sort_is_given(dao, path):
    add_regions(path)
    assert [region["Code"] for region in dao.fetch("Regions", skip=1, limit=2)] == ["b", "c"]


def test_skip_without_a_limit_returns_the_remaining_rows(dao, path):
    add_regions(path)
    assert [region["Code"] for region in dao.fetch("Regions", skip=3)] == ["d"]


def test_a_page_follows_sort_by(dao, path):
    add_regions(path)
    assert [region["Code"] for region in dao.fetch("Regions", sort_by=[("Name", -1)], skip=1, limit=2)] == ["c", "b"]


def test_a_page_is_filtered_and_expanded(dao, path):
    add_orders(path, (10249, 1), (10250, 2))
    page = dao.fetch("Orders", query=[("OrderID", ">", 10248)], expand=["ShipVia"], meta=SHIP_VIA, skip=1, limit=1)
    assert list(page) == [
        {"OrderID": 10250, "ShipVia": {"ShipperID": 2, "CompanyName": "United Package", "Phone": "(503) 555-3199"}}]


def test_count_counts_the_rows_a_query_matches(dao):
    assert dao.count("Order Details") == 3
    assert dao.count("Order Details", query=[("OrderID", "==", 10248)]) == 2


# Table names with spaces are quoted.

def test_fetch_filters_sorts_and_projects_a_table_whose_name_has_a_space(dao):
    found = list(dao.fetch("Order Details", query=[("Quantity", ">", 9)], sort_by=[("Quantity", -1)],
                           keys=["ProductID", "Quantity"]))
    assert found == [{"ProductID": 11, "Quantity": 12}, {"ProductID": 42, "Quantity": 10}]


def test_distinct_reads_a_table_whose_name_has_a_space(dao):
    assert sorted(dao.distinct("Order Details", "OrderID")) == [10248, 10249]


def test_insert_into_a_table_whose_name_has_a_space(dao, path):
    dao.insert("Order Details", {"OrderID": 10250, "ProductID": 41, "Quantity": 10})
    assert rows(path, 'SELECT Quantity FROM "Order Details" WHERE OrderID = 10250 AND ProductID = 41') == [(10,)]


def test_delete_many_removes_matching_rows_from_a_table_whose_name_has_a_space(dao, path):
    assert dao.delete_many("Order Details", query=[("OrderID", "==", 10248)], physical_delete=True) == 2
    assert rows(path, 'SELECT OrderID, ProductID FROM "Order Details"') == [(10249, 14)]


def test_delete_all_empties_a_table_whose_name_has_a_space(dao, path):
    assert dao.delete_all("Order Details", physical_delete=True) == 3
    assert rows(path, 'SELECT count(*) FROM "Order Details"') == [(0,)]


# Composite keys: a row is addressed by its whole key, never by the first column alone.

@pytest.mark.parametrize("key", [{"OrderID": 10248, "ProductID": 42}, (10248, 42)], ids=["dict", "tuple"])
def test_find_by_id_accepts_a_whole_composite_key(dao, key):
    assert dao.find_by_id("OrderLines", key) == {"OrderID": 10248, "ProductID": 42, "Quantity": 10}


def test_find_by_id_with_one_value_for_a_composite_key_raises(dao):
    with pytest.raises(ValueError, match="OrderID, ProductID"):
        dao.find_by_id("OrderLines", 10248)


def test_fetch_by__id_on_a_composite_key_raises(dao):
    with pytest.raises(ValueError, match="OrderID, ProductID"):
        dao.fetch("OrderLines", query=[("_id", "==", 10248)])


def test_update_by_composite_key_changes_only_that_row(dao, path):
    dao.update("OrderLines", {"OrderID": 10248, "ProductID": 42}, {"Quantity": 99})
    assert rows(path, "SELECT OrderID, ProductID, Quantity FROM OrderLines ORDER BY 1, 2") == [
        (10248, 11, 12), (10248, 42, 99), (10249, 14, 9)]


def test_delete_by_composite_key_removes_only_that_row(dao, path):
    assert dao.delete("OrderLines", {"OrderID": 10248, "ProductID": 11}) is True
    assert rows(path, "SELECT OrderID, ProductID FROM OrderLines ORDER BY 1, 2") == [(10248, 42), (10249, 14)]


def test_delete_with_one_value_for_a_composite_key_raises_and_deletes_nothing(dao, path):
    with pytest.raises(ValueError, match="OrderID, ProductID"):
        dao.delete("OrderLines", 10248)
    assert rows(path, "SELECT count(*) FROM OrderLines") == [(3,)]


# Writes on tables without Spore's bookkeeping columns.

def test_insert_into_a_plain_table_stores_the_row_under_the_key_the_database_assigns(dao, path):
    # Shaped like GenericDAO's model_dump(by_alias=True): _id unset, bookkeeping fields filled in.
    now = datetime(2026, 11, 5, tzinfo=timezone.utc)
    stored = dao.insert("Shippers", {"_id": None, "CompanyName": "Federal Shipping", "Phone": "(503) 555-9931",
                                     "_version": 1, "_created": now, "_updated": now})
    assert stored["ShipperID"] == 3
    assert rows(path, "SELECT ShipperID, CompanyName, Phone FROM Shippers WHERE ShipperID = 3") == [
        (3, "Federal Shipping", "(503) 555-9931")]


def test_update_on_a_plain_table_changes_the_row(dao, path):
    updated = dao.update("Shippers", 1, {"Phone": "(503) 555-0000"})
    assert updated["Phone"] == "(503) 555-0000"
    assert rows(path, "SELECT Phone FROM Shippers WHERE ShipperID = 1") == [("(503) 555-0000",)]


def test_upsert_of_an_existing_row_in_a_plain_table_updates_it(dao, path):
    dao.upsert("Shippers", {"ShipperID": 2, "CompanyName": "United Package", "Phone": "(503) 555-1111"})
    assert rows(path, "SELECT Phone FROM Shippers WHERE ShipperID = 2") == [("(503) 555-1111",)]


def test_upsert_of_a_new_row_in_a_plain_table_inserts_it(dao, path):
    dao.upsert("Shippers", {"CompanyName": "Federal Shipping", "Phone": "(503) 555-9931"})
    assert rows(path, "SELECT ShipperID, CompanyName FROM Shippers WHERE ShipperID = 3") == [(3, "Federal Shipping")]


@pytest.mark.parametrize("soft_delete", [
    lambda dao: dao.delete("Shippers", 1, physical_delete=False),
    lambda dao: dao.delete_objects_list("Shippers", [1], physical_delete=False),
    lambda dao: dao.delete_many("Shippers", query=[("ShipperID", "==", 1)]),
    lambda dao: dao.delete_all("Shippers"),
], ids=["delete", "delete_objects_list", "delete_many", "delete_all"])
def test_soft_delete_on_a_table_without__state_raises_and_deletes_nothing(dao, path, soft_delete):
    with pytest.raises(ValueError, match="_state"):
        soft_delete(dao)
    assert rows(path, "SELECT count(*) FROM Shippers") == [(2,)]


# Spore-shaped tables keep their bookkeeping.

def test_insert_into_a_spore_table_generates_a_uuid_and_bookkeeping(dao, path):
    stored = dao.insert("notes", {"text": "new"})
    assert len(stored["_id"]) == 36
    assert rows(path, "SELECT text, _version, _created IS NOT NULL FROM notes WHERE _id = ?", stored["_id"]) == [
        ("new", 1, 1)]


def test_update_on_a_spore_table_bumps_the_version_and_updated_time(dao, path):
    dao.update("notes", "n1", {"text": "edited"})
    assert rows(path, "SELECT text, _version, _updated > '2026-01-01T00:00:00+00:00' FROM notes WHERE _id = 'n1'") == [
        ("edited", 2, 1)]


def test_update_of_a_missing_row_returns_none(dao):
    assert dao.update("notes", "missing", {"text": "x"}) is None


def test_soft_delete_on_a_spore_table_marks_the_row_deleted(dao, path):
    assert dao.delete("notes", "n1", physical_delete=False) is True
    assert rows(path, "SELECT _state FROM notes WHERE _id = 'n1'") == [("DELETED",)]


# Failed writes raise instead of returning None.

def test_inserting_a_duplicate_key_raises(dao):
    with pytest.raises(IntegrityError):
        dao.insert("Shippers", {"ShipperID": 1, "CompanyName": "Duplicate"})


def test_a_failed_update_raises(dao):
    with pytest.raises(SQLAlchemyError):
        dao.update("Shippers", 1, {"NoSuchColumn": 1})


def test_a_failed_upsert_raises(dao):
    with pytest.raises(SQLAlchemyError):
        dao.upsert("Shippers", {"ShipperID": 1, "NoSuchColumn": 1})


# describe() reports the whole database schema, read from the database itself.

def test_describe_lists_every_table_but_sqlite_internals(dao):
    # Shippers' AUTOINCREMENT makes SQLite create sqlite_sequence, which is not part of the schema
    assert sorted(dao.describe()) == ["Order Details", "OrderLines", "Orders", "Shippers", "notes"]


def test_describe_reports_columns_primary_key_and_foreign_keys(dao):
    assert dao.describe()["Orders"] == {
        "table": "Orders",
        "properties": {"OrderID": "integer", "ShipVia": "integer"},
        "primary_key": ["OrderID"],
        "references": {"ShipVia": {"table": "Shippers", "is_array": False}},
    }


def test_describe_reports_composite_primary_keys(dao):
    assert dao.describe()["Order Details"]["primary_key"] == ["OrderID", "ProductID"]


def test_describe_names_column_types_independently_of_the_database(path):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE Samples (Price REAL, Amount NUMERIC, Shipped DATETIME, Born DATE, "
                "Photo BLOB, Active BOOLEAN)")
    con.commit()
    con.close()
    dao = SqlDAO(dbname=str(path), dbtype="sqlite")
    try:
        assert dao.describe()["Samples"]["properties"] == {
            "Price": "number", "Amount": "number", "Shipped": "datetime",
            "Born": "date", "Photo": "binary", "Active": "boolean",
        }
    finally:
        dao.engine.dispose()
