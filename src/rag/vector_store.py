from typing import List, Tuple
from uuid import UUID

from langchain_core.documents import Document as LangChainDocument
from langchain_postgres import PGVector
from sqlalchemy.orm import Session

from src.config import settings
from src.models import Document
from src.rag.embeddings import get_embeddings


def get_vector_store() -> PGVector:
    """
    Get PGVector store instance.

    Returns:
        PGVector: Configured vector store for similarity search
    """
    embeddings = get_embeddings()

    return PGVector(
        embeddings=embeddings,
        collection_name="documents",
        connection=settings.database_url,
        use_jsonb=True,
    )


def add_document_to_vector_store(
    db: Session,
    document: Document,
) -> None:
    """
    Add a document to the vector store.

    Args:
        db: Database session
        document: Document model instance with content to embed

    Note:
        This function generates embeddings for the document content
        and stores them in the vector store for similarity search.
    """
    embeddings = get_embeddings()

    # Generate embedding for the document content
    embedding_vector = embeddings.embed_query(document.content)

    # Update the document with the embedding
    document.embedding = embedding_vector
    db.commit()


def search_similar_documents(
    query: str,
    k: int = 5,
) -> List[Tuple[LangChainDocument, float]]:
    """
    Search for similar documents using vector similarity.

    Args:
        query: Search query text
        k: Number of similar documents to retrieve (default: 5)

    Returns:
        List of tuples containing (Document, similarity_score)
        Documents are LangChain Document objects with page_content and metadata
    """
    vector_store = get_vector_store()

    # Search for similar documents with scores
    results = vector_store.similarity_search_with_score(query, k=k)

    return results
