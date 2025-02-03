import streamlit as st
import asyncio
import json
import pathlib
from controlers import Build
from models import Prompt
from utils import *

# Page configuration
st.set_page_config(page_title="Document Query System with LangChain (ChatOllama)", layout="wide")

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

# Initialize session state
session_state_defaults = {
    'documents': [],
    'messages': [],
    'i': 0,
    'embedding_processed': False,
    'added_embeddings': set(),
    'chunks': [],
    'image_descriptions': {}
}
for key, value in session_state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Create columns
col1, col2 = st.columns(2)
col1.write("# :blue[Chat]")
col2.write("# :red[Image Description]")

# File uploader
uploaded_files = col1.file_uploader("Upload Files", accept_multiple_files=True)
if uploaded_files:
    new_documents = process_uploaded_files(uploaded_files)
    if new_documents:
        st.session_state.documents.extend(new_documents)
        col1.write("Documents loaded:")
        for i, doc in enumerate(new_documents):
            col1.write(f"Document {i + 1}: {doc[:100]}...")

# Display chat history
for message in st.session_state.messages:
    col1.chat_message(message['role']).write(message['content'])

# Sidebar controls
model = st.sidebar.selectbox(
    "Which LLM would you like to use?",
    ("tinyllama", "llama3", "dolphin-llama3", "llama2")
)
use_web = st.sidebar.selectbox(
    "Would you like me to search the web?",
    ("Yes", "No")
)

# Chat input
prompt = col1.chat_input("Ask a question about the uploaded documents:")
if prompt:
    # Add user message to chat
    col1.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Initialize controller
        prompt_model = Prompt(content=prompt, documents=st.session_state.documents)
        builder = Build(prompt=prompt_model, model=model)

        # Handle web search if needed
        if use_web == "Yes":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            search_with_playwright(prompt)
            scrape_data_from_links(data_load().get('links', []))
            download_images(data_load().get('img_links', []))
            asyncio.run(concurrence())

        image_descriptions, ai_reply = builder.Building()
        st.session_state.image_descriptions.update(image_descriptions)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        col1.chat_message("assistant").write(ai_reply)
        for img, desc in image_descriptions.items():
            col2.write(f"**{img}**: {desc}")

    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        col1.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})