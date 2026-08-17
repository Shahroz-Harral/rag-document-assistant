from typing import AsyncGenerator, Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.vectorstore import get_vectorstore
from app.core.llm import get_llm

RAG_PROMPT_TEMPLATE = """Answer the question based ONLY on the following context.
If you cannot answer the question based on the context, say "I don't know based on the provided documents."

Context:
{context}

Question: {question}
"""


def _format_docs(docs: List[Any]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def ask_question(question: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Executes the full RAG pipeline synchronously:
    1. Embeds question and retrieves top_k document chunks from Pinecone.
    2. Formats prompt with context.
    3. LLM generates answer based on context.
    4. Returns answer and source chunk metadata.
    """
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    docs = retriever.invoke(question)
    context_str = _format_docs(docs)

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context_str, "question": question})

    sources = [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page"),
            "score": float(doc.metadata.get("score", 1.0)),
        }
        for doc in docs
    ]

    return {"answer": answer, "sources": sources}


async def ask_question_stream(question: str, top_k: int = 5) -> AsyncGenerator[str, None]:
    """
    Executes the full streaming RAG pipeline:
    Retrieves context asynchronously and streams LLM output tokens.
    """
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    docs = await retriever.ainvoke(question)
    context_str = _format_docs(docs)

    chain = prompt | llm | StrOutputParser()

    async for chunk in chain.astream({"context": context_str, "question": question}):
        if chunk:
            yield chunk

