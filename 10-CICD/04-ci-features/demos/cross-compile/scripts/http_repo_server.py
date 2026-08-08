"""Minimal HTTP firmware repo: GET download + PUT upload (demo only)."""
from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class FirmwareRepoHandler(SimpleHTTPRequestHandler):
    def do_PUT(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        rel = self.path.lstrip("/")
        if not rel or ".." in rel:
            self.send_error(400, "bad path")
            return
        dest = Path(self.directory) / rel  # type: ignore[attr-defined]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(self.rfile.read(length))
        self.send_response(201)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(f"stored {rel} ({length} bytes)\n".encode())

    def log_message(self, fmt: str, *args) -> None:
        print("[http-repo]", fmt % args)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default="http_repo")
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args()
    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)

    class Handler(FirmwareRepoHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(root), **kw)

    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Firmware HTTP repo: http://127.0.0.1:{args.port}/  (root={root})")
    print("Board/test bench would: curl -O http://.../fw-<sha>.bin then flash.")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
