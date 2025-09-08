import pytest
from src.sql_translator import translate_to_sql, get_schema
from sqlalchemy import create_engine
from unittest.mock import patch


@pytest.fixture
def mock_engine():
    engine = create_engine('sqlite:///:memory:')
    engine.execute("CREATE TABLE test (id INTEGER, churn_risk FLOAT)")
    return engine


@patch('src.sql_translator.llm')  # Mock LLM to avoid real calls
def test_translate_to_sql(mock_llm, mock_engine):
    mock_llm.invoke.return_value.content = "SELECT * FROM test WHERE churn_risk > 0.8"

    sql = translate_to_sql(mock_engine, 'test', "Show customers with churn risk > 0.8")
    assert "SELECT * FROM test WHERE churn_risk > 0.8" in sql


def test_get_schema(mock_engine):
    schema = get_schema(mock_engine, 'test')
    assert len(schema) == 2  # id and churn_risk


def test_invalid_sql(mock_engine):
    with pytest.raises(ValueError):
        translate_to_sql(mock_engine, 'test', "Invalid query that generates bad SQL")
    # Adjust mock to return invalid SQL for this test