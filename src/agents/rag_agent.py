"""RAG agent node."""

from langchain_core.messages import HumanMessage

from src.config import get_llm
from src.graph.state import AgentState
from src.tools.rag_tool import query_documents


def rag_agent_node(state: AgentState) -> dict:
    """Execute RAG agent to retrieve and process document information.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with RAG result
    """
    # Get the RAG query (either extracted or full query)
    query = state.get("rag_query") or state["query"]
    
    # Retrieve relevant documents
    try:
        retrieved_docs = query_documents.invoke({"question": query})
    except Exception as e:
        retrieved_docs = f"Error retrieving documents: {str(e)}"
    
    # Generate answer using retrieved context
    llm = get_llm(temperature=0.3)
    
    rag_prompt = f"""You are a helpful assistant that answers questions based on the provided context from a PDF document.

Context from documents:
{retrieved_docs}

User Question: {query}

Instructions:
- Answer based ONLY on the provided context
- If the context doesn't contain relevant information, say so
- Be concise and accurate
- Cite specific information from the context when possible

Answer:"""

    response = llm.invoke([HumanMessage(content=rag_prompt)])
    
    return {
        "rag_result": response.content,
        "messages": [{"role": "assistant", "content": "Document search completed"}],
    }
