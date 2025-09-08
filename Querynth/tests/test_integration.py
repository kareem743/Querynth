import pytest
from src.ingestion import DataIngestion
from src.agent import agent_executor
import pandas as pd
import os

@pytest.fixture(scope="module")
def setup_integration(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("data") / "integration.db"
    ingester = DataIngestion(db_url=f'sqlite:///{db_path}')
    csv_path = tmp_path_factory.mktemp("data") / "integration.csv"
    df = pd.DataFrame({'id': [1], 'value': [10]})
    df.to_csv(csv_path, index=False)
    table = ingester.ingest_csv(csv_path)
    yield ingester, table
    os.remove(db_path)

def test_end_to_end(setup_integration):
    ingester, table = setup_integration
    response = agent_executor.invoke({"input": f"Sum values from {table}"})
    assert "10" in response['output']  # Assuming agent summarizes sum