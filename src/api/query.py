from fastapi import APIRouter, HTTPException, status

from src.dependencies import AuthUsername
from src.rag.chain import query_rag
from src.schemas import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def query_documents(
    request: QueryRequest,
    username: AuthUsername,
) -> QueryResponse:
    """
    Query documents using RAG (Retrieval-Augmented Generation).

    This endpoint:
    1. Searches for similar documents using vector similarity
    2. Uses retrieved documents as context
    3. Generates an answer using Gemini 2.5 Pro

    Args:
        request: Query request with user's question
        username: Authenticated username (from Basic auth)

    Returns:
        QueryResponse with generated answer and source documents

    Raises:
        HTTPException: If query processing fails (500 Internal Server Error)
    """
    try:
        response = query_rag(request.question)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )
