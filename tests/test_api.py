import json

import pytest

import api


RECORD = {"id": 1, "title": "Vídeo", "url": "https://example.com/v", "category": "Música", "creator": "Canal", "duration_minutes": 4, "active": True}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("APP_USERNAME", "test")
    monkeypatch.setattr(api.db, "user_hash", lambda *args: api.hash_password("senha"))
    monkeypatch.setattr(api.db, "list_records", lambda *args, **kwargs: [RECORD])
    monkeypatch.setattr(api.db, "create_record", lambda *args: RECORD)
    monkeypatch.setattr(api.db, "update_record", lambda *args: RECORD if args[2] == 1 else None)
    monkeypatch.setattr(api.db, "delete_record", lambda *args: {"id": 1} if args[2] == 1 else None)
    monkeypatch.setattr(api.db, "set_status", lambda *args: RECORD if args[2] == 1 else None)
    monkeypatch.setattr(api.db, "duplicate", lambda *args: RECORD if args[2] == 1 else None)
    monkeypatch.setattr(api.db, "dashboard", lambda *args: {"categories": [{"label": "Música", "value": 1}], "statuses": [], "creators": []})
    return api.app.test_client()


def test_health_login_and_authentication(client):
    assert client.get("/api/web/health").status_code == 200
    assert client.get("/api/cli/health").status_code == 200
    assert client.get("/api/web/records").status_code == 401
    assert client.get("/api/cli/dashboard").status_code == 401
    assert client.post("/api/web/login", json={"username": "test", "password": "wrong"}).status_code == 401
    assert client.post("/api/web/login", json=["invalid"]).status_code == 401
    assert client.post("/api/web/login", json={"username": 1, "password": "senha"}).status_code == 401
    assert client.post("/api/web/login", json={"username": "test", "password": "senha"}).status_code == 200
    assert client.get("/api/web/records").status_code == 200
    token = client.post("/api/cli/token", json={"username": "test", "password": "senha"}).json["token"]
    assert client.get("/api/cli/records", headers={"Authorization": "Bearer " + token}).status_code == 200
    assert client.get("/api/cli/records", headers={"Authorization": "Bearer x.y"}).status_code == 401


def test_all_record_routes(client):
    client.post("/api/web/login", json={"username": "test", "password": "senha"})
    assert client.get("/api/web/records/search?title=x&category=y&creator=z&page=2&sort=title&direction=desc").status_code == 200
    assert client.get("/api/web/records?page=x").status_code == 400
    assert client.post("/api/web/records", json=RECORD).status_code == 201
    assert client.post("/api/web/records", json={}).status_code == 400
    assert client.put("/api/web/records/1", json=RECORD).status_code == 200
    assert client.put("/api/web/records/2", json=RECORD).status_code == 404
    assert client.put("/api/web/records/1", json={}).status_code == 400
    assert client.delete("/api/web/records/1").status_code == 204
    assert client.delete("/api/web/records/2").status_code == 404
    assert client.patch("/api/web/records/1/status", json={"active": False}).status_code == 200
    assert client.patch("/api/web/records/2/status", json={"active": False}).status_code == 404
    assert client.patch("/api/web/records/1/status", json={"active": "no"}).status_code == 400
    assert client.post("/api/web/records/1/duplicate").status_code == 201
    assert client.post("/api/web/records/2/duplicate").status_code == 404
    assert "Vídeo" in client.get("/api/web/records/export?category=Música").text
    assert client.get("/api/web/dashboard").json["categories"][0]["value"] == 1


def test_cli_routes_and_errors(client):
    token = client.post("/api/cli/token", json={"username": "test", "password": "senha"}).json["token"]
    headers = {"Authorization": "Bearer " + token}
    assert client.post("/api/cli/records", json=RECORD, headers=headers).status_code == 201
    assert client.put("/api/cli/records/1", json=RECORD, headers=headers).status_code == 200
    assert client.get("/api/cli/records/search", headers=headers).status_code == 200
    assert client.get("/api/cli/records/export", headers=headers).status_code == 200
    assert client.get("/api/cli/dashboard", headers=headers).status_code == 200
    assert client.patch("/api/cli/records/1/status", json={"active": True}, headers=headers).status_code == 200
    assert client.post("/api/cli/records/1/duplicate", headers=headers).status_code == 201
    assert client.delete("/api/cli/records/1", headers=headers).status_code == 204
    assert client.post("/api/cli/records", json={}, headers=headers).status_code == 400


@pytest.mark.parametrize("payload", [None, {}, {**RECORD, "url": "bad"}, {**RECORD, "duration_minutes": "bad"}, {**RECORD, "duration_minutes": -1}, {**RECORD, "active": "yes"}])
def test_validation_rejects_invalid_payload(payload):
    with pytest.raises(ValueError):
        api.validated(payload)


def test_token_and_password_edges(monkeypatch):
    monkeypatch.setenv("APP_USERNAME", "test")
    assert not api.verify_password("x", None)
    assert api.verify_password("senha", api.hash_password("senha"))
    assert not api.valid_token("")
    assert not api.valid_token("bad.token")
    assert api.valid_token(api.token_for("test"))
    assert api.validated(RECORD)["duration_minutes"] == 4


def test_internal_error_is_generic(client, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("secret text")
    monkeypatch.setattr(api.db, "user_hash", fail)
    response = client.post("/api/web/login", json={"username": "test", "password": "senha"})
    assert response.status_code == 500
    assert b"secret text" not in response.data
