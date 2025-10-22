from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Document Schemas
class DocumentCreate(BaseModel):
    """Schema for creating a new document."""

    content: str = Field(..., description="Markdown content of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata (title, tags, etc.)")


class DocumentResponse(BaseModel):
    """Schema for document response."""

    id: UUID
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for paginated document list response."""

    total: int = Field(..., description="Total number of documents")
    documents: List[DocumentResponse] = Field(..., description="List of documents")


# Query Schemas
class QueryRequest(BaseModel):
    """Schema for RAG query request."""

    question: str = Field(..., description="User's question", min_length=1)


class SourceDocument(BaseModel):
    """Schema for source document in query response."""

    id: UUID
    content: str = Field(..., description="Relevant content snippet")
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    """Schema for RAG query response."""

    answer: str = Field(..., description="Generated answer")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents used")


# Health Check Schema
class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(..., description="API status")
    database: str = Field(..., description="Database connection status")


# Error Schema
class ErrorResponse(BaseModel):
    """Schema for error response."""

    detail: str = Field(..., description="Error message")
