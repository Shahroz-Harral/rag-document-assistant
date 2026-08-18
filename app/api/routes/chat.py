"""
RAG Document Assistant — Chat Routes

Handles question answering over indexed documents with multi-turn memory and streaming support.
"""

import json
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
    3. Generate answer using LLM with context & chat history
    4. Validate output through Guardrails AI
    5. Return answer with source citations & session_id
    """
    rag_result = await anyio.to_thread.run_sync(
        ask_question, request.question, request.top_k, request.session_id
    )
    answer = rag_result["answer"]

    if request.use_guardrails:
        answer = validate_response(answer)

    return ChatResponse(
        answer=answer,
        sources=rag_result["sources"],
        model="Groq/Gemini-Fallback",
        session_id=rag_result["session_id"],
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Ask a question with streaming response (Server-Sent Events).
    Yields:
    - metadata event containing sources & session_id
    - token events containing answer chunks
    - done event
    """
    async def generate():
        async for event in ask_question_stream(
            question=request.question,
            top_k=request.top_k,
            session_id=request.session_id
        ):
            payload = json.dumps(event)
            yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
