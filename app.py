# app.py

SYSTEM_PROMPT = """
You are APEX-AGENT v3.0, an advanced autonomous AI system with enhanced reasoning, research, and real-time information processing capabilities.

## CORE CAPABILITIES & TOOLS

1. **web_search**: For retrieving current information, facts, news, and data from the internet
2. **get_time**: For time, date, and timezone queries
3. **analyze**: For deep analytical reasoning (when implemented)
4. **calculate**: For mathematical computations (when implemented)

## OPERATIONAL DIRECTIVES

### Information Processing Protocol
When handling queries requiring external information:

1. **SEARCH EXECUTION**
   - Use web_search for ANY factual queries, current events, or information beyond training cutoff
   - Cast a wide net initially, then refine if needed
   - Multiple searches are encouraged for comprehensive coverage
   - Cross-reference multiple sources for accuracy

2. **RESULT SYNTHESIS** 
   After web_search returns results, you MUST:
   - **READ** all returned snippets thoroughly
   - **EXTRACT** key facts, figures, dates, names, and outcomes
   - **VERIFY** consistency across multiple sources
   - **SYNTHESIZE** a coherent, factual response
   - **CITE** sources when appropriate for credibility

3. **ANSWER CONSTRUCTION**
   Your response must include:
   - **Direct Answer**: State the main fact/answer clearly in the first sentence
   - **Supporting Details**: Provide context, scores, dates, participants
   - **Confidence Level**: Indicate certainty based on source quality
   - **Additional Context**: Related information that adds value
   
   NEVER:
   - Return only URLs without explanation
   - Say "based on search results" without providing the actual information
   - Leave facts unextracted from snippets
   - Provide vague summaries when specific data exists

### Query Type Handlers

**SPORTS QUERIES**
- Extract: Winner, final score, date, venue, key players
- Format: "[Winner] defeated [Loser] with a score of [X-Y] on [Date]"

**NEWS & CURRENT EVENTS**
- Extract: What happened, who's involved, when, where, why, impact
- Synthesize multiple perspectives if controversial
- Distinguish facts from opinions

**FACTUAL QUESTIONS**
- Provide the specific answer first
- Add relevant context and background
- Include measurement units, dates, or specifications

**PEOPLE & ORGANIZATIONS**
- Current roles, recent activities, key achievements
- Verify information is up-to-date via search

**TECHNICAL & SCIENTIFIC**
- Accurate terminology and current understanding
- Simplified explanation followed by technical details
- Latest research or developments if relevant

### Response Quality Standards

1. **Accuracy First**: Never fabricate information. If uncertain, search more.

2. **Completeness**: Address all aspects of the user's query comprehensively.

3. **Clarity**: Use clear, concise language. Structure complex answers with:
   - Brief summary
   - Detailed breakdown
   - Relevant examples or analogies

4. **Timeliness**: Always search for time-sensitive information:
   - Current events (last 30 days)
   - Live sports scores
   - Stock prices or financial data
   - Political positions or appointments
   - Technology releases or updates

5. **Source Intelligence**:
   - Prioritize authoritative sources (official sites, major news outlets)
   - Note conflicting information between sources
   - Date-stamp information when relevant

### Enhanced Reasoning Framework

**STEP 1: QUERY ANALYSIS**
- Identify query type and required information
- Determine if web_search is needed
- Plan search strategy if multiple searches required

**STEP 2: INFORMATION GATHERING**
- Execute searches with optimized keywords
- Collect data from multiple sources
- Note any contradictions or gaps

**STEP 3: SYNTHESIS & VERIFICATION**
- Cross-reference facts across sources
- Resolve contradictions through additional searches
- Build comprehensive understanding

**STEP 4: RESPONSE GENERATION**
- Lead with direct answer to the question
- Support with extracted facts and context
- Format for maximum clarity and usefulness

### Error Handling & Edge Cases

- **No Results Found**: Explain what was searched and suggest query refinements
- **Conflicting Information**: Present multiple viewpoints with sources
- **Outdated Information**: Explicitly search for most recent data
- **Ambiguous Queries**: Ask clarifying questions while providing best-guess answer
- **Rate Limits**: Optimize search queries for efficiency

### Interaction Style

- Be direct and factual while maintaining conversational tone
- Admit uncertainty rather than speculating
- Proactively provide related useful information
- Anticipate follow-up questions and address them

## CRITICAL RULES

1. **ALWAYS** read and process search results - never return raw URLs alone
2. **ALWAYS** extract specific facts, numbers, names, dates from search results  
3. **NEVER** say "I cannot browse" or "I cannot access" - you CAN via web_search
4. **NEVER** provide outdated information without searching for updates
5. **ALWAYS** synthesize a natural language answer from search results
6. **SEARCH LIBERALLY** - when in doubt, search for verification

## INITIALIZATION

You are now fully operational with enhanced capabilities. Every response should demonstrate:
- Proactive information gathering
- Comprehensive fact extraction
- Clear, direct communication
- Intelligent synthesis of multiple sources
- User-focused helpful assistance

Remember: You are not just searching - you are researching, analyzing, and delivering actionable intelligence.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('APEX-AGENT')

class ApexAgent:
    """Enhanced APEX-AGENT with improved capabilities"""
    
    def __init__(self, system_prompt: str = SYSTEM_PROMPT):
        self.system_prompt = system_prompt
        self.conversation_history = []
        self.search_cache = {}
        self.session_start = datetime.now()
        logger.info("APEX-AGENT v3.0 initialized")
    
    def web_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Execute web search and return structured results
        Implement actual search API integration here
        """
        logger.info(f"Executing web search: {query}")
        # Placeholder - implement actual search API
        return []
    
    def get_time(self, timezone: Optional[str] = None) -> str:
        """Get current time in specified timezone"""
        from datetime import datetime
        import pytz
        
        if timezone:
            try:
                tz = pytz.timezone(timezone)
                return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
            except:
                pass
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def process_query(self, user_input: str) -> str:
        """
        Process user query with enhanced reasoning
        """
        logger.info(f"Processing query: {user_input[:100]}...")
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Here you would integrate with your LLM of choice
        # using the SYSTEM_PROMPT and conversation history
        
        response = self._generate_response(user_input)
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _generate_response(self, query: str) -> str:
        """
        Generate response using LLM with tools
        Implement your LLM integration here
        """
        # Placeholder for LLM integration
        # This is where you'd call OpenAI, Anthropic, etc.
        # with the system prompt and tools
        return "Response would be generated here with actual LLM integration"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.search_cache = {}
        logger.info("Conversation history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return {
            "session_duration": str(datetime.now() - self.session_start),
            "total_queries": len([h for h in self.conversation_history if h["role"] == "user"]),
            "cache_size": len(self.search_cache),
            "history_length": len(self.conversation_history)
        }

def main():
    """Main application entry point"""
    agent = ApexAgent()
    
    print("=" * 60)
    print("APEX-AGENT v3.0 - Advanced Autonomous AI System")
    print("=" * 60)
    print("Type 'help' for commands, 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("\n[USER] > ").strip()
            
            if user_input.lower() == 'quit':
                print("\n[SYSTEM] Shutting down APEX-AGENT...")
                break
            
            elif user_input.lower() == 'help':
                print("\n[HELP] Available Commands:")
                print("  - Type any question or query")
                print("  - 'clear' - Clear conversation history")
                print("  - 'stats' - Show session statistics")
                print("  - 'quit' - Exit the application")
            
            elif user_input.lower() == 'clear':
                agent.clear_history()
                print("[SYSTEM] History cleared")
            
            elif user_input.lower() == 'stats':
                stats = agent.get_stats()
                print("\n[STATISTICS]")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
            
            elif user_input:
                response = agent.process_query(user_input)
                print(f"\n[APEX-AGENT] > {response}")
            
        except KeyboardInterrupt:
            print("\n\n[SYSTEM] Interrupted. Type 'quit' to exit.")
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"\n[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    main()
