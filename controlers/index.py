import json

from langchain_core.documents import Document
from statsmodels.base.covtype import descriptions
import asyncio
import streamlit as st

from models import Prompt
from utils import *

class Build:

    def __init__(self, prompt:Prompt, model="llama2-uncensored",embeding_model = "mxbai-embed-large"):
        self.prompt = prompt
        self.model = model
        self.embeding_model = embeding_model

    def building(self):
        unified_scraping_flow(self.prompt)
        webflag, imgflag, fileflag = self.prompt.get_flags()
        text = data_load()
        documents = [Document(page_content=i) for i in text]
        if fileflag:
            documents.extend(st.session_state.documents)
        split_docs = split_documents(
            documents,
            model_name="gpt-4",
            chunk_size=80,
            chunk_overlap=3
        )
        embeding(split_docs,self.embeding_model,collection)

        if imgflag:
            images = img_load()
            print(images)
            response, descriptions = asyncio.run(concurrent_generation(self.prompt, documents, self.model, images))
            return descriptions, response
        else:
            response = data_from_web(self.prompt, documents, self.model)
            print(response)
            return response


# def main():
#     prompt = Prompt("Who is the president of us?",imgflag=True)
#     build = Build(prompt)
#     build.building()
#
# if __name__ == "__main__":
#     main()