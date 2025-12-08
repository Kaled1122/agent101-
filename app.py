# app.py

from flask import Flask, request, jsonify, render_template_string
import os
import json
from datetime import datetime
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('APEX-AGENT')

SYSTEM_PROMPT = """
You are APEX-AGENT v3.0, an advanced autonomous AI system with enhanced reasoning, research, and real-time information processing capabilities.

## CRITICAL SEARCH PROCESSING RULES

When using web_search tool:
1. **ALWAYS READ** the search results completely
2. **ALWAYS EXTRACT** the specific answer from the results
3. **ALWAYS SYNTHESIZE** a clear, direct answer with the facts
4. **NEVER** return just URLs or say "based on the search results" without the actual information

### MANDATORY RESPONSE FORMAT for web searches:

1. **DIRECT ANSWER FIRST**: State the main fact/answer in the first sentence
2. **KEY DETAILS**: Include scores, dates, names, specific numbers
3. **SOURCE**: Briefly mention source credibility if relevant

### EXAMPLES:

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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APEX-AGENT v3.0</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            max-width: 800px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .chat-container {
            background: #f7f7f7;
            border-radius: 10px;
            padding: 20px;
            min-height: 400px;
            max-height: 500px;
            overflow-y: auto;
            margin-bottom: 20px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 10px;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            margin-left: 20%;
            text-align: right;
        }
        
        .agent-message {
            background: white;
            color: #333;
            margin-right: 20%;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .input-container {
            display: flex;
            gap: 10px;
        }
        
        input[type="text"] {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .system-prompt {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .system-prompt h3 {
            color: #666;
            margin-bottom: 10px;
        }
        
        .system-prompt pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 12px;
            color: #555;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>APEX-AGENT v3.0</h1>
        <p class="subtitle">Advanced Autonomous AI System - Direct Answer Engine</p>
        
        <div class="chat-container" id="chat">
            <div class="message agent-message">
                Hello! I'm APEX-AGENT v3.0. I'm designed to provide direct, factual answers to your questions. I'll search for information and give you the specific facts you need, not just links. Try asking me about current events, sports scores, stock prices, or any factual questions!
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="userInput" placeholder="Ask me anything..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <div class="system-prompt">
            <h3>System Configuration</h3>
            <pre>{{ system_prompt }}</pre>
        </div>
    </div>
    
    <script>
        function sendMessage() {
            const input = document.getElementById('userInput');
            const chat = document.getElementById('chat');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            chat.innerHTML += `<div class="message user-message">${message}</div>`;
            input.value = '';
            
            // Add loading indicator
            chat.innerHTML += `<div class="message agent-message" id="loading"><div class="loading"></div> Thinking...</div>`;
            chat.scrollTop = chat.scrollHeight;
            
            // Send to backend
            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').remove();
                chat.innerHTML += `<div class="message agent-message">${data.response}</div>`;
                chat.scrollTop = chat.scrollHeight;
            })
            .catch(error => {
                document.getElementById('loading').remove();
                chat.innerHTML += `<div class="message agent-message">Error: ${error.message}</div>`;
                chat.scrollTop = chat.scrollHeight;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template_string(HTML_TEMPLATE, system_prompt=SYSTEM_PROMPT[:500] + "...")

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # Log the incoming message
        logger.info(f"Received message: {user_message[:100]}...")
        
        # Here you would integrate with your LLM API
        # For now, return a placeholder response
        response = f"I received your message: '{user_message}'. To fully function, I need to be connected to an LLM API (OpenAI, Anthropic, etc.) with the web_search tool enabled. The system prompt above shows how I should process search results to give you direct answers, not just links."
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({
            'response': f"Error: {str(e)}",
            'status': 'error'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'agent': 'APEX-AGENT v3.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/system-prompt')
def get_system_prompt():
    """Return the full system prompt"""
    return jsonify({
        'prompt': SYSTEM_PROMPT,
        'version': '3.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
