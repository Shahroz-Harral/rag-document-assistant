"""
RAG Document Assistant — Output Guardrails

Validates LLM responses to prevent hallucinations, PII leaks, and off-topic content.
Uses Guardrails AI for runtime output validation.
"""

# TODO: Configure Guardrails AI validators once the RAG pipeline is built.
#
# Example setup:
#
# from guardrails import Guard
# from guardrails.hub import DetectPII, ToxicLanguage
#
# guard = Guard().use_many(
#     DetectPII(pii_entities=["EMAIL", "PHONE"]),
#     ToxicLanguage(threshold=0.8),
# )
#
# result = guard(
#     llm_api=llm.invoke,
#     prompt="..."
# )
