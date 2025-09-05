from ingestion import DataIngestion
from agent import agent_executor
import click  # For CLI

@click.command()
@click.option('--csv', help='Path to CSV')
@click.option('--query', help='Natural language query')
def main(csv, query):
    ingester = DataIngestion()
    if csv:
        table = ingester.ingest_csv(csv)
    response = agent_executor.invoke({"input": query})
    print(response['output'])

if __name__ == '__main__':
    main()