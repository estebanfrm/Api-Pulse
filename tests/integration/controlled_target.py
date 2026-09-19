from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from urllib.parse import parse_qs, urlparse


HOST = "0.0.0.0"
PORT = 8080


class ControlledTargetHandler(BaseHTTPRequestHandler):
    server_version = "ApiPulseControlledTarget/1.0"

    def do_GET(self) -> None:
        self._handle_request()

    def do_POST(self) -> None:
        self._handle_request()

    def do_PUT(self) -> None:
        self._handle_request()

    def do_DELETE(self) -> None:
        self._handle_request()

    def log_message(self, format: str, *args: object) -> None:
        return

    def _handle_request(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send_json(200, {"status": "ok", "target": "controlled"})
            return

        if parsed.path == "/redirect":
            self.send_response(302)
            self.send_header("Content-Type", "application/json")
            self.send_header("Location", "/echo")
            self.end_headers()
            self.wfile.write(b'{"redirect":"not followed"}')
            return

        if parsed.path.startswith("/status/"):
            try:
                status_code = int(parsed.path.removeprefix("/status/"))
            except ValueError:
                status_code = 400
            self._send_json(
                status_code,
                {"controlled": True, "method": self.command, "status": status_code},
            )
            return

        if parsed.path != "/echo":
            self._send_json(404, {"controlled": True, "message": "Not found"})
            return

        payload = self._read_json_body()
        status_code = 201 if self.command == "POST" else 200
        self._send_json(
            status_code,
            {
                "controlled": True,
                "method": self.command,
                "path": parsed.path,
                "query": parse_qs(parsed.query),
                "json": payload,
                "test_header": self.headers.get("X-Api-Pulse-Test"),
            },
        )

    def _read_json_body(self) -> object | None:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length == 0:
            return None
        raw_body = self.rfile.read(content_length)
        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            return {"invalid_json": raw_body.decode("utf-8", errors="replace")}

    def _send_json(self, status_code: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), ControlledTargetHandler)
    server.serve_forever()
