"""
RAG Document Assistant — Hallucination Tests (DeepEval)

Run with: deepeval test run tests/test_hallucination.py
"""

# TODO: Implement once RAG pipeline is built
#
# from deepeval import assert_test
# from deepeval.test_case import LLMTestCase
# from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
#
# def test_faithfulness():
#     """Test that answers are grounded in source documents."""
#     faithfulness = FaithfulnessMetric(threshold=0.7)
#     test_case = LLMTestCase(
#         input="What is our refund policy?",
#         actual_output="Our refund policy allows returns within 30 days.",
#         retrieval_context=["Refund policy: Returns accepted within 30 days of purchase."]
#     )
#     assert_test(test_case, [faithfulness])
#
# def test_answer_relevancy():
#     """Test that answers are relevant to the question asked."""
#     relevancy = AnswerRelevancyMetric(threshold=0.7)
#     test_case = LLMTestCase(
#         input="What are the shipping costs?",
#         actual_output="Shipping is free for orders over $50.",
#         retrieval_context=["Free shipping on orders above $50. Standard shipping: $5.99."]
#     )
#     assert_test(test_case, [relevancy])
