"""Graph state definitions for AskAtlas."""

from typing import Annotated, Optional
from typing_extensions import TypedDict
import operator


class AgentState(TypedDict):
    """Main state for the agent graph.
    
    Attributes:
        query: The user's input query
        query_type: Classified type of query (weather, rag, both)
        weather_query: Extracted weather-related query
        rag_query: Extracted RAG-related query
        weather_result: Result from weather agent
        rag_result: Result from RAG agent
        final_response: Synthesized final response
        messages: Conversation history
    """
    
    query: str
    query_type: Optional[str]
    weather_query: Optional[str]
    rag_query: Optional[str]
    weather_result: Optional[str]
    rag_result: Optional[str]
    final_response: Optional[str]
    messages: Annotated[list, operator.add]
