import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.config import settings

security = HTTPBasic()


def verify_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
) -> str:
    """
    Verify HTTP Basic authentication credentials.

    Args:
        credentials: HTTP Basic credentials from request

    Returns:
        Username if authentication is successful

    Raises:
        HTTPException: If credentials are invalid (401 Unauthorized)
    """
    # Use secrets.compare_digest to prevent timing attacks
    is_username_correct = secrets.compare_digest(
        credentials.username.encode("utf8"),
        settings.basic_auth_username.encode("utf8")
    )
    is_password_correct = secrets.compare_digest(
        credentials.password.encode("utf8"),
        settings.basic_auth_password.encode("utf8")
    )

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
