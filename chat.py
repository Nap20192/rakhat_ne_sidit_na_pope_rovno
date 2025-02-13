import streamlit as st
import asyncio
import json
import pathlib
from controlers import Build
from models import Prompt
from utils import *
import traceback

from utils.preprocessing import filter_swear_words
from utils.telegram_message import send_telegram_notification

# Page configuration
st.set_page_config(page_title="Munchkin the chatbot", layout="wide")

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
    'image_descriptions': {},
    'telegram_id': '2140322165'
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

history = history_load()
print(history)


img_history = img_history_load()
print(img_history)
st.session_state.image_descriptions = img_history

# Display chat history
for message in st.session_state.messages:
    col1.chat_message(message['role']).write(filter_swear_words(message['content']))

for img, desc in st.session_state.image_descriptions.items():
    col2.image(f"./img/{img}")
    col2.write(f"**{img}**: {filter_swear_words(desc)}")

# Sidebar controls
model = st.sidebar.selectbox(
    "Which LLM would you like to use?",
    ("tinyllama", "llama3", "dolphin-llama3", "llama2")
)
use_web = st.sidebar.selectbox(
    "Would you like me to search the web?",
    ("Yes", "No")
)

find_images = st.sidebar.selectbox(
    "Would you like me to find images according to your query?",
    ("Yes", "No")
)

st.session_state.messages = history
telegram_id = st.sidebar.text_input("Enter your telegram id")
if telegram_id:
    st.session_state.telegram_id = telegram_id

st.sidebar.write("Your telegram id is", st.session_state.telegram_id)

if st.sidebar.button("Clear history"):
    st.session_state.messages = []
    st.session_state.documents = []
    st.session_state.image_descriptions = {}
    history_clear()
    st.rerun()

# Chat input

prompt = st.chat_input("Ask a question about the uploaded documents:")
if prompt:
    censored_prompt = filter_swear_words(prompt)
    col1.chat_message("user").write(censored_prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        prompt_model = Prompt(text=prompt)
        if use_web == "Yes":
            prompt_model.webflag = True

        if find_images == "Yes":
            prompt_model.imgflag = True

        if uploaded_files:
            prompt_model.fileflag = True

        builder = Build(prompt=prompt_model, model=model, history=st.session_state.messages)

        if prompt_model.fileflag:
            builder.file_documents = st.session_state.documents

        if prompt_model.webflag:
            if prompt_model.imgflag:
                image_descriptions, ai_reply = builder.building()
                st.session_state.image_descriptions.update(image_descriptions)
                img_history_save(st.session_state.image_descriptions)
                print(st.session_state.image_descriptions)
                print(img_history_load())
            else:
                ai_reply = builder.building()
        else:
            ai_reply = builder.building()

        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

        history_save(st.session_state.messages)


        col1.chat_message("assistant").write(filter_swear_words(ai_reply))
        send_telegram_notification(chat_id=st.session_state.telegram_id)
        try:
            for img, desc in st.session_state.image_descriptions.items():
                col2.image(f"./img/{img}")
                col2.write(f"**{img}**: {filter_swear_words(desc)}")
        except NameError:
            pass




    except Exception as e:
        send_telegram_notification(success=False, chat_id=st.session_state.telegram_id)
        tb = traceback.extract_tb(e.__traceback__)
        filename, line, func, text = tb[-1]
        error_msg = f"Error in {filename}, line {line}, in {func}(): {str(e)}"
        print(error_msg)
        st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})