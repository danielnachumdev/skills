#!/usr/bin/env python3
"""Tiny local server for a triage-board UI (example under scripts/)."""

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
        if self.path != "/api/submit":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        items = data.get("items")
        if not isinstance(items, list):
            self.send_error(400, "Missing items list")
            return
        out = ROOT / "decisions.json"
        out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        payload = {"ok": True, "path": str(out), "count": len(items)}
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
    print(f"Serving {ROOT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
