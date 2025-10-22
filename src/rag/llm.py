from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import settings


def get_llm() -> ChatGoogleGenerativeAI:
    """
    Get Google Gemini LLM instance.

    Returns:
        ChatGoogleGenerativeAI: Configured Gemini 2.5 Pro instance

    Note:
        Uses gemini-2.5-pro-preview-03-25 model for high-quality responses.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro-preview-03-25",
        google_api_key=settings.google_api_key,
        temperature=0.1,
        max_output_tokens=2048,
    )
