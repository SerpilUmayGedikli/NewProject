from __future__ import annotations

import json
import mimetypes
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import os

BASE_DIR = Path(__file__).resolve().parent
SITE_DIR = BASE_DIR / "site"
STATIC_DIR = BASE_DIR / "static"
RUNTIME_DIR = BASE_DIR / "runtime"
RUNTIME_DIR.mkdir(exist_ok=True)
AGENT_LOG_FILE = RUNTIME_DIR / "agent_logs.json"

executor = ThreadPoolExecutor(max_workers=20)
active_agents: dict[str, dict] = {}
chats: dict[str, dict] = {}
lock = threading.Lock()

DEFAULT_AGENTS = [
    {"id": "claude", "name": "Claude", "role": "Analyst"},
    {"id": "chatgpt", "name": "ChatGPT", "role": "Generalist"},
    {"id": "gemini", "name": "Gemini", "role": "Researcher"},
]


def _count_tokens(text: str) -> int:
    return max(1, len(text.split()))


def _read_logs() -> list[dict]:
    if not AGENT_LOG_FILE.exists():
        return []
    return json.loads(AGENT_LOG_FILE.read_text(encoding="utf-8"))


def _persist_log(entry: dict) -> None:
    logs = _read_logs()
    logs.append(entry)
    AGENT_LOG_FILE.write_text(json.dumps(logs[-500:], ensure_ascii=False, indent=2), encoding="utf-8")


def _run_agent(agent_id: str, prompt: str) -> None:
    with lock:
        active_agents[agent_id]["status"] = "running"
    time.sleep(0.8)
    output = f"{agent_id} processed: {prompt[:80]}"
    _persist_log(
        {
            "timestamp": time.time(),
            "agent_id": agent_id,
            "prompt": prompt,
            "output": output,
            "tokens": _count_tokens(prompt) + _count_tokens(output),
            "latency_sec": 0.8,
        }
    )
    with lock:
        active_agents[agent_id]["status"] = "idle"
        active_agents[agent_id]["last_output"] = output


def _chat_reply(chat_id: str, message: str) -> None:
    time.sleep(0.7)
    with lock:
        chat = chats.get(chat_id)
        if not chat or chat.get("paused"):
            return
        agent_id = chat["agent_id"]
        reply_text = f"{agent_id} yanıtı: {message[:120]}"
        reply = {
            "sender": agent_id,
            "text": reply_text,
            "ts": time.time(),
        }
        chat["messages"].append(reply)
        chat["tokens_total"] += _count_tokens(reply_text)
        chat["status"] = "idle"


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict | list, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        data = file_path.read_bytes()
        ctype = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_body_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b"{}"
        return json.loads(body.decode("utf-8"))

    def _chat_action(self, chat_id: str, action: str) -> tuple[dict, int]:
        with lock:
            chat = chats.get(chat_id)
            if not chat:
                return {"ok": False, "error": "chat not found"}, HTTPStatus.NOT_FOUND
            if action == "pause":
                chat["paused"] = True
                chat["status"] = "paused"
            elif action == "resume":
                chat["paused"] = False
                chat["status"] = "idle"
            elif action == "delete":
                del chats[chat_id]
                return {"ok": True}, HTTPStatus.OK
            return {"ok": True, "chat": chat}, HTTPStatus.OK

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            return self._send_file(SITE_DIR / "index.html")
        if path == "/logs":
            return self._send_file(SITE_DIR / "logs.html")
        if path == "/analytics":
            return self._send_file(SITE_DIR / "analytics.html")
        if path.startswith("/static/"):
            rel = path.removeprefix("/static/")
            return self._send_file(STATIC_DIR / rel)

        if path == "/api/agents/status":
            with lock:
                return self._send_json(active_agents)
        if path == "/api/logs":
            return self._send_json(_read_logs())
        if path == "/api/metrics":
            logs = _read_logs()
            total_tokens = sum(item["tokens"] for item in logs)
            avg_latency = sum(item["latency_sec"] for item in logs) / len(logs) if logs else 0
            by_agent: dict[str, int] = {}
            for item in logs:
                by_agent[item["agent_id"]] = by_agent.get(item["agent_id"], 0) + 1
            return self._send_json({"total_runs": len(logs), "total_tokens": total_tokens, "avg_latency": avg_latency, "by_agent": by_agent})
        if path == "/api/chats":
            with lock:
                return self._send_json(list(chats.values()))

        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/agents/start":
            payload = self._read_body_json()
            prompt = payload.get("prompt", "Sample mission")
            agents = payload.get("agents", DEFAULT_AGENTS)

            with lock:
                for agent in agents:
                    active_agents[agent["id"]] = {
                        "name": agent["name"],
                        "role": agent.get("role", "generalist"),
                        "status": "queued",
                        "last_output": "",
                    }

            for agent in agents:
                executor.submit(_run_agent, agent["id"], prompt)

            return self._send_json({"ok": True, "active_count": len(active_agents)})

        if path == "/api/chats/start":
            payload = self._read_body_json()
            agent_id = payload.get("agent_id", "chatgpt")
            title = payload.get("title", f"Yeni Sohbet - {agent_id}")
            chat_id = str(uuid.uuid4())[:8]
            with lock:
                chats[chat_id] = {
                    "chat_id": chat_id,
                    "agent_id": agent_id,
                    "title": title,
                    "status": "idle",
                    "paused": False,
                    "tokens_total": 0,
                    "messages": [],
                    "created_at": time.time(),
                }
            return self._send_json(chats[chat_id], HTTPStatus.CREATED)

        if path == "/api/chats/message":
            payload = self._read_body_json()
            chat_id = payload.get("chat_id", "")
            message = payload.get("message", "")
            if not message or chat_id not in chats:
                return self._send_json({"ok": False, "error": "invalid chat or empty message"}, HTTPStatus.BAD_REQUEST)

            with lock:
                if chats[chat_id].get("paused"):
                    return self._send_json({"ok": False, "error": "chat paused"}, HTTPStatus.CONFLICT)
                chats[chat_id]["messages"].append({"sender": "user", "text": message, "ts": time.time()})
                chats[chat_id]["tokens_total"] += _count_tokens(message)
                chats[chat_id]["status"] = "running"

            executor.submit(_chat_reply, chat_id, message)
            return self._send_json({"ok": True})

        if path in ("/api/chats/pause", "/api/chats/resume", "/api/chats/delete"):
            payload = self._read_body_json()
            chat_id = payload.get("chat_id", "")
            action = path.rsplit("/", 1)[-1]
            result, status = self._chat_action(chat_id, action)
            return self._send_json(result, status)

        self.send_error(HTTPStatus.NOT_FOUND)


def run(host: str | None = None, port: int | None = None) -> None:
    bind_host = host or os.environ.get("HOST", "0.0.0.0")
    bind_port = port or int(os.environ.get("PORT", "5000"))
    server = ThreadingHTTPServer((bind_host, bind_port), Handler)
    print(f"Server started on {bind_host}:{bind_port}")
    if bind_host == "0.0.0.0":
        print(f"Open locally: http://127.0.0.1:{bind_port}")
        print(f"Open via localhost: http://localhost:{bind_port}")
    else:
        print(f"Open: http://{bind_host}:{bind_port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
