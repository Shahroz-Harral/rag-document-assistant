"""
RAG Document Assistant — Chat Routes

Handles question answering over indexed documents.
"""

import anyio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag import ask_question, ask_question_stream
from app.core.guardrails import validate_response

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
    rag_result = await anyio.to_thread.run_sync(
        ask_question, request.question, request.top_k
    )
    answer = rag_result["answer"]

    if request.use_guardrails:
        answer = validate_response(answer)

    return ChatResponse(
        answer=answer,
        sources=rag_result["sources"],
        model="Groq/Gemini-Fallback",
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Ask a question with streaming response (Server-Sent Events).
    """
    async def generate():
        async for chunk in ask_question_stream(request.question, top_k=request.top_k):
            safe_chunk = chunk.replace("\n", "\\n")
            yield f"data: {safe_chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

