from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA

embeddings = OpenAIEmbeddings()

# Sample docs: List of strings like "Column sales: Monthly revenue in USD"
docs = [...]  # Load from a file or generate from schema
vectorstore = FAISS.from_texts(docs, embeddings)

rag_chain = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever())

# Integrate into agent: Before translating SQL, query RAG for context
context = rag_chain.run("Explain columns for sales table")