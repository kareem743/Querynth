import pytest
from src.ingestion import DataIngestion
import pandas as pd
from sqlalchemy import create_engine, inspect
import os


@pytest.fixture
def temp_ingester(tmp_path):
    db_path = tmp_path / "test.db"
    ingester = DataIngestion(db_url=f'sqlite:///{db_path}')
    yield ingester
    if os.path.exists(db_path):
        os.remove(db_path)


def test_ingest_csv(temp_ingester, tmp_path):
    csv_path = tmp_path / "test.csv"
    df = pd.DataFrame({'id': [1, 2], 'name': ['Alice', 'Bob']})
    df.to_csv(csv_path, index=False)

    table_name = temp_ingester.ingest_csv(csv_path)
    assert table_name == 'test'

    inspector = inspect(temp_ingester.engine)
    assert 'test' in inspector.get_table_names()

    result_df = pd.read_sql_table('test', temp_ingester.engine)
    pd.testing.assert_frame_equal(result_df, df)


def test_ingest_error(temp_ingester, tmp_path):
    invalid_path = tmp_path / "nonexistent.csv"
    with pytest.raises(Exception):
        temp_ingester.ingest_csv(invalid_path)