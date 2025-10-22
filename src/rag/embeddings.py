from langchain_openai import OpenAIEmbeddings

from src.config import settings


def get_embeddings() -> OpenAIEmbeddings:
    """
    Get OpenAI embeddings instance.

    Returns:
        OpenAIEmbeddings: Configured embeddings instance

    Note:
        Uses text-embedding-3-small model which produces 1536-dimensional vectors.
        This matches the vector dimension defined in the database schema.
    """
    return OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model="text-embedding-3-small",
    )
