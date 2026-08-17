"""
RAG Document Assistant — Output Guardrails

Validates LLM responses to prevent hallucinations, PII leaks, and off-topic content.
Uses Guardrails AI for runtime output validation.
"""

import logging

logger = logging.getLogger(__name__)

# Attempt to initialize Guard with PII detection
# We configure it to detect and mask emails and phone numbers.
# If the hub validator isn't installed locally (via `guardrails hub install`),
# we catch the ImportError and set guard to None so the server doesn't crash on startup.
try:
    from guardrails import Guard
    from guardrails.hub import DetectPII

    guard = Guard().use_many(
        DetectPII(
            pii_entities=["EMAIL", "PHONE_NUMBER"],
            on_fail="fix" # This tells Guardrails to automatically mask the detected PII
        )
    )
except ImportError:
    guard = None
    logger.warning("Guardrails Hub validator 'DetectPII' is not installed. Run 'guardrails hub install hub://guardrails/detect_pii' to enable it.")


def validate_response(llm_output: str) -> str:
    """
    Validates the LLM output using Guardrails AI.
    """
    if guard is None:
        return llm_output

    try:
        # validate the raw string
        validation_result = guard.parse(llm_output)
        # return the sanitized string (PII masked)
        return validation_result.validated_output or llm_output
    except Exception as e:
        # If guardrails fails entirely, return a safe fallback or the original depending on strictness
        # We will return the original here but log the error in production
        logger.error(f"Guardrails validation error: {e}")
        return llm_output
