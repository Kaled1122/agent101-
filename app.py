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
