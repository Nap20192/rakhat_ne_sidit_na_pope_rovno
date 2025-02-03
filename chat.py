import streamlit as st
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage, AIMessage
import chromadb
import json
from web_scraper import search_with_playwright, scrape_data_from_links, download_images
import ollama
import asyncio
import pathlib
from transformers import AutoTokenizer, AutoModel



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



async def concurrence():
    await asyncio.gather(
        data_from_web(prompt, st.session_state.documents, model),
        img_output(file_names)
    )


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
col1, col2 = st.columns(2)
col1.write(f"# :blue[Chat]")
col2.write(f"# :red[Image Description]")

uploaded_files = col1.file_uploader("Upload Files", accept_multiple_files=True)
new_documents = []

if uploaded_files:
    new_documents = process_uploaded_files(uploaded_files)
    if new_documents:
        st.session_state.documents.extend(new_documents)

if new_documents:
    st.write("Documents loaded:")
    for i, doc in enumerate(new_documents):
        st.write(f"Document {i + 1}: {doc[:100]}...")

for message in st.session_state.messages:
    col1.chat_message(message['role']).write(message['content'])

prompt = st.chat_input("Ask a question about the uploaded documents:")

model = st.sidebar.selectbox("Which LLM would you like to use?", ("tinyllama", "llama3", "dolphin-llama3", "llama2"))
use_web = st.sidebar.selectbox("Would you like me to search the web?", ("Yes", "No"))

if prompt:
    col1.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    if use_web == "Yes":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        search_with_playwright(prompt)

        with open("search_results.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        scrape_data_from_links(data['links'])
        d = data_load()

        with open("scraped_data.json", "r", encoding="utf-8") as file:
            scraped_data = json.load(file)

        for data in scraped_data["data"]:
            download_images(data["img_links"])
        print("DOWNLOADED")

        directory = pathlib.Path("img")
        file_names = [file.name for file in directory.rglob("*") if file.is_file()]
        print(file_names)

        asyncio.run(concurrence())

    else:
        ai_reply = generate_response_with_ollama(prompt, model, st.session_state.messages, st.session_state.documents)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        col1.chat_message("assistant").write(ai_reply)



