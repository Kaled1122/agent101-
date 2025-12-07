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
    if not key:
        return ["❌ SERPAPI_KEY is not set in the environment"]

    try:
        r = requests.get(
            "https://serpapi.com/search.json",
            params={"q": query, "api_key": key},
            timeout=15
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("SERPAPI ERROR:", e, flush=True)
        return [f"❌ Web search failed: {e}"]

    results = []
    for item in data.get("organic_results", [])[:3]:
        title = item.get("title")
        link = item.get("link")
        if title and link:
            results.append(f"{title} → {link}")

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
    """
    Always returns 200 with a 'reply' field.
    Any internal error is sent back as text instead of crashing.
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        user_msg = (data.get("message") or "").strip()
        print("INCOMING MESSAGE:", user_msg, flush=True)

        if not user_msg:
            return jsonify({ "reply": "Please type a message." })

        # Call OpenAI
        try:
            response = client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg}
                ],
                tools=TOOLS,
                tool_choice="auto"
            )
        except Exception as e:
            print("OPENAI ERROR:", e, flush=True)
            return jsonify({ "reply": f"❌ OpenAI error: {e}" })

        msg = response.choices[0].message
        print("RAW OPENAI MESSAGE:", msg, flush=True)

        # TOOL CALL
        if getattr(msg, "tool_calls", None):
            tool_call = msg.tool_calls[0]
            tool_name = tool_call.function.name
            args_str = tool_call.function.arguments or "{}"
            print("TOOL CALL:", tool_name, args_str, flush=True)

            try:
                args = json.loads(args_str)
            except Exception as e:
                print("ARGS PARSE ERROR:", e, flush=True)
                return jsonify({ "reply": f"❌ Tool args parse error: {e}" })

            if tool_name == "get_time":
                return jsonify({ "reply": get_time() })

            if tool_name == "web_search":
                query = args.get("query", "")
                return jsonify({ "reply": web_search(query) })

            # Unknown tool
            return jsonify({ "reply": f"❌ Unknown tool requested: {tool_name}" })

        # NORMAL RESPONSE
        content = msg.content or "I couldn't generate a response."
        return jsonify({ "reply": content })

    except Exception as e:
        # Last-resort catch: never 500, just show the error
        print("FATAL ERROR in /chat:", e, flush=True)
        return jsonify({ "reply": f"❌ Server error: {e}" })


@app.route("/")
def home():
    return "APEX-AGENT v2 BACKEND ACTIVE"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
