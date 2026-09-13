#!/usr/bin/env python3
"""Serve local review HTML and persist one digest-bound form decision."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


class ReviewHandler(SimpleHTTPRequestHandler):
    server_version = "SynsReview/1"

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/decision":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length > 64_000:
            self.send_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        form = {k: v[-1] for k, v in parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True).items()}
        if not secrets.compare_digest(form.get("token", ""), self.server.token):  # type: ignore[attr-defined]
            self.send_error(HTTPStatus.FORBIDDEN, "Invalid or stale review token")
            return
        decision = form.get("decision", "").strip()
        allowed = self.server.allowed  # type: ignore[attr-defined]
        if not decision or decision not in allowed:
            self.send_error(HTTPStatus.BAD_REQUEST, "A valid decision is required; blank approves nothing")
            return
        record = {
            "decision": decision,
            "submitted_at": int(time.time()),
            "bound_digests": self.server.digests,  # type: ignore[attr-defined]
            "fields": {k: v for k, v in form.items() if k != "token"},
        }
        output = self.server.output  # type: ignore[attr-defined]
        tmp = output.with_suffix(output.suffix + ".tmp")
        tmp.write_text(json.dumps(record, indent=2) + "\n")
        os.chmod(tmp, 0o600)
        tmp.replace(output)
        body = b"<!doctype html><title>Decision recorded</title><p>Decision recorded. You may return to the agent.</p>"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        print(format % args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--page", default="structure-review.html")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--digests", type=Path, required=True, help="JSON object of approval-bound digests")
    parser.add_argument("--allowed", nargs="+", required=True)
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    token = secrets.token_urlsafe(24)
    page = args.directory / args.page
    raw = page.read_text()
    page.write_text(raw.replace("{{REVIEW_TOKEN}}", token))
    handler = lambda *a, **kw: ReviewHandler(*a, directory=str(args.directory), **kw)  # noqa: E731
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    server.token = token  # type: ignore[attr-defined]
    server.output = args.output  # type: ignore[attr-defined]
    server.digests = json.loads(args.digests.read_text())  # type: ignore[attr-defined]
    server.allowed = set(args.allowed)  # type: ignore[attr-defined]
    os.chmod(args.directory, 0o700)
    print(f"http://127.0.0.1:{server.server_port}/{args.page}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
