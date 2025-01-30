import streamlit as st
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.schema import HumanMessage, AIMessage
import chromadb
import json
from web_scraper import search_with_playwright, links_scraped_data_with_playwright
import ollama
import asyncio

client = chromadb.Client()
web_collection = client.get_or_create_collection("web_results")
file_collection = client.get_or_create_collection("file_results")

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

def collection_query(prompt, collection):
    response = generate_prompt_embedding(prompt)
    results = collection.query(
        query_embeddings=[response["embedding"]],
        n_results=1
    )
    data = results['documents'][0][0]
    return data

def generate_document_embeddings(documents, collection):
    ollama_embed = OllamaEmbeddings(model='mxbai-embed-large')
    embeddings = ollama_embed.embed_documents(documents)
    collection.add(ids=1, embeddings=embeddings, documents=[documents])

def generate_prompt_embedding(prompt):    
  ollama_embed = OllamaEmbeddings(model='mxbai-embed-large')
  embedding = ollama_embed.embed_query(prompt)
  return embedding
    

def append_msg_history(history, prompt, file_documents, web_documents):
    messages = []
    for msg in history:
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            messages.append(AIMessage(content=msg['content']))
        else:
            raise ValueError(f"Unsupported message type: {msg['role']}")
    
    file_context = "\n".join(file_documents)
    web_context = "\n".join(web_documents)
    prompt_with_context = f"Documents content: {file_context}\n\nData from web: {web_context}\n\nUser's question: {prompt}"
    messages.append(HumanMessage(content=prompt_with_context))
    return messages

def generate_response_with_ollama(prompt, model, history, file_documents, web_documents):
    llm = ChatOllama(model=model, base_url="http://localhost:11434")
    
    messages = append_msg_history(history, prompt, file_documents, web_documents)
    
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





prompt = st.chat_input("Ask a question about the uploaded documents:")


model = st.sidebar.selectbox("Which LLM would you like to use?", ("llama3", "dolphin-llama3", "llama2"))
use_web = st.sidebar.selectbox("Would you like me to search the web?", ("Yes", "No"))


uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True)
new_documents = []

if uploaded_files:
    new_documents = process_uploaded_files(uploaded_files)
    generate_document_embeddings(new_documents, file_collection)
    file_documents = collection_query(prompt, file_collection)
    if new_documents:
        st.session_state.documents.extend(new_documents)
else:
    file_documents = "no file documents"

if new_documents:
    st.write("Documents loaded:")
    for i, doc in enumerate(new_documents):
        st.write(f"Document {i+1}: {doc[:100]}...")


for message in st.session_state.messages:
    st.chat_message(message['role']).write(message['content'])

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

        generate_document_embeddings(d, web_collection)


        web_documents = collection_query(prompt, web_collection)
        ai_reply = generate_response_with_ollama(prompt, st.session_state.messages, model, web_documents, file_documents)
    else:
        web_documents = "no web documents"
        ai_reply = generate_response_with_ollama(prompt, model, st.session_state.messages, file_documents, web_documents)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    st.chat_message("assistant").write(ai_reply)
