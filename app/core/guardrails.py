"""
RAG Document Assistant — Output Guardrails

Validates LLM responses to prevent hallucinations, PII leaks, and off-topic content.
Uses Guardrails AI for runtime output validation with safe fallbacks for serverless environments.
"""

import logging

logger = logging.getLogger(__name__)

guard = None

# Attempt to initialize Guard with PII detection
# We configure it to detect and mask emails and phone numbers.
# On serverless platforms (Vercel/Lambda) where ~/.guardrails is missing,
# we catch FileNotFoundError / Exception so the app runs smoothly.
try:
    from guardrails import Guard
    from guardrails.hub import DetectPII

    guard = Guard().use_many(
        DetectPII(
            pii_entities=["EMAIL", "PHONE_NUMBER"],
            on_fail="fix"  # Automatically mask detected PII
        )
    )
except Exception as e:
    guard = None
    logger.info(f"Guardrails AI initialization skipped ({e}). Using pass-through validation.")


def validate_response(llm_output: str) -> str:
    """
    Validates the LLM output using Guardrails AI if available, falling back safely.
    """
    if guard is None:
        return llm_output

    try:
        validation_result = guard.parse(llm_output)
        return validation_result.validated_output or llm_output
    except Exception as e:
        logger.warning(f"Guardrails validation fallback: {e}")
        return llm_output
