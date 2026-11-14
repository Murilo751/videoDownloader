"""Acesso PostgreSQL do catálogo de vídeos."""
import json
import os
from datetime import datetime, timezone

import psycopg
from psycopg.rows import dict_row


FIELDS = "id, title, url, category, creator, duration_minutes, active"
WEB_SELECT = f"SELECT {FIELDS} FROM records WHERE TRUE"
CLI_SELECT = f"SELECT {FIELDS} FROM records WHERE TRUE"
WEB_SQL = {
    "user": "SELECT password_hash FROM users WHERE username = %s",
    "create": f"INSERT INTO records (title,url,category,creator,duration_minutes,active) VALUES (%s,%s,%s,%s,%s,%s) RETURNING {FIELDS}",
    "update": f"UPDATE records SET title=%s,url=%s,category=%s,creator=%s,duration_minutes=%s,active=%s WHERE id=%s RETURNING {FIELDS}",
    "delete": "DELETE FROM records WHERE id=%s RETURNING id",
    "status": f"UPDATE records SET active=%s WHERE id=%s RETURNING {FIELDS}",
    "duplicate": f"INSERT INTO records (title,url,category,creator,duration_minutes,active) SELECT title,url,category,creator,duration_minutes,active FROM records WHERE id=%s RETURNING {FIELDS}",
    "categories": "SELECT category AS label, COUNT(*) AS value FROM records GROUP BY category ORDER BY category",
    "statuses": "SELECT CASE WHEN active THEN 'Ativo' ELSE 'Inativo' END AS label, COUNT(*) AS value FROM records GROUP BY active ORDER BY active",
    "creators": "SELECT creator AS label, COUNT(*) AS value FROM records GROUP BY creator ORDER BY creator",
}
CLI_SQL = {
    "user": "SELECT password_hash FROM users WHERE username = %s",
    "create": f"INSERT INTO records (title,url,category,creator,duration_minutes,active) VALUES (%s,%s,%s,%s,%s,%s) RETURNING {FIELDS}",
    "update": f"UPDATE records SET title=%s,url=%s,category=%s,creator=%s,duration_minutes=%s,active=%s WHERE id=%s RETURNING {FIELDS}",
    "delete": "DELETE FROM records WHERE id=%s RETURNING id",
    "status": f"UPDATE records SET active=%s WHERE id=%s RETURNING {FIELDS}",
    "duplicate": f"INSERT INTO records (title,url,category,creator,duration_minutes,active) SELECT title,url,category,creator,duration_minutes,active FROM records WHERE id=%s RETURNING {FIELDS}",
    "categories": "SELECT category AS label, COUNT(*) AS value FROM records GROUP BY category ORDER BY category",
    "statuses": "SELECT CASE WHEN active THEN 'Ativo' ELSE 'Inativo' END AS label, COUNT(*) AS value FROM records GROUP BY active ORDER BY active",
    "creators": "SELECT creator AS label, COUNT(*) AS value FROM records GROUP BY creator ORDER BY creator",
}


def sql_for(client, name):
    return (WEB_SQL if client == "web" else CLI_SQL)[name]


def log(client, operation, status, request_id, message):
    print(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "level": "INFO" if status == "success" else "ERROR", "layer": "db", "client": client, "operation": operation, "status": status, "request_id": request_id, "message": message}), flush=True)


def connection():
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)


def run(client, operation, request_id, sql, params=(), mode=None):
    try:
        with connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchone() if mode == "one" else cursor.fetchall() if mode == "all" else None
        log(client, operation, "success", request_id, "Consulta concluída")
        return result
    except Exception:
        log(client, operation, "error", request_id, "Falha no acesso a dados")
        raise


def initialize(username, password_hash, request_id):
    run("web", "schema", request_id, "CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT NOT NULL)")
    run("web", "schema", request_id, "CREATE TABLE IF NOT EXISTS records (id BIGSERIAL PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL, category TEXT NOT NULL, creator TEXT NOT NULL, duration_minutes INTEGER NOT NULL DEFAULT 0, active BOOLEAN NOT NULL DEFAULT TRUE)")
    run("web", "seed_user", request_id, "INSERT INTO users (username, password_hash) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING", (username, password_hash))


def user_hash(client, request_id, username):
    row = run(client, "login_lookup", request_id, sql_for(client, "user"), (username,), "one")
    return row["password_hash"] if row else None


def filters_sql(client, filters):
    sql = WEB_SELECT if client == "web" else CLI_SELECT
    values = []
    for key in ("title", "category", "creator"):
        if filters.get(key):
            sql += f" AND {key} ILIKE %s"
            values.append(f"%{filters[key]}%")
    return sql, values


def list_records(client, request_id, filters, page=1, sort="id", direction="asc", all_rows=False):
    sql, values = filters_sql(client, filters)
    sort = sort if sort in {"id", "title", "category", "creator", "duration_minutes"} else "id"
    direction = "DESC" if direction == "desc" else "ASC"
    sql += f" ORDER BY {sort} {direction}, id ASC"
    if not all_rows:
        sql += " LIMIT 6 OFFSET %s"
        values.append((page - 1) * 5)
    return run(client, "list" if not all_rows else "export", request_id, sql, values, "all")


def create_record(client, request_id, data):
    values = tuple(data[key] for key in ("title", "url", "category", "creator", "duration_minutes", "active"))
    return run(client, "insert", request_id, sql_for(client, "create"), values, "one")


def update_record(client, request_id, record_id, data):
    values = tuple(data[key] for key in ("title", "url", "category", "creator", "duration_minutes", "active")) + (record_id,)
    return run(client, "update", request_id, sql_for(client, "update"), values, "one")


def delete_record(client, request_id, record_id):
    return run(client, "delete", request_id, sql_for(client, "delete"), (record_id,), "one")


def set_status(client, request_id, record_id, active):
    return run(client, "status", request_id, sql_for(client, "status"), (active, record_id), "one")


def duplicate(client, request_id, record_id):
    return run(client, "duplicate", request_id, sql_for(client, "duplicate"), (record_id,), "one")


def dashboard(client, request_id):
    categories = run(client, "dashboard_categories", request_id, sql_for(client, "categories"), mode="all")
    statuses = run(client, "dashboard_status", request_id, sql_for(client, "statuses"), mode="all")
    creators = run(client, "dashboard_creators", request_id, sql_for(client, "creators"), mode="all")
    return {"categories": categories, "statuses": statuses, "creators": creators}
