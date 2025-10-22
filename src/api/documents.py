from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.dependencies import AuthUsername, DBSession
from src.models import Document
from src.rag.vector_store import add_document_to_vector_store
from src.schemas import DocumentCreate, DocumentListResponse, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document: DocumentCreate,
    db: DBSession,
    username: AuthUsername,
) -> DocumentResponse:
    """
    Create a new document with markdown content.

    This endpoint:
    1. Stores the markdown content in the database
    2. Generates vector embeddings using OpenAI
    3. Stores embeddings for similarity search

    Args:
        document: Document creation request with content and metadata
        db: Database session
        username: Authenticated username (from Basic auth)

    Returns:
        DocumentResponse with created document details

    Raises:
        HTTPException: If document creation fails (500 Internal Server Error)
    """
    try:
        # Create document model instance
        db_document = Document(
            content=document.content,
            metadata=document.metadata,
        )

        db.add(db_document)
        db.flush()  # Flush to get the ID before embedding

        # Generate and store embeddings
        add_document_to_vector_store(db, db_document)

        db.refresh(db_document)
        return DocumentResponse.model_validate(db_document)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document creation failed: {str(e)}"
        )


@router.get("", response_model=DocumentListResponse)
def list_documents(
    db: DBSession,
    username: AuthUsername,
    skip: int = 0,
    limit: int = 10,
) -> DocumentListResponse:
    """
    List all documents with pagination.

    Args:
        db: Database session
        username: Authenticated username (from Basic auth)
        skip: Number of documents to skip (default: 0)
        limit: Maximum number of documents to return (default: 10)

    Returns:
        DocumentListResponse with total count and list of documents
    """
    total = db.query(Document).count()
    documents = db.query(Document).offset(skip).limit(limit).all()

    return DocumentListResponse(
        total=total,
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    db: DBSession,
    username: AuthUsername,
) -> DocumentResponse:
    """
    Get a specific document by ID.

    Args:
        document_id: Document UUID
        db: Database session
        username: Authenticated username (from Basic auth)

    Returns:
        DocumentResponse with document details

    Raises:
        HTTPException: If document not found (404 Not Found)
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found"
        )

    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    db: DBSession,
    username: AuthUsername,
) -> None:
    """
    Delete a document by ID.

    Args:
        document_id: Document UUID
        db: Database session
        username: Authenticated username (from Basic auth)

    Raises:
        HTTPException: If document not found (404 Not Found)
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found"
        )

    db.delete(document)
    db.commit()
