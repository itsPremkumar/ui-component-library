"""Mock server for consumer development - simulates provider behavior based on contracts."""
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse


class MockServerHandler(BaseHTTPRequestHandler):
    """HTTP handler that matches requests against registered contract interactions."""

    interactions: dict = {}  # path -> list of (request_spec, response_spec)

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        self._handle_request("GET")

    def do_POST(self):
        self._handle_request("POST")

    def do_PUT(self):
        self._handle_request("PUT")

    def do_DELETE(self):
        self._handle_request("DELETE")

    def do_PATCH(self):
        self._handle_request("PATCH")

    def _handle_request(self, method: str):
        parsed = urlparse(self.path)
        path = parsed.path

        matched = None
        for req_spec, resp_spec in self.interactions.get(path, []):
            if req_spec.get("method", "").upper() == method:
                matched = resp_spec
                break

        if matched is None:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error = json.dumps({"error": f"No matching interaction for {method} {path}"})
            self.wfile.write(error.encode())
            return

        status = matched.get("status", 200)
        headers = matched.get("headers", {"Content-Type": "application/json"})
        body = matched.get("body", {})

        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()

        if body:
            if isinstance(body, (dict, list)):
                self.wfile.write(json.dumps(body).encode())
            else:
                self.wfile.write(str(body).encode())


class MockServer:
    """A mock HTTP server backed by Pact contract interactions."""

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._interactions: dict = {}

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def load_pact(self, pact_path: Path) -> int:
        """Load interactions from a Pact JSON file."""
        from pactnet.pact.io import PactReader

        reader = PactReader()
        contract = reader.read(pact_path)

        count = 0
        for interaction in contract.interactions:
            if interaction.request:
                path = interaction.request.get("path", "/")
                if path not in self._interactions:
                    self._interactions[path] = []
                self._interactions[path].append((interaction.request, interaction.response))
                count += 1

        MockServerHandler.interactions = self._interactions
        return count

    def add_interaction(
        self,
        method: str,
        path: str,
        request: dict,
        response: dict,
    ) -> None:
        """Add an interaction programmatically."""
        if path not in self._interactions:
            self._interactions[path] = []
        self._interactions[path].append((request, response))
        MockServerHandler.interactions = self._interactions

    def start(self) -> None:
        """Start the mock server in a background thread."""
        self._server = HTTPServer((self.host, self.port), MockServerHandler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the mock server."""
        if self._server:
            self._server.shutdown()
            self._server = None
            self._thread = None

    def reset(self) -> None:
        """Clear all registered interactions."""
        self._interactions.clear()
        MockServerHandler.interactions = {}

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
