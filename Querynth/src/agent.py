from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('sqlite:///analyst.db')
llm = ChatOpenAI(model="gpt-4o")

# Tool for SQL execution
def execute_sql(query, table_name):
    try:
        df = pd.read_sql_query(query, engine)
        return df.to_json(orient='records')  # Return as JSON for LLM
    except Exception as e:
        return f"Error: {e}"

sql_tool = Tool(
    name="execute_sql",
    func=execute_sql,
    description="Execute SQL query on the database. Input: SQL query string and table_name."
)

# Agent prompt
system_prompt = "You are a data analyst. Translate user questions to SQL, execute, and summarize results. Use tools wisely."

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

tools = [sql_tool]  # Add more later
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = create_tool_calling_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True, max_iterations=5)

# Usage
# response = agent_executor.invoke({"input": "Show customers with churn risk > 0.8 from customers table."})