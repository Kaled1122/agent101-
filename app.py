from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime, json, requests, os
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------- TOOLS --------------------

def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def web_search(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    r = requests.get(url).json()
    return [x["Text"] for x in r.get("RelatedTopics", [])[:3]] or ["No results found"]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Returns the current time",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    }
]

SYSTEM_PROMPT = "You are an AI agent. Use tools when appropriate."

# -------------------- MAIN ENDPOINT --------------------

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

    # Tool call?
    if msg.tool_calls:
        call = msg.tool_calls[0]
        fn = call.function.name
        args = json.loads(call.function.arguments or "{}")

        if fn == "get_time":
            return jsonify({"reply": get_time()})

        if fn == "web_search":
            return jsonify({"reply": web_search(args["query"])})

    # Normal model response
    return jsonify({"reply": msg.content})

@app.route("/")
def home():
    return "Agent backend running GPT-5.1"

if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", 5000)), host="0.0.0.0")
