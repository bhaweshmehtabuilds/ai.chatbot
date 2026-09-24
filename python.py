import datetime
import json
import os
import urllib.request

from flask import Flask, jsonify, request

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(BASE_DIR, "api.gitignore")

app = Flask(__name__)


def load_api_key(path=KEY_FILE):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("sk-"):
                return line
    raise RuntimeError("No API key found in %s" % path)


def call_llm(messages, tools=None):
    payload = {"model": MODEL, "messages": messages}
    if tools:
        payload["tools"] = tools
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": "Bearer %s" % load_api_key(),
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]


def calculator(expression):
    allowed = set("0123456789+-*/(). %")
    if not set(expression) <= allowed:
        return "error: invalid characters"
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return "error: %s" % e


def get_time():
    return datetime.datetime.now().isoformat()


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a basic arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current local date and time.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

DISPATCH = {"calculator": calculator, "get_time": get_time}

SYSTEM_PROMPT = "You are a helpful agent. Use tools when needed. Be concise."

HISTORY = [{"role": "system", "content": SYSTEM_PROMPT}]


def run_agent(user_input, max_steps=5):
    global HISTORY
    HISTORY.append({"role": "user", "content": user_input})
    events = []
    for _ in range(max_steps):
        message = call_llm(HISTORY, TOOLS)
        HISTORY.append(message)
        tool_calls = message.get("tool_calls")
        if not tool_calls:
            return message.get("content", ""), events
        for call in tool_calls:
            name = call["function"]["name"]
            args = json.loads(call["function"].get("arguments") or "{}")
            result = DISPATCH[name](**args)
            events.append({"tool": name, "args": args, "result": str(result)})
            HISTORY.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": str(result),
            })
    return "max steps reached", events


@app.route("/")
def index():
    with open(os.path.join(BASE_DIR, "index.html")) as f:
        return f.read()


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "empty message"}), 400
    try:
        reply, events = run_agent(message)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"reply": reply, "events": events})


@app.route("/api/reset", methods=["POST"])
def reset():
    global HISTORY
    HISTORY = [{"role": "system", "content": SYSTEM_PROMPT}]
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
