from io import BytesIO
from urllib.error import HTTPError, URLError

import cli


class Response:
    def __init__(self, value):
        self.value = value
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self):
        return self.value


def test_http_calls(monkeypatch):
    monkeypatch.setenv("API_URL", "http://api")
    requests = []
    def open_request(request, timeout):
        requests.append(request)
        return Response(b'{"status":"ok"}')
    monkeypatch.setattr(cli, "urlopen", open_request)
    assert cli.call("health")["status"] == "ok"
    assert cli.call("records", "POST", {"title": "test"}, "secret")["status"] == "ok"
    assert requests[-1].get_header("Authorization") == "Bearer secret"
    monkeypatch.setattr(cli, "urlopen", lambda *args, **kwargs: Response("id,title\n1,Vídeo\n".encode()))
    assert cli.call("records/export?title=V").startswith("id,title")
    monkeypatch.setattr(cli, "urlopen", lambda *args, **kwargs: Response(b""))
    assert cli.call("records/1", "DELETE") == {}


def test_http_errors(monkeypatch):
    def http_error(*args, **kwargs):
        raise HTTPError("url", 401, "Unauthorized", {}, BytesIO(b"unauthorized"))
    monkeypatch.setattr(cli, "urlopen", http_error)
    try:
        cli.call("records")
        assert False
    except RuntimeError as exc:
        assert "HTTP 401" in str(exc)
    monkeypatch.setattr(cli, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(URLError("offline")))
    try:
        cli.call("records")
        assert False
    except RuntimeError as exc:
        assert "indisponível" in str(exc)


def test_commands(monkeypatch, tmp_path, capsys):
    calls = []
    def fake_call(path, method="GET", payload=None, token=None):
        calls.append((path, method, payload, token))
        if path == "dashboard":
            return {"categories": [{"label": "Música", "value": 1}], "statuses": [], "creators": []}
        return "id,title\n1,Video\n" if path.startswith("records/export") else {"ok": True}
    monkeypatch.setattr(cli, "call", fake_call)
    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt: "senha")
    monkeypatch.setenv("VIDEO_TOKEN", "token")
    assert cli.main(["health"]) == 0
    assert cli.main(["token", "admin"]) == 0
    assert cli.main(["list", "--page", "2", "--sort", "title", "--direction", "desc"]) == 0
    assert cli.main(["search", "--title", "V", "--category", "M", "--creator", "C"]) == 0
    fields = ["--title", "V", "--url", "https://example.com", "--category", "M", "--creator", "C"]
    assert cli.main(["create", *fields, "--inactive"]) == 0
    assert cli.main(["update", "1", *fields]) == 0
    assert cli.main(["delete", "1"]) == 0
    assert cli.main(["activate", "1"]) == 0
    assert cli.main(["deactivate", "1"]) == 0
    assert cli.main(["duplicate", "1"]) == 0
    assert cli.main(["dashboard"]) == 0
    target = tmp_path / "videos.csv"
    assert cli.main(["export", "--output", str(target)]) == 0
    assert target.read_text(encoding="utf-8").startswith("id,title")
    assert any(call[0].startswith("records/search") for call in calls)
    assert any(call[1] == "PATCH" for call in calls)
    assert '"ok": true' in capsys.readouterr().out
    monkeypatch.setattr(cli, "call", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("failed")))
    assert cli.main(["health"]) == 1
    assert "failed" in capsys.readouterr().err
