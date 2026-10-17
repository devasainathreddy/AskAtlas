"""RAG tool for document retrieval from Qdrant."""

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class RAGInput(BaseModel):
    """Input schema for RAG tool."""

    question: str = Field(description="Question to search for in the documents")


@tool(args_schema=RAGInput)
def query_documents(question: str) -> str:
    """Search the document database for relevant information.
    
    Args:
        question: The question to search for in the documents
        
    Returns:
        Relevant document chunks with their content
    """
    from src.vectorstore.qdrant_client import get_retriever
    
    try:
        retriever = get_retriever()
        docs = retriever.invoke(question)
        
        if not docs:
            return "No relevant information found in the documents."
        
        # Format the results
        results = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content.strip()
            results.append(f"[{i}] {content}")
        
        return "\n\n".join(results)
    except Exception as e:
        return f"Error searching documents: {str(e)}"
