from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import datetime
import json
import requests
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# -----------------------------------------
# TOOLS
# -----------------------------------------

def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def web_search(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    r = requests.get(url).json()
    results = []
    if "RelatedTopics" in r:
        for item in r["RelatedTopics"][:3]:
            if "Text" in item:
                results.append(item["Text"])
    return results if results else ["No results found"]

TOOLS = [
    {
        "name": "get_time",
        "description": "Returns the current server time",
        "parameters": {
            "type": "object",
            "properties": {}
        },
    },
    {
        "name": "web_search",
        "description": "Searches the web and returns results",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
]


SYSTEM_PROMPT = """
You are an AI agent. When asked:
- time → use get_time
- search/info/google/news → use web_search
Otherwise answer yourself.
"""


@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ],
        tools=TOOLS
    )

    msg = response.choices[0].message

    if msg.get("tool_calls"):
        tool = msg["tool_calls"][0]
        name = tool["function"]["name"]
        args = json.loads(tool["function"].get("arguments", "{}"))

        if name == "get_time":
            return jsonify({"reply": get_time()})

        if name == "web_search":
            return jsonify({"reply": web_search(args["query"])})

    return jsonify({"reply": msg["content"]})

@app.route("/")
def home():
    return "🚀 Agent backend running!"

if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", 5000)), host="0.0.0.0")
