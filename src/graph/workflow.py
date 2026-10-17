"""Main LangGraph workflow for AskAtlas."""

from langgraph.graph import StateGraph, START, END

from src.graph.state import AgentState
from src.agents.router import router_node, route_query
from src.agents.weather_agent import weather_agent_node
from src.agents.rag_agent import rag_agent_node
from src.agents.general_agent import general_agent_node
from src.agents.synthesizer import synthesizer_node


def both_agents_node(state: AgentState) -> dict:
    """Run both weather and RAG agents."""
    # Run weather agent
    weather_result = weather_agent_node(state)
    
    # Run RAG agent
    rag_result = rag_agent_node(state)
    
    # Combine results
    return {
        "weather_result": weather_result.get("weather_result"),
        "rag_result": rag_result.get("rag_result"),
        "messages": weather_result.get("messages", []) + rag_result.get("messages", []),
    }


def create_workflow():
    """Create the main agent workflow.
    
    The workflow follows an Orchestrator-Worker pattern:
    1. Router classifies the query
    2. Appropriate worker agents are called
    3. Synthesizer combines results into final response
    
    Returns:
        Compiled LangGraph workflow
    """
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("weather_agent", weather_agent_node)
    workflow.add_node("rag_agent", rag_agent_node)
    workflow.add_node("general_agent", general_agent_node)
    workflow.add_node("both_agents", both_agents_node)
    workflow.add_node("synthesizer", synthesizer_node)
    
    # Add edges
    workflow.add_edge(START, "router")
    
    # Conditional routing based on query type
    workflow.add_conditional_edges(
        "router",
        route_query,
        {
            "weather_agent": "weather_agent",
            "rag_agent": "rag_agent",
            "general_agent": "general_agent",
            "both_agents": "both_agents",
        }
    )
    
    # All agents lead to synthesizer (except general which goes to END)
    workflow.add_edge("weather_agent", "synthesizer")
    workflow.add_edge("rag_agent", "synthesizer")
    workflow.add_edge("both_agents", "synthesizer")
    workflow.add_edge("general_agent", END)  # General doesn't need synthesis
    
    # Synthesizer leads to end
    workflow.add_edge("synthesizer", END)
    
    # Compile the workflow
    return workflow.compile()


# Create a singleton instance
_workflow = None


def get_workflow():
    """Get the compiled workflow instance."""
    global _workflow
    if _workflow is None:
        _workflow = create_workflow()
    return _workflow


def run_query(query: str) -> str:
    """Run a query through the workflow.
    
    Args:
        query: User's input query
        
    Returns:
        Final response from the agent
    """
    workflow = get_workflow()
    
    initial_state = {
        "query": query,
        "query_type": None,
        "weather_query": None,
        "rag_query": None,
        "weather_result": None,
        "rag_result": None,
        "final_response": None,
        "messages": [],
    }
    
    result = workflow.invoke(initial_state)
    
    return result.get("final_response", "No response generated.")
