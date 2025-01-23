import streamlit as st
from langchain.chat_models import ChatOllama
from langchain.schema import HumanMessage, AIMessage
import chromadb
import sqlite3
import json
from web_scraper import search_with_playwright,links_scraped_data_with_playwright
import ollama

client = chromadb.Client()
collection = client.create_collection("search_results")

def data_load():
    with open("scraped_data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data = data["data"]
    text = []
    for item in data:
        text.append(item["data"])
    return text

def data_from_web(query):
    response = ollama.embeddings(
        prompt=query,
        model="mxbai-embed-large"
    )
    results = collection.query(
        query_embeddings=[response["embedding"]],
        n_results=1
    )
    data = results['documents'][0][0]
    return data

def generate_embeddings(data):
    for chunk in data:
        response = ollama.embeddings(model="mxbai-embed-large", prompt=chunk)
        embedding = response["embedding"]
        collection.add(
            ids=[str(st.session_state.i)], 
            embeddings=[embedding],
            documents=[chunk]
        )
        st.session_state.i+=1
        st.write(chunk)


def generate_response_with_ollama(prompt, model, history, documents):
    # Configure LangChain's ChatOllama model
    llm = ChatOllama(model=model, base_url="http://localhost:11434")  # Replace with your Ollama server URL if different
    # Convert session state history into LangChain's message types
    messages = []
    for msg in history:
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            messages.append(AIMessage(content=msg['content']))
        else:
            raise ValueError(f"Unsupported message type: {msg['role']}")

    # Add the current user input with document context
    context = "\n".join(documents)
    prompt_with_context = f"Documents content: {context}\n\nUser's question: {prompt}"
    messages.append(HumanMessage(content=prompt_with_context))

    # Generate a response
    try:
        response = llm(messages)  # Passing all formatted messages to the model
        return response.content
    except ValueError as e:
        # Catch unsupported message errors or other exceptions
        st.error(f"An error occurred while communicating with the Ollama model: {e}")
        return "An error occurred while processing your request. Please check your input or model setup."

def process_uploaded_files(uploaded_files):
    documents = []
    for uploaded_file in uploaded_files:
        if uploaded_file.type.startswith("text/"):
            file_contents = uploaded_file.getvalue().decode("utf-8")
            documents.append(file_contents)
        else:
            st.warning(f"File '{uploaded_file.name}' is not in text format, cannot process.")
            documents.append(f"Unable to process file '{uploaded_file.name}'")
    return documents

st.set_page_config(page_title="Document Query System with LangChain (ChatOllama)", layout="wide")

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'messages' not in st.session_state:
    st.session_state.messages = []

query = st.text_input("Enter a query to search the internet:")

if query:
    search_with_playwright(query)

    with open("search_results.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    print(data)

    links_scraped_data_with_playwright(data['links'])
# File uploader section
uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True)
new_documents = []

if uploaded_files:
    new_documents = process_uploaded_files(uploaded_files)
    if new_documents:
        st.session_state.documents.extend(new_documents)

if new_documents:
    st.write("Documents loaded:")
    for i, doc in enumerate(new_documents):
        st.write(f"Document {i+1}: {doc[:100]}...")

# Display chat messages
for message in st.session_state.messages:
    st.chat_message(message['role']).write(message['content'])

# Chat input section
prompt = st.chat_input("Ask a question about the uploaded documents:")

# Sidebar for model selection
model = st.sidebar.selectbox("Which LLM would you like to use?", ("llama2", "dolphin-llama3","llama3"))  # Specify ChatOllama-compatible models

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    ai_reply = generate_response_with_ollama(prompt, model, st.session_state.messages, st.session_state.documents)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    st.chat_message("assistant").write(ai_reply)
