import pandas as pd
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestion:
    def __init__(self, db_url='sqlite:///analyst.db'):
        self.engine = create_engine(db_url)

    def ingest_csv(self, csv_path, table_name=None):
        try:
            df = pd.read_csv(csv_path)
            if table_name is None:
                table_name = csv_path.stem  # Use filename as table name
            df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            logger.info(f"Ingested {csv_path} into table '{table_name}'")
            return table_name
        except Exception as e:
            logger.error(f"Ingestion error: {e}")
            raise

    def list_tables(self):
        inspector = inspect(self.engine)
        return inspector.get_table_names()

# Usage example
# ingester = DataIngestion()
# table = ingester.ingest_csv('sales_data.csv')