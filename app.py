from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import datetime
import logging
import requests
from openai import OpenAI

# ------------------ APP & LOGGING ------------------

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("APEX-AGENT")

# OpenAI client (new SDK)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------ SYSTEM PROMPT ------------------

SYSTEM_PROMPT = """
You are APEX-AGENT v3.0, an advanced autonomous AI system with enhanced reasoning, research, and real-time information processing capabilities.

## CRITICAL SEARCH PROCESSING RULES

When using web_search tool:
1. ALWAYS READ the search results completely
2. ALWAYS EXTRACT the specific answer from the results
3. ALWAYS SYNTHESIZE a clear, direct answer with the facts
4. NEVER return just URLs or say "based on the search results" without the actual information

MANDATORY RESPONSE FORMAT for web searches:

1. DIRECT ANSWER FIRST: State the main fact/answer in the first sentence
2. KEY DETAILS: Include scores, dates, names, specific numbers
3. SOURCE: Briefly mention source credibility if relevant

BAD: "Based on search results, here are some links about the game..."
GOOD: "The Lakers defeated the Celtics 117-96 last night at Crypto.com Arena."

BAD: "I found information about this topic: [URLs]"
GOOD: "Tesla's stock closed at $242.84, up 3.5% today following Q4 earnings beat."

## SEARCH TRIGGERS
Use web_search for:
- Current events and news
- Sports scores and results
- Stock prices and market data
- Recent developments (last 2 years)
- Any factual questions where you need verification
- People's current roles or positions
- Latest statistics or data

## CORE DIRECTIVE
You are not a link aggregator. You are an intelligent agent that:
- Searches for information
- Reads and processes the results
- Extracts the relevant facts
- Delivers a clear, comprehensive answer

Remember: Users want ANSWERS, not links. Process search results and give them the information they're looking for.
"""

# ------------------ TOOLS ------------------


def get_time():
    """
    Return current time in Riyadh (UTC+3), regardless of server timezone.
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    ksa_time = now_utc + datetime.timedelta(hours=3)
    return ksa_time.strftime("Current time in Riyadh (UTC+3) is %Y-%m-%d %H:%M:%S")


def web_search(query: str):
    """
    General-purpose real-time search using SerpAPI (Google).
    Returns text snippets for the model to read & summarize.
    """
    key = os.getenv("SERPAPI_KEY")
    if not key:
        return ["❌ SERPAPI_KEY is not set in the environment"]

    try:
        r = requests.get(
            "https://serpapi.com/search.json",
            params={"q": query, "api_key": key},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logger.error(f"SERPAPI ERROR: {e}")
        return [f"❌ Web search failed: {e}"]

    snippets = []
    for item in data.get("organic_results", [])[:3]:
        title = item.get("title")
        snippet = item.get("snippet") or ""
        link = item.get("link")
        if title:
            snippets.append(f"{title}\n{snippet}\n{link or ''}")

    return snippets or ["No results found"]


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current time in Riyadh (UTC+3).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web using SerpAPI and return readable snippets.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
]

# ------------------ CORE CHAT HANDLER ------------------


def handle_chat_message(user_message: str):
    """
    Core logic: call GPT-5.1 with tools, execute tools if needed,
    and always return a string reply (no exceptions leaking out).
    """
    logger.info(f"Received message: {user_message[:200]}")

    if not user_message.strip():
        return "Please type a message."

    # 1) Call OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            tools=TOOLS,
            tool_choice="auto",
        )
    except Exception as e:
        logger.error(f"OPENAI ERROR: {e}")
        return f"❌ OpenAI error: {e}"

    msg = response.choices[0].message
    logger.info(f"RAW OPENAI MESSAGE: {msg}")

    # 2) If tool call requested
    if getattr(msg, "tool_calls", None):
        tool_call = msg.tool_calls[0]
        tool_name = tool_call.function.name
        args_str = tool_call.function.arguments or "{}"
        logger.info(f"TOOL CALL: {tool_name} {args_str}")

        try:
            args = json.loads(args_str)
        except Exception as e:
            logger.error(f"ARGS PARSE ERROR: {e}")
            return f"❌ Tool args parse error: {e}"

        if tool_name == "get_time":
            return get_time()

        if tool_name == "web_search":
            query = args.get("query", "")
            snippets = web_search(query)
            # Let the model synthesize a clean answer from snippets
            try:
                followup = client.chat.completions.create(
                    model="gpt-5.1",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                        {
                            "role": "tool",
                            "name": "web_search",
                            "content": "\n\n".join(snippets),
                        },
                    ],
                )
                final_msg = followup.choices[0].message
                return final_msg.content or "\n\n".join(snippets)
            except Exception as e:
                logger.error(f"FOLLOWUP OPENAI ERROR: {e}")
                return "\n\n".join(snippets)

        return f"❌ Unknown tool requested: {tool_name}"

    # 3) No tool: normal answer
    return msg.content or "I couldn't generate a response."


# ------------------ ROUTES ------------------


@app.route("/chat", methods=["POST"])
@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Universal chat endpoint. Always returns:
    { "reply": "...", "response": "...", "status": "success|error" }
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        user_message = data.get("message", "")
        reply = handle_chat_message(user_message)
        return jsonify({"reply": reply, "response": reply, "status": "success"})
    except Exception as e:
        logger.error(f"Error in /chat: {e}")
        text = f"❌ Server error: {e}"
        return jsonify({"reply": text, "response": text, "status": "error"})


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "agent": "APEX-AGENT v3.0",
            "timestamp": datetime.datetime.now().isoformat(),
        }
    )


@app.route("/api/system-prompt")
def get_system_prompt():
    return jsonify({"prompt": SYSTEM_PROMPT, "version": "3.0"})


@app.route("/")
def home():
    return "APEX-AGENT v3.0 backend is running."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
