"""DatabaseConnectionManager: DBTYPE is case-insensitive, so DBTYPE=SQLite opens the DBNAME file like DBTYPE=sqlite."""
import sqlite3

from api import settings
from services.database.database_connection_manager import DatabaseConnectionManager


def test_mixed_case_sqlite_dbtype_opens_the_file_named_by_dbname(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "DB_CONNECTION_STRING", None)
    db = tmp_path / "shop.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE lines (_id INTEGER PRIMARY KEY, Quantity INTEGER)")
    con.executemany("INSERT INTO lines VALUES (?, ?)", [(1, 5), (2, 15)])
    con.commit()
    con.close()

    dao = DatabaseConnectionManager().connect(dbtype="SQLite", dbname=str(db))

    assert sorted(row["Quantity"] for row in dao.fetch("lines")) == [5, 15]
