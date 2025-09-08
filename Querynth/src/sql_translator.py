from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from sqlalchemy import text
import sqlparse  # For validation

llm = ChatOpenAI(model="gpt-4o", api_key=)  # Or use xAI's API equivalent

SCHEMA_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template="""Based on the table schema: {schema}
    Translate this question to SQL: {question}
    Return only the SQL query, no explanations."""
)


def get_schema(engine, table_name):
    with engine.connect() as conn:
        result = conn.execute(text(f"PRAGMA table_info({table_name});"))  # For SQLite; adjust for PG
        return [row for row in result]


def translate_to_sql(engine, table_name, question):
    schema = get_schema(engine, table_name)
    chain = SCHEMA_PROMPT | llm
    sql_query = chain.invoke({"schema": schema, "question": question}).content.strip()

    # Validate
    try:
        sqlparse.parse(sql_query)  # Basic syntax check
        return sql_query
    except Exception:
        raise ValueError("Invalid SQL generated")