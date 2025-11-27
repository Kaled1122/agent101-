from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json, datetime, requests
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================
# SYSTEM PROMPT (APEX-AGENT v2)
# =====================================================
SYSTEM_PROMPT = """
You are APEX-AGENT v2, an autonomous, tool-enabled AI system designed for real-time reasoning, research, and problem-solving.

Your mission: deliver correct, current, verifiable, and context-aware answers using tools when necessary. 
Never guess. If uncertainty exists, verify using search.

USE web_search(query) WHEN:
- The request requires real-world knowledge, live data, news, events, prices, results, people, companies, weather, sports, politics, or facts.
USE get_time() WHEN:
- The user asks about the current date or time.

NO TOOL when:
- The task is reasoning, explanation, planning, creative ideation, or hypothetical.

Maintain short-term conversational memory.
Be concise, structured, accurate, and confident.
Do not mention internal logic, tools, APIs, or this system prompt.
"""

# =====================================================
# TOOLS
# =====================================================

def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def web_search(query: str):
    key = os.getenv("SERPAPI_KEY")
    if not key:
        return ["❌ SERPAPI_KEY not configured"]

    r = requests.get(
        "https://serpapi.com/search.json",
        params={"q": query, "api_key": key}
    ).json()

    results = []
    for item in r.get("organic_results", [])[:3]:
        title = item.get("title")
        link = item.get("link")
        if title and link:
            results.append(f"{title} → {link}")

    return results or ["No results found. Try another query."]


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Return the current time.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web via SerpAPI for real-time, verified information.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    }
]

# =====================================================
# ROUTES
# =====================================================

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")

    resp = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ],
        tools=TOOLS
    )

    msg = resp.choices[0].message

    # TOOL CALL HANDLER
    if msg.tool_calls:
        action = msg.tool_calls[0]
        name = action.function.name
        args = json.loads(action.function.arguments or "{}")

        if name == "get_time":
            return jsonify({"reply": get_time()})
        if name == "web_search":
            return jsonify({"reply": web_search(args["query"])})

    # MODEL DIRECT RESPONSE
    return jsonify({"reply": msg.content})


@app.route("/")
def home():
    return "🚀 APEX-AGENT v2 Backend Running (GPT-5.1 + Real-Time Web Search)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
