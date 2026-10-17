"""PDF ingestion script for AskAtlas."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.documents import Document

from src.config import get_settings
from src.vectorstore.qdrant_client import add_documents, ensure_collection_exists


def load_pdf(pdf_path: str) -> str:
    """Load text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text from the PDF
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[Document]:
    """Split text into chunks for embedding.
    
    Args:
        text: Text to split
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of Document objects
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    
    chunks = splitter.split_text(text)
    documents = [
        Document(page_content=chunk, metadata={"source": "rag.pdf", "chunk": i})
        for i, chunk in enumerate(chunks)
    ]
    return documents


def ingest_pdf(pdf_path: str = None) -> None:
    """Ingest a PDF file into the vector database.
    
    Args:
        pdf_path: Path to PDF file (defaults to config setting)
    """
    settings = get_settings()
    pdf_path = pdf_path or settings.pdf_path
    
    print(f"Loading PDF from: {pdf_path}")
    
    # Load and process PDF
    text = load_pdf(pdf_path)
    print(f"Extracted {len(text)} characters from PDF")
    
    # Chunk the text
    documents = chunk_text(text)
    print(f"Created {len(documents)} document chunks")
    
    # Ensure collection exists
    ensure_collection_exists()
    
    # Add to vector store
    add_documents(documents)
    print("PDF ingestion complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest PDF into Qdrant")
    parser.add_argument(
        "--pdf", 
        type=str, 
        default=None,
        help="Path to PDF file (defaults to config setting)"
    )
    
    args = parser.parse_args()
    ingest_pdf(args.pdf)
