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
    # print(len(text))
    return text

def data_from_web(prompt, documents, model):
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
        model=model,
        prompt=f"Using this document data: {documents} and using this web data: {data}. Respond to this prompt: {prompt}"
    )
    return output['response']

def generate_embeddings(data):
    for i, d in enumerate(data):
        response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
        embedding = response["embedding"]
        print(f"IDs: {len(str(i))}, Embeddings: {len(embedding)}, Documents: {len(d)}")
        try:
            collection.add(
                ids=[str(i)],
                embeddings=[embedding],
                documents=[d]
            )
        except:
            continue

def generate_response_with_ollama(prompt, model, history, documents):
    llm = ChatOllama(model=model, base_url="http://localhost:11434")
    
    messages = []
    for msg in history:
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            messages.append(AIMessage(content=msg['content']))
        else:
            raise ValueError(f"Unsupported message type: {msg['role']}")
    
    context = "\n".join(documents)
    prompt_with_context = f"Documents content: {context}\n\nUser's question: {prompt}"
    messages.append(HumanMessage(content=prompt_with_context))

    try:
        response = llm(messages)
        return response.content
    except ValueError as e:
        st.error(f"An error occurred while communicating with the Ollama model: {e}")
        return "An error occurred while processing your request."

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
# query = st.text_input("Enter a query to search the internet:")

# if query:
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
#     search_with_playwright(query)

#     with open("search_results.json", "r", encoding="utf-8") as file:
#         data = json.load(file)
#     print(data)

#     links_scraped_data_with_playwright(data['links'])
#     d = data_load()
#     generate_embeddings(d)

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


for message in st.session_state.messages:
    st.chat_message(message['role']).write(message['content'])


prompt = st.chat_input("Ask a question about the uploaded documents:")


model = st.sidebar.selectbox("Which LLM would you like to use?", ("llama3", "dolphin-llama3", "llama2"))
use_web = st.sidebar.selectbox("Would you like me to search the web?", ("Yes", "No"))

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    if use_web == "Yes":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        search_with_playwright(prompt)

        with open("search_results.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        print(data)

        links_scraped_data_with_playwright(data['links'])
        d = data_load()
        generate_embeddings(d)
        ai_reply = data_from_web(prompt, st.session_state.documents, model)
    else:
        ai_reply = generate_response_with_ollama(prompt, model, st.session_state.messages, st.session_state.documents)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    st.chat_message("assistant").write(ai_reply)
