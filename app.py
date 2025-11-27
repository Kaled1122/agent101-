from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json, datetime, requests
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are APEX-AGENT v2, an autonomous, tool-enabled AI system designed for real-time reasoning and research.
Use web_search for any external facts. Use get_time for time queries. Do not guess. Be concise and accurate.
"""

# ------------------ TOOLS ------------------

def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def web_search(query: str):
    key = os.getenv("SERPAPI_KEY")
    r = requests.get(
        "https://serpapi.com/search.json",
        params={"q": query, "api_key": key}
    ).json()
    results = []
    for item in r.get("organic_results", [])[:3]:
        results.append(f"{item['title']} → {item['link']}")
    return results or ["No results found"]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get current time.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web using SerpAPI.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    }
]

# ------------------ CHAT ROUTE ------------------

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ],
        tools=TOOLS
    )

    msg = response.choices[0].message

    # TOOL CALL DETECTED
    if msg.tool_calls:
        tool = msg.tool_calls[0].function.name
        args = json.loads(msg.tool_calls[0].function.arguments)

        if tool == "get_time":
            return jsonify({"reply": get_time()})

        if tool == "web_search":
            return jsonify({"reply": web_search(args["query"])})

    # NORMAL RESPONSE
    return jsonify({"reply": msg.content})

@app.route("/")
def home():
    return "APEX-AGENT v2 BACKEND ACTIVE"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
