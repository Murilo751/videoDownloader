import pytest

import db


class Cursor:
    def __init__(self, fail=False):
        self.fail = fail
        self.sql = None
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def execute(self, sql, params):
        if self.fail:
            raise RuntimeError("db unavailable")
        self.sql = sql
    def fetchone(self):
        return {"id": 1, "password_hash": "hash"}
    def fetchall(self):
        return [{"id": 1}]


class Connection:
    def __init__(self, cursor):
        self.current = cursor
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def cursor(self):
        return self.current


def test_connection_and_run(monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test")
    monkeypatch.setattr(db.psycopg, "connect", lambda url, row_factory: Connection(Cursor()))
    assert isinstance(db.connection(), Connection)
    assert db.run("web", "select", "req-1", "SELECT 1", mode="one")["id"] == 1
    assert db.run("cli", "list", "req-2", "SELECT 1", mode="all")[0]["id"] == 1
    assert db.run("web", "write", "req-3", "SELECT 1") is None
    assert '"request_id": "req-1"' in capsys.readouterr().out
    monkeypatch.setattr(db.psycopg, "connect", lambda url, row_factory: Connection(Cursor(True)))
    with pytest.raises(RuntimeError):
        db.run("cli", "fail", "req-4", "bad")
    assert '"status": "error"' in capsys.readouterr().out


def test_operations(monkeypatch):
    calls = []
    def fake_run(client, operation, request_id, sql, params=(), mode=None):
        calls.append((client, operation, sql, params, mode))
        if operation == "login_lookup":
            return {"password_hash": "hashed"}
        if operation.startswith("dashboard"):
            return [{"label": "x", "value": 1}]
        return {"id": 1} if mode == "one" else [{"id": 1}] if mode == "all" else None
    monkeypatch.setattr(db, "run", fake_run)
    db.initialize("user", "hash", "req")
    assert db.user_hash("web", "req", "user") == "hashed"
    record = {"title": "t", "url": "https://e", "category": "c", "creator": "a", "duration_minutes": 1, "active": True}
    for client in ("web", "cli"):
        assert db.list_records(client, "req", {"title": "t", "category": "c", "creator": "a"}, page=2, sort="title", direction="desc")
        assert db.list_records(client, "req", {}, all_rows=True)
        assert db.create_record(client, "req", record)
        assert db.update_record(client, "req", 1, record)
        assert db.delete_record(client, "req", 1)
        assert db.set_status(client, "req", 1, False)
        assert db.duplicate(client, "req", 1)
        assert db.dashboard(client, "req")["categories"][0]["value"] == 1
    assert any("OFFSET" in call[2] for call in calls)
    assert any(call[1] == "export" and "LIMIT" not in call[2] for call in calls)
    assert db.filters_sql("web", {})[0].startswith("SELECT")
    assert db.filters_sql("cli", {})[0].startswith("SELECT")
