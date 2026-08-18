"""
RAG Document Assistant — Output Validation

Simple pass-through validation. Guardrails AI was removed because the package
triggers filesystem operations (NLTK data, hub registry, config files) that are
incompatible with Vercel's read-only serverless environment.
"""

import logging

logger = logging.getLogger(__name__)


def validate_response(llm_output: str) -> str:
    """
    Returns the LLM output as-is.

    Previously used Guardrails AI for PII detection, but the package's
    heavy dependencies caused FileNotFoundError on serverless platforms.
    """
    return llm_output
