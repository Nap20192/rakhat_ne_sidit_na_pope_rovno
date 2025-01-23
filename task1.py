import streamlit as st
from langchain.chat_models import ChatOllama
from langchain.schema import HumanMessage, AIMessage
import chromadb
import sqlite3
import json
from web_scraper import search_with_playwright, links_scraped_data_with_playwright
import ollama
import asyncio

client = chromadb.Client()
collection = client.get_or_create_collection("search_result")

def data_load():
    with open("scraped_data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data = data["data"]
    text = []
    for item in data:
        for it in item["data"]:
            text.append(it)
    print(len(text))
    return text

def data_from_web(prompt, mod="llama3"):
    response = ollama.embeddings(
        prompt=prompt,
        model="mxbai-embed-large"
    )
    results = collection.query(
        query_embeddings=[response["embedding"]],
        n_results=1
    )
    data = results['documents'][0][0]
    output = ollama.generate(
        model=mod,
        prompt=f"Using this data: {data}. Respond to this prompt: {prompt}"
    )
    return output['response']

def generate_embeddings(data):
    for i, d in enumerate(data):
        response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
        embedding = response["embedding"]
        collection.add(
            ids=[str(i)],
            embeddings=[embedding],
            documents=[d]
        )

def generate_response_with_ollama(prompt, model, history, embedding_model, collection):
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

    # Embed the prompt to enhance query understanding
    try:
        embedding_response = ollama.embeddings(
            prompt=prompt,
            model=embedding_model  # Specify the embedding model
        )
        embedded_query = embedding_response["embedding"]

        # Query the document collection with the embedded query
        results = collection.query(
            query_embeddings=[embedded_query],
            n_results=3  # Adjust the number of relevant documents to retrieve
        )
        relevant_documents = [doc[0] for doc in results["documents"]]
    except Exception as e:
        st.error(f"An error occurred during embedding or document retrieval: {e}")
        return "An error occurred while processing your request. Please check your embedding model or data setup."

    # Add the current user input with relevant document context
    context = "\n".join(relevant_documents)
    prompt_with_context = f"Documents content: {context}\n\nUser's question: {prompt}"
    messages.append(HumanMessage(content=prompt_with_context))

    # Generate a response
    try:
        response = llm(messages)  # Passing all formatted messages to the model
        return response.content
    except ValueError as e:
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
if 'i' not in st.session_state:
    st.session_state.i = 0
if 'embedding_processed' not in st.session_state:
    st.session_state.embedding_processed = False
if 'added_embeddings' not in st.session_state:
    st.session_state.added_embeddings = set()
if 'chunks' not in st.session_state:
    st.session_state.chunks = []

# Input for querying from the internet
query = st.text_input("Enter a query to search the internet:")

if query:
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    search_with_playwright(query)

    with open("search_results.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    print(data)

    links_scraped_data_with_playwright(data['links'])
    d = data_load()
    generate_embeddings(d)

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
model = st.sidebar.selectbox("Which LLM would you like to use?", ("llama3", "dolphin-llama3", "llama2"))  # Specify ChatOllama-compatible models

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    ai_reply = data_from_web(prompt,model)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    st.chat_message("assistant").write(ai_reply)
