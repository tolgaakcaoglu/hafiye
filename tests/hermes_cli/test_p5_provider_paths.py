"""P5 integration coverage for custom OpenAI-compatible providers."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

import yaml
from fastapi.testclient import TestClient

from hermes_cli.web_server import _SESSION_HEADER_NAME, _SESSION_TOKEN, app

_AUTH_HEADERS = {_SESSION_HEADER_NAME: _SESSION_TOKEN}


class _RemoteOpenAIHandler(BaseHTTPRequestHandler):
    server_version = "HafiyeP5Test/1.0"

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        if self.path != "/v1/models":
            self._send_json(404, {"error": "not found"})
            return
        if self.headers.get("Authorization") != "Bearer p5-remote-secret":
            self._send_json(401, {"error": "unauthorized"})
            return
        self._send_json(200, {"data": [{"id": "remote-model"}]})

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        if self.path != "/v1/chat/completions":
            self._send_json(404, {"error": "not found"})
            return
        if self.headers.get("Authorization") != "Bearer p5-remote-secret":
            self._send_json(401, {"error": "unauthorized"})
            return
        self._send_json(
            200,
            {
                "id": "p5-test-completion",
                "object": "chat.completion",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "P5_REMOTE_OK"},
                        "finish_reason": "stop",
                    }
                ],
            },
        )

    def log_message(self, _format: str, *_args) -> None:
        return


def test_remote_openai_endpoint_validation_and_save_uses_keyring(tmp_path: Path, monkeypatch):
    home = tmp_path / "hafiye"
    home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))

    server = ThreadingHTTPServer(("127.0.0.1", 0), _RemoteOpenAIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    client = TestClient(app)
    base_url = f"http://127.0.0.1:{server.server_port}/v1"

    try:
        validation = client.post(
            "/api/providers/custom-endpoints/validate",
            json={
                "id": "p5-remote",
                "name": "P5 Remote",
                "base_url": base_url,
                "model": "remote-model",
                "api_key": "p5-remote-secret",
            },
            headers=_AUTH_HEADERS,
        )
        assert validation.status_code == 200
        assert validation.json()["ok"] is True
        assert validation.json()["models"] == ["remote-model"]

        saved = client.post(
            "/api/providers/custom-endpoints",
            json={
                "id": "p5-remote",
                "name": "P5 Remote",
                "base_url": base_url,
                "model": "remote-model",
                "models": ["remote-model"],
                "api_key": "p5-remote-secret",
                "make_default": True,
            },
            headers=_AUTH_HEADERS,
        )
        assert saved.status_code == 200
        assert saved.json()["ok"] is True

        raw_config = yaml.safe_load((home / "config.yaml").read_text(encoding="utf-8"))
        provider = raw_config["providers"]["p5-remote"]
        assert provider["key_env"].startswith("HERMES_CUSTOM_")
        assert "api_key" not in provider
        assert raw_config["model"]["key_env"] == provider["key_env"]
        assert "p5-remote-secret" not in (home / "config.yaml").read_text(encoding="utf-8")

        request = Request(
            f"{base_url}/chat/completions",
            data=json.dumps(
                {
                    "model": "remote-model",
                    "messages": [{"role": "user", "content": "test"}],
                }
            ).encode("utf-8"),
            headers={
                "Authorization": "Bearer p5-remote-secret",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(request, timeout=5) as response:
            completion = json.load(response)
        assert completion["choices"][0]["message"]["content"] == "P5_REMOTE_OK"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
