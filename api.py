"""API REST para Web e CLI do catálogo de vídeos."""
import base64
import binascii
import csv
import hashlib
import hmac
import io
import json
import os
import secrets
import time
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, Response, g, jsonify, request

import db


app = Flask(__name__)
SECRET = secrets.token_bytes(32)


def log(client, operation, status, request_id, message):
    print(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "level": "INFO" if status == "success" else "WARN", "layer": "api", "client": client, "operation": operation, "status": status, "request_id": request_id, "message": message}), flush=True)


def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password, stored):
    if not stored:
        return False
    salt, expected = stored.split(":", 1)
    actual = hash_password(password, bytes.fromhex(salt)).split(":", 1)[1]
    return hmac.compare_digest(actual, expected)


def token_for(username):
    payload = base64.urlsafe_b64encode(f"{username}:{int(time.time()) + 86400}".encode()).decode().rstrip("=")
    signature = hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def valid_token(token):
    try:
        payload, signature = token.split(".", 1)
        expected = hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return False
        username, expiry = base64.urlsafe_b64decode(payload + "==").decode().rsplit(":", 1)
        return username == os.environ.get("APP_USERNAME", "admin") and int(expiry) > time.time()
    except (ValueError, UnicodeDecodeError, binascii.Error):
        return False


@app.before_request
def start_request():
    g.request_id = request.headers.get("X-Request-ID") or f"req-{secrets.token_hex(8)}"
    g.client = "cli" if request.path.startswith("/api/cli/") else "web"
    g.operation = request.endpoint or "unknown"


@app.after_request
def finish_request(response):
    log(g.client, g.operation, "success" if response.status_code < 400 else "error", g.request_id, f"HTTP {response.status_code}")
    response.headers["X-Request-ID"] = g.request_id
    return response


@app.errorhandler(Exception)
def handle_error(exc):
    app.logger.error("Erro de requisição: %s", type(exc).__name__)
    return jsonify(error="Erro interno"), 500


def protected(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if g.client == "cli":
            authorization = request.headers.get("Authorization", "")
            token = authorization[7:] if authorization.startswith("Bearer ") else ""
        else:
            token = request.cookies.get("session", "")
        if not valid_token(token):
            return jsonify(error="Autenticação necessária"), 401
        return function(*args, **kwargs)
    return wrapper


def validated(data):
    if not isinstance(data, dict):
        raise ValueError("Envie um objeto JSON")
    result = {}
    for key in ("title", "url", "category", "creator"):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Campo obrigatório: {key}")
        result[key] = value.strip()
    if not result["url"].startswith(("http://", "https://")):
        raise ValueError("URL deve começar com http:// ou https://")
    try:
        result["duration_minutes"] = int(data.get("duration_minutes", 0))
    except (TypeError, ValueError):
        raise ValueError("Duração deve ser um inteiro") from None
    if result["duration_minutes"] < 0:
        raise ValueError("Duração não pode ser negativa")
    if not isinstance(data.get("active", True), bool):
        raise ValueError("Status deve ser booleano")
    result["active"] = data.get("active", True)
    return result


@app.get("/api/web/health")
@app.get("/api/cli/health")
def health():
    return jsonify(status="ok")


@app.post("/api/web/login")
@app.post("/api/cli/token")
def login():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify(error="Credenciais inválidas"), 401
    username = data.get("username", "")
    password = data.get("password", "")
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify(error="Credenciais inválidas"), 401
    stored = db.user_hash(g.client, g.request_id, username)
    if not verify_password(password, stored):
        return jsonify(error="Credenciais inválidas"), 401
    token = token_for(username)
    if g.client == "cli":
        return jsonify(token=token)
    response = jsonify(message="Autenticado")
    response.set_cookie("session", token, httponly=True, samesite="Lax", max_age=86400)
    return response


def filters():
    return {key: request.args.get(key, "").strip() for key in ("title", "category", "creator")}


@app.get("/api/web/records")
@app.get("/api/cli/records")
@protected
def records_list():
    try:
        page = max(1, int(request.args.get("page", "1")))
    except ValueError:
        return jsonify(error="Página inválida"), 400
    rows = db.list_records(g.client, g.request_id, filters(), page, request.args.get("sort", "id"), request.args.get("direction", "asc"))
    return jsonify(items=rows[:5], page=page, has_next=len(rows) > 5)


@app.get("/api/web/records/search")
@app.get("/api/cli/records/search")
@protected
def records_search():
    return records_list.__wrapped__()


@app.post("/api/web/records")
@app.post("/api/cli/records")
@protected
def records_create():
    try:
        data = validated(request.get_json(silent=True))
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(db.create_record(g.client, g.request_id, data)), 201


@app.put("/api/web/records/<int:record_id>")
@app.put("/api/cli/records/<int:record_id>")
@protected
def records_update(record_id):
    try:
        data = validated(request.get_json(silent=True))
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    row = db.update_record(g.client, g.request_id, record_id, data)
    return jsonify(row) if row else (jsonify(error="Registro não encontrado"), 404)


@app.delete("/api/web/records/<int:record_id>")
@app.delete("/api/cli/records/<int:record_id>")
@protected
def records_delete(record_id):
    row = db.delete_record(g.client, g.request_id, record_id)
    return ("", 204) if row else (jsonify(error="Registro não encontrado"), 404)


@app.patch("/api/web/records/<int:record_id>/status")
@app.patch("/api/cli/records/<int:record_id>/status")
@protected
def records_status(record_id):
    data = request.get_json(silent=True) or {}
    if not isinstance(data.get("active"), bool):
        return jsonify(error="Status deve ser booleano"), 400
    row = db.set_status(g.client, g.request_id, record_id, data["active"])
    return jsonify(row) if row else (jsonify(error="Registro não encontrado"), 404)


@app.post("/api/web/records/<int:record_id>/duplicate")
@app.post("/api/cli/records/<int:record_id>/duplicate")
@protected
def records_duplicate(record_id):
    row = db.duplicate(g.client, g.request_id, record_id)
    return (jsonify(row), 201) if row else (jsonify(error="Registro não encontrado"), 404)


@app.get("/api/web/records/export")
@app.get("/api/cli/records/export")
@protected
def records_export():
    rows = db.list_records(g.client, g.request_id, filters(), all_rows=True)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=("id", "title", "url", "category", "creator", "duration_minutes", "active"))
    writer.writeheader()
    writer.writerows(rows)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=videos.csv"})


@app.get("/api/web/dashboard")
@app.get("/api/cli/dashboard")
@protected
def dashboard():
    return jsonify(db.dashboard(g.client, g.request_id))


if __name__ == "__main__":  # pragma: no cover - inicialização validada via Compose
    db.initialize(os.environ.get("APP_USERNAME", "admin"), hash_password(os.environ["APP_PASSWORD"]), "startup")
    app.run(host="0.0.0.0", port=5000)
