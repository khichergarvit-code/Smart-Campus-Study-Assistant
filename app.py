"""
app.py
Web UI for the Smart Campus & Study Assistant.

Run:
    python app.py            -> opens http://127.0.0.1:8000 in the browser
    (on Windows you can also use:  py app.py)

It uses only the Python standard library (no Flask needed). The same modules
and intent detection from main.py are reused, so the CLI and the web UI
behave exactly the same.

How it works:
- The browser sends each message to POST /api/chat.
- The command runs in a worker thread. Anything the modules print() becomes a
  "block" (tables, timetable, moves), and speak() becomes a chat message.
- When a module needs more input (for example "will i pass" asks yes/no
  questions), the worker waits and the browser's next message is given to it.
"""

import json
import os
import queue
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from modules import speech, utilities
from main import detect_intent, handle, USER_NAME

PORT = int(os.environ.get("PORT", 8000))
UI_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "index.html")

# intent -> (feature label, algorithm) shown as a badge in the UI
BADGES = {
    "route": ("Campus Navigation", "A* / BFS / DFS / IDS"),
    "compare": ("Route Comparison", "A* vs BFS vs DFS vs IDS"),
    "timetable": ("Study Timetable", "Simulated Annealing / Hill Climbing"),
    "pass": ("Pass Predictor", "Bayesian Network"),
    "focus": ("Focus Tracker", "Hidden Markov Model"),
    "hanoi": ("Towers of Hanoi", "Recursion"),
    "puzzle": ("8 Puzzle", "A* + Manhattan distance"),
    "replan": ("Live Re-planning", "D* Lite"),
    "wumpus": ("Campus Escape (Wumpus World)", "Logical agent, model checking"),
    "em": ("Student Group Clustering", "EM algorithm (Gaussian mixture)"),
    "syllabus": ("Syllabus Coverage", "All lab topics"),
}


class Session:
    """One conversation. Runs each command in a thread so modules can ask questions."""

    def __init__(self):
        self.lock = threading.Lock()
        self.reset()

    def reset(self):
        self.events = []
        self.buf = ""
        self.inbox = queue.Queue()
        self.signal = queue.Queue()
        self.thread = None

    # --- output collected from the modules ---
    def write(self, text):
        self.buf += text

    def flush_block(self):
        if self.buf.strip():
            self.events.append({"type": "block", "text": self.buf.rstrip("\n")})
        self.buf = ""

    def emit(self, text):
        self.flush_block()
        self.events.append({"type": "text", "text": str(text)})

    # --- input requested by the modules ---
    def ask(self):
        self.flush_block()
        self.signal.put("wait")
        try:
            return self.inbox.get(timeout=300).strip().lower()
        except queue.Empty:
            return ""

    def _run(self, command):
        try:
            intent = detect_intent(command)
            if intent == "exit":
                self.emit("Goodbye, all the best for your exams!")
            else:
                self.emit(handle(intent, command, self.ask))
        except Exception as exc:  # never crash the server
            self.emit(f"Something went wrong: {exc}")
        self.flush_block()
        self.signal.put("done")

    def chat(self, message):
        with self.lock:
            self.events = []
            waiting = self.thread is not None and self.thread.is_alive()
            meta = {}
            if waiting:
                self.inbox.put(message)
            else:
                intent = detect_intent(message.lower())
                meta = {"intent": intent, "badge": BADGES.get(intent)}
                self.thread = threading.Thread(target=self._run, args=(message.lower(),), daemon=True)
                self.thread.start()
            try:
                state = self.signal.get(timeout=60)
            except queue.Empty:
                state = "done"
            return {"events": self.events, "waiting": state == "wait", **meta}


session = Session()


class Router:
    """Replaces sys.stdout so print() from the modules goes to the session."""

    def write(self, text):
        session.write(text)
        return len(text)

    def flush(self):
        pass


def fake_speak(text, voice_on=True):
    session.emit(text)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(UI_FILE, "rb") as f:
                self._send(200, f.read(), "text/html")
        elif self.path == "/api/hello":
            self._send(200, json.dumps({"text": utilities.greet(USER_NAME), "name": USER_NAME}))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            payload = {}
        if self.path == "/api/chat":
            message = str(payload.get("message", "")).strip()
            if not message:
                self._send(400, json.dumps({"error": "empty message"}))
                return
            self._send(200, json.dumps(session.chat(message)))
        elif self.path == "/api/reset":
            session.reset()
            self._send(200, json.dumps({"ok": True}))
        else:
            self._send(404, json.dumps({"error": "not found"}))


def main():
    speech.speak = fake_speak          # modules import speak() at call time
    sys.stdout = Router()
    server = None
    for port in range(PORT, PORT + 20):      # if the port is busy, try the next one
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if server is None:
        sys.stderr.write("Could not find a free port. Close other programs and try again.\n")
        return
    url = f"http://127.0.0.1:{server.server_address[1]}"
    sys.stderr.write(f"Smart Campus Assistant running at {url}  (Ctrl+C to stop)\n")
    if "--no-browser" not in sys.argv:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
