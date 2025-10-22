import uuid
from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from src.database import Base


class Document(Base):
    """
    Document model for storing user-submitted markdown content with embeddings.

    Attributes:
        id: Unique identifier (UUID)
        content: Markdown content of the document
        embedding: Vector embedding (1536 dimensions for OpenAI embeddings)
        metadata: JSON metadata (title, tags, etc.)
        created_at: Timestamp when document was created
        updated_at: Timestamp when document was last updated
    """

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    metadata = Column(JSONB, nullable=False, default=dict, server_default="{}")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, metadata={self.metadata})>"
