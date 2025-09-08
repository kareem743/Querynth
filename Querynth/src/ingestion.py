import logging
import pandas as pd
from sqlalchemy import create_engine, inspect
from pathlib import Path
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestion:
    def __init__(self, db_url='sqlite:///analyst.db'):
        self.engine = create_engine(db_url)

    def ingest_csv(self, csv_input, table_name=None):
        try:
            # Case 1: Streamlit UploadedFile or file-like object
            if hasattr(csv_input, "read"):
                df = pd.read_csv(csv_input)
                if table_name is None:
                    table_name = Path(csv_input.name).stem  # Streamlit gives .name
            else:
                # Case 2: Normal file path
                csv_path = Path(csv_input)
                df = pd.read_csv(csv_path)
                if table_name is None:
                    table_name = csv_path.stem

            # Store into SQL
            df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            logger.info(f"Ingested into table '{table_name}'")
            return table_name

        except Exception as e:
            logger.error(f"Ingestion error: {e}")
            raise

    def list_tables(self):
        inspector = inspect(self.engine)
        return inspector.get_table_names()
