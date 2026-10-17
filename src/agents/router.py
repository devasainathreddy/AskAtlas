"""Router/Orchestrator agent for query classification."""

from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import get_llm_with_structured_output
from src.graph.state import AgentState


class QueryClassification(BaseModel):
    """Schema for query classification."""
    
    intent: Literal["weather", "rag", "both", "general"] = Field(
        description="The type of query: 'weather', 'rag', 'both', or 'general' for greetings/casual chat"
    )
    weather_query: Optional[str] = Field(
        default=None,
        description="The weather-related part of the query (city name or weather question)"
    )
    rag_query: Optional[str] = Field(
        default=None,
        description="The document-related part of the query (question about PDF content)"
    )


def get_router_llm():
    """Get LLM configured for routing with structured output."""
    return get_llm_with_structured_output(QueryClassification, temperature=0)


def router_node(state: AgentState) -> dict:
    """Classify the query and determine which agents to call.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with query classification
    """
    router = get_router_llm()
    
    system_prompt = """You are a query classifier for an AI assistant that can:
1. Fetch real-time weather data for cities
2. Answer questions from a PDF document about AI, LLMs, embeddings, and RAG

Classify the user's query:
- "weather": Query is about current weather in a city (e.g., "What's the weather in Mumbai?")
- "rag": Query is about the PDF document content (e.g., "What is RAG?" or "Explain embeddings")
- "both": Query combines weather AND document questions
- "general": Greetings, casual chat, or questions not related to weather or documents (e.g., "Hello", "Hi", "How are you?", "Thanks")

Extract the relevant parts of the query for each type."""

    result = router.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["query"]),
    ])
    
    return {
        "query_type": result.intent,
        "weather_query": result.weather_query,
        "rag_query": result.rag_query,
        "messages": [{"role": "system", "content": f"Query classified as: {result.intent}"}],
    }


def route_query(state: AgentState) -> str:
    """Determine which agent node to call based on query type.
    
    Args:
        state: Current graph state
        
    Returns:
        Node name to route to
    """
    query_type = state.get("query_type", "general")
    
    if query_type == "weather":
        return "weather_agent"
    elif query_type == "rag":
        return "rag_agent"
    elif query_type == "both":
        return "both_agents"
    else:  # general
        return "general_agent"

