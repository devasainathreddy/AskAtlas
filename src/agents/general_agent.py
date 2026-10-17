"""General agent for casual conversation."""

from langchain_core.messages import HumanMessage

from src.config import get_llm
from src.graph.state import AgentState


def general_agent_node(state: AgentState) -> dict:
    """Handle general conversation and greetings.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with response
    """
    query = state["query"]
    
    llm = get_llm(temperature=0.7)
    
    prompt = f"""You are a friendly AI assistant called AskAtlas. 
You can help with weather queries and answer questions about documents.

Respond naturally to the user's message. Be helpful and conversational.

User: {query}

Response:"""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Handle response content
    content = response.content
    if isinstance(content, list):
        content = " ".join(str(c.get("text", c)) if isinstance(c, dict) else str(c) for c in content)
    
    return {
        "final_response": content,
        "messages": [{"role": "assistant", "content": "General response generated"}],
    }
