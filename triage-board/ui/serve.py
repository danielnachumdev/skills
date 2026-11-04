#!/usr/bin/env python3
"""Tiny local server for triage-board UIs."""

from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8765


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self) -> None:
        routes = {
            "/api/submit": ("decisions.json", "count"),
            "/api/submit-renames": ("rename-decisions.json", "rename_count"),
        }
        if self.path not in routes:
            self.send_error(404, "Not found")
            return
        filename, count_key = routes[self.path]
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        repos = data.get("repos")
        if not isinstance(repos, list):
            self.send_error(400, "Missing repos list")
            return
        out = ROOT / filename
        out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        rename_count = sum(1 for r in repos if r.get("will_rename"))
        payload = {"ok": True, "path": str(out), "count": len(repos), "rename_count": rename_count}
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[triage] {self.address_string()} {fmt % args}")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Decision board: http://{HOST}:{PORT}/")
    print(f"Rename board:   http://{HOST}:{PORT}/rename.html")
    print(f"Serving {ROOT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
