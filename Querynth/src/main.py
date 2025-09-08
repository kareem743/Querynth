import streamlit as st
from src.ingestion import DataIngestion
from src.agent import agent_executor
import pandas as pd
import os

# Initialize session state
if 'ingester' not in st.session_state:
    st.session_state.ingester = DataIngestion(db_url='sqlite:///analyst.db')
if 'tables' not in st.session_state:
    st.session_state.tables = st.session_state.ingester.list_tables()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Streamlit App
st.title("Data Analyst Assistant")

# Sidebar for CSV Upload
with st.sidebar:
    st.header("Upload CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_path = os.path.join("temp", uploaded_file.name)
        os.makedirs("temp", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        try:
            table_name = st.session_state.ingester.ingest_csv(temp_path)
            st.session_state.tables = st.session_state.ingester.list_tables()
            st.success(f"Ingested {uploaded_file.name} as table '{table_name}'")
        except Exception as e:
            st.error(f"Error ingesting file: {e}")
        finally:
            os.remove(temp_path)  # Clean up

    # Display available tables
    st.header("Available Tables")
    for table in st.session_state.tables:
        st.write(f"- {table}")

# Main Chat Interface
st.header("Ask Questions about Your Data")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "df" in message:
            st.dataframe(message["df"])
        if "plot_path" in message:
            st.image(message["plot_path"])

# User input
user_query = st.chat_input("Type your question here (e.g., 'Show customers with churn risk > 0.8')")

if user_query:
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Run agent
    with st.spinner("Analyzing..."):
        try:
            tables_str = ', '.join(st.session_state.tables)
            full_input = f"Available tables: {tables_str}\nUser query: {user_query}"
            response = agent_executor.invoke({"input": full_input})
            output = response['output']

            # Add assistant response
            assistant_msg = {"role": "assistant", "content": output}

            # Parse for tables/plots if agent returns them (customize based on agent output)
            if "dataframe" in response:  # Assume agent might return JSON or dict
                df = pd.read_json(response["dataframe"])
                assistant_msg["df"] = df
            if "plot_path" in response:
                assistant_msg["plot_path"] = response["plot_path"]

            st.session_state.chat_history.append(assistant_msg)

            with st.chat_message("assistant"):
                st.markdown(output)
                if "df" in assistant_msg:
                    st.dataframe(assistant_msg["df"])
                if "plot_path" in assistant_msg:
                    st.image(assistant_msg["plot_path"])
        except Exception as e:
            st.error(f"Error: {e}")