"""
RAG Document Assistant — Chat Routes

Handles question answering over indexed documents.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.core.llm import get_llm

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask a question about your uploaded documents.

    The pipeline:
    1. Embed the question
    2. Retrieve relevant chunks from Pinecone
    3. Generate answer using LLM with retrieved context
    4. Validate output through Guardrails AI
    5. Return answer with source citations
    """
    llm = get_llm()

    # TODO: Implement full RAG pipeline
    # 1. Embed query → search Pinecone → get relevant chunks
    # 2. Build prompt with context
    # 3. Generate response via LLM
    # 4. Validate through guardrails
    # 5. Return with sources

    # Placeholder: Direct LLM call (no RAG yet)
    response = llm.invoke(request.question)

    return ChatResponse(
        answer=response.content,
        sources=[],
        model=llm.model if hasattr(llm, "model") else "unknown",
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Ask a question with streaming response (Server-Sent Events).
    """
    llm = get_llm()

    async def generate():
        # TODO: Replace with RAG pipeline + streaming
        async for chunk in llm.astream(request.question):
            if chunk.content:
                yield f"data: {chunk.content}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
