import json

from langchain_core.documents import Document
from statsmodels.base.covtype import descriptions
import asyncio
import streamlit as st

from models import Prompt
from utils import *
from utils.preprocessing import filter_swear_words
from utils.telegram_message import send_telegram_notification


class Build:

    def __init__(self, prompt:Prompt, history, model="llama2-uncensored",embeding_model = "mxbai-embed-large", file_documents=""):
        self.prompt = prompt
        self.model = model
        self.embeding_model = embeding_model
        self.history = history
        self.file_documents = file_documents

    def building(self):
        webflag, imgflag, fileflag = self.prompt.get_flags()

        if fileflag:
            self.file_documents = []
            self.file_documents.extend(st.session_state.documents)

        if webflag:
            unified_scraping_flow(self.prompt)
            text = data_load()
            web_data = [Document(page_content=i) for i in text]
            split_docs = split_documents(
                web_data,
                model_name="gpt-4",
                chunk_size=80,
                chunk_overlap=3
            )

            embeding(split_docs, self.embeding_model, collection)
            if imgflag:
                images = img_load()
                print(images)
                response, descriptions = asyncio.run(concurrent_generation(self.prompt, self.history, self.file_documents, self.model, images, web_data))
                return descriptions, response
            else:
                response = asyncio.run(data_from_web(self.prompt, self.file_documents, self.model, self.history, web_data))
                print(response)

        else:
            response = asyncio.run(generate_response_with_ollama(self.prompt, self.model, self.history, self.file_documents))
            print(response)

        return response


# def main():
#     prompt = Prompt("Who is the president of us?",imgflag=True)
#     build = Build(prompt)
#     build.building()
#
# if __name__ == "__main__":
#     main()