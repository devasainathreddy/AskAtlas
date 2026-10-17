"""Synthesizer agent for combining results."""

from langchain_core.messages import HumanMessage

from src.config import get_llm
from src.graph.state import AgentState


def synthesizer_node(state: AgentState) -> dict:
    """Synthesize final response from agent results.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with final response
    """
    query_type = state.get("query_type", "rag")
    weather_result = state.get("weather_result")
    rag_result = state.get("rag_result")
    original_query = state["query"]
    
    # Build context based on what results we have
    context_parts = []
    
    if weather_result:
        context_parts.append(f"**Weather Information:**\n{weather_result}")
    
    if rag_result:
        context_parts.append(f"**Document Information:**\n{rag_result}")
    
    if not context_parts:
        return {
            "final_response": "I apologize, but I couldn't find relevant information to answer your question.",
            "messages": [{"role": "assistant", "content": "No results to synthesize"}],
        }
    
    combined_context = "\n\n".join(context_parts)
    
    # For simple queries, just return the result UNLESS comparison is requested
    comparison_triggers = ["compare", "difference", " vs ", "versus", "better"]
    is_comparison = any(trigger in original_query.lower() for trigger in comparison_triggers)
    
    if query_type in ["weather", "rag"] and len(context_parts) == 1 and not is_comparison:
        return {
            "final_response": context_parts[0].split(":**\n", 1)[-1],
            "messages": [{"role": "assistant", "content": "Response generated"}],
        }
    
    # For hybrid queries, synthesize the response
    llm = get_llm(temperature=0.5)
    
    synthesis_prompt = f"""You are a helpful assistant. The user asked a question and you have gathered information from multiple sources.

Original Question: {original_query}

Gathered Information:
{combined_context}

Please provide a cohesive, well-formatted response that addresses the user's complete question. 
Combine the information naturally and ensure nothing is missed.

Response:"""

    response = llm.invoke([HumanMessage(content=synthesis_prompt)])
    
    return {
        "final_response": response.content,
        "messages": [{"role": "assistant", "content": "Final response synthesized"}],
    }
