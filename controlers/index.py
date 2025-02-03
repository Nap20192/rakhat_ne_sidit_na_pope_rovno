import json

from langchain_core.documents import Document
from models import Prompt
from utils import *
from assignment4 import collection
class Build:

    def __init__(self, prompt:Prompt, model="llama2",embeding_model = "mxbai-embed-large"):
        self.prompt = prompt
        self.model = model
        self.embeding_model = embeding_model

    def Building(self):
        text = data_load()

        documents = [Document(page_content=i) for i in text]
        split_docs = split_documents(
            documents,
            model_name="gpt-4",
            chunk_size=80,
            chunk_overlap=3
        )
        embeding(split_docs,self.embeding_model,collection)
        imgages = img_load()
        descriptions = response_img(imgages)
        print(descriptions)
        print(generate_response_with_ollama())

if __name__ == "__main__":
    prompt = Prompt("banana fruit")
    build = Build(prompt)
    build.Building()