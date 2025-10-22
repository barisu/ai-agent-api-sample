from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from src.dependencies import DBSession
from src.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: DBSession) -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse with API and database status

    Raises:
        HTTPException: If database connection fails (503 Service Unavailable)
    """
    try:
        # Try to execute a simple query to check database connection
        db.execute(text("SELECT 1"))
        return HealthResponse(status="ok", database="connected")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )
