import pytest
from src.rag import rag_chain

def test_rag_query():
    result = rag_chain.run("Explain churn_risk column")
    assert "Probability" in result  # Based on sample docs