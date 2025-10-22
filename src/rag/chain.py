from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from src.rag.llm import get_llm
from src.rag.vector_store import search_similar_documents
from src.schemas import QueryResponse, SourceDocument


def format_docs(docs_with_scores: List[tuple]) -> str:
    """
    Format retrieved documents into a single context string.

    Args:
        docs_with_scores: List of tuples (Document, score) from vector search

    Returns:
        Formatted string with all document contents
    """
    return "\n\n".join(doc.page_content for doc, _ in docs_with_scores)


def create_rag_chain():
    """
    Create a simple RAG chain using LangChain.

    Returns:
        Runnable chain that processes questions and generates answers

    Note:
        This is a simple RAG implementation:
        1. Retrieve relevant documents based on query
        2. Format documents as context
        3. Generate answer using LLM with context
    """
    # Define the prompt template
    template = """あなたは親切なアシスタントです。以下のコンテキスト情報を使用して、ユーザーの質問に答えてください。
コンテキストに関連する情報がない場合は、「提供されたコンテキストには関連情報がありません」と伝えてください。

コンテキスト:
{context}

質問: {question}

回答:"""

    prompt = ChatPromptTemplate.from_template(template)
    llm = get_llm()

    # Create the chain
    chain = (
        {"context": lambda x: format_docs(x["docs"]), "question": lambda x: x["question"]}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def query_rag(question: str, k: int = 5) -> QueryResponse:
    """
    Execute RAG query to answer a question.

    Args:
        question: User's question
        k: Number of documents to retrieve (default: 5)

    Returns:
        QueryResponse with answer and source documents
    """
    # Search for similar documents
    docs_with_scores = search_similar_documents(question, k=k)

    # Create and run the RAG chain
    chain = create_rag_chain()
    answer = chain.invoke({"docs": docs_with_scores, "question": question})

    # Format source documents
    sources = []
    for doc, score in docs_with_scores:
        # Extract ID from metadata if available
        doc_id = doc.metadata.get("id")
        if doc_id:
            sources.append(
                SourceDocument(
                    id=doc_id,
                    content=doc.page_content[:500],  # Truncate for response
                    score=float(score),
                    metadata=doc.metadata,
                )
            )

    return QueryResponse(answer=answer, sources=sources)
