from typing import AsyncGenerator, Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.vectorstore import get_vectorstore
from app.services.memory import memory_manager
from app.core.llm import get_llm

RAG_PROMPT_TEMPLATE = """Answer the question based ONLY on the following context, considering prior conversation history if relevant.
If you cannot answer the question based on the context, say "I don't know based on the provided documents."

Prior Conversation History:
{chat_history}

Context:
{context}

Question: {question}
"""


def _format_docs(docs: List[Any]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def ask_question(question: str, top_k: int = 5, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes the full RAG pipeline synchronously:
    1. Embeds question and retrieves top_k document chunks from Pinecone.
    2. Formats prompt with context and prior conversation history.
    3. LLM generates answer based on context and history.
    4. Records turn in session memory.
    5. Returns answer, session_id, and source chunk metadata.
    """
    if not session_id:
        session_id = memory_manager.generate_session_id()

    chat_history_str = memory_manager.format_history_for_prompt(session_id)

    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    docs = retriever.invoke(question)
    context_str = _format_docs(docs)

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({
        "chat_history": chat_history_str,
        "context": context_str,
        "question": question
    })

    memory_manager.add_turn(session_id, question, answer)

    sources = [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page"),
            "score": float(doc.metadata.get("score", 1.0)),
        }
        for doc in docs
    ]

    return {
        "answer": answer,
        "sources": sources,
        "session_id": session_id
    }


async def ask_question_stream(
    question: str, top_k: int = 5, session_id: Optional[str] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Executes the full streaming RAG pipeline:
    1. Retrieves context asynchronously.
    2. Yields initial 'metadata' dictionary containing sources & session_id.
    3. Yields token text chunks.
    4. Records turn in session memory upon completion.
    """
    if not session_id:
        session_id = memory_manager.generate_session_id()

    chat_history_str = memory_manager.format_history_for_prompt(session_id)

    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    docs = await retriever.ainvoke(question)
    context_str = _format_docs(docs)

    sources = [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page"),
            "score": float(doc.metadata.get("score", 1.0)),
        }
        for doc in docs
    ]

    # First yield metadata packet
    yield {"type": "metadata", "sources": sources, "session_id": session_id}

    chain = prompt | llm | StrOutputParser()
    full_answer_chunks = []

    async for chunk in chain.astream({
        "chat_history": chat_history_str,
        "context": context_str,
        "question": question
    }):
        if chunk:
            full_answer_chunks.append(chunk)
            yield {"type": "token", "content": chunk}

    full_answer = "".join(full_answer_chunks)
    memory_manager.add_turn(session_id, question, full_answer)
