"""Cliente de terminal para a API do catálogo de vídeos."""
import argparse
import getpass
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def call(path, method="GET", payload=None, token=None):
    base = os.environ.get("API_URL", "http://api:5000")
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(base + "/api/cli/" + path, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=20) as response:
            body = response.read()
            return body.decode() if path.startswith("records/export") else json.loads(body) if body else {}
    except HTTPError as exc:
        message = exc.read().decode()
        raise RuntimeError(f"HTTP {exc.code}: {message}") from None
    except URLError as exc:
        raise RuntimeError(f"API indisponível: {exc.reason}") from None


def record_payload(args):
    return {key: getattr(args, key) for key in ("title", "url", "category", "creator", "duration_minutes")}


def query(args):
    values = {key: getattr(args, key) for key in ("title", "category", "creator", "page", "sort", "direction") if getattr(args, key, None) is not None}
    return "?" + urlencode(values) if values else ""


def parser():
    root = argparse.ArgumentParser(description="Catálogo de vídeos via API REST")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("health", help="Verifica a API")
    token = commands.add_parser("token", help="Obtém um Bearer token")
    token.add_argument("username")
    for name in ("list", "search", "export"):
        command = commands.add_parser(name)
        for key in ("title", "category", "creator"):
            command.add_argument(f"--{key}")
        if name != "export":
            command.add_argument("--page", type=int, default=1)
            command.add_argument("--sort", choices=("id", "title", "category", "creator", "duration_minutes"), default="id")
            command.add_argument("--direction", choices=("asc", "desc"), default="asc")
        else:
            command.add_argument("--output", default="/exports/videos.csv")
    for name in ("create", "update"):
        command = commands.add_parser(name)
        if name == "update":
            command.add_argument("id", type=int)
        for key in ("title", "url", "category", "creator"):
            command.add_argument(f"--{key}", required=True)
        command.add_argument("--duration-minutes", type=int, default=0)
        command.add_argument("--inactive", action="store_true")
    for name in ("delete", "activate", "deactivate", "duplicate"):
        commands.add_parser(name).add_argument("id", type=int)
    commands.add_parser("dashboard")
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "health":
            result = call("health")
        elif args.command == "token":
            result = call("token", "POST", {"username": args.username, "password": getpass.getpass("Senha: ")})
        else:
            token = os.environ.get("VIDEO_TOKEN", "")
            if args.command in ("list", "search", "export"):
                path = "records/search" if args.command == "search" else "records/export" if args.command == "export" else "records"
                result = call(path + query(args), token=token)
                if args.command == "export":
                    output = Path(args.output)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text(result, encoding="utf-8")
                    result = {"file": str(output)}
            elif args.command in ("create", "update"):
                data = record_payload(args)
                data["active"] = not args.inactive
                result = call("records" + (f"/{args.id}" if args.command == "update" else ""), "PUT" if args.command == "update" else "POST", data, token)
            elif args.command == "delete":
                result = call(f"records/{args.id}", "DELETE", token=token)
            elif args.command in ("activate", "deactivate"):
                result = call(f"records/{args.id}/status", "PATCH", {"active": args.command == "activate"}, token)
            elif args.command == "duplicate":
                result = call(f"records/{args.id}/duplicate", "POST", token=token)
            else:
                result = call("dashboard", token=token)
                for key, heading in (("categories", "Por categoria"), ("statuses", "Por status"), ("creators", "Por criador")):
                    print(heading + ":")
                    for item in result[key]:
                        print(f"  {item['label']}: {item['value']}")
                return 0
        print(json.dumps(result, ensure_ascii=False, indent=2) if not isinstance(result, str) else result)
        return 0
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover - executado via Compose
    raise SystemExit(main())
