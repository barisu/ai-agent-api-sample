from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.auth import verify_credentials
from src.database import get_db

# Type aliases for dependency injection
DBSession = Annotated[Session, Depends(get_db)]
AuthUsername = Annotated[str, Depends(verify_credentials)]
