import json

from langchain_core.documents import Document

from models import Prompt
from utils import unified_scraping_flow, split_documents,data_load,embeding


class Build:

    def __init__(self, prompt:Prompt, model="llama2",embeding_model = "mxbai-embed-large"):
        self.prompt = prompt
        self.model = model
        self.embeding_model = embeding_model

    def Building(self):
        unified_scraping_flow(self.prompt)
        text = data_load()
        documents = [Document(page_content=i) for i in text]
        split_docs = split_documents(
            documents,
            model_name="gpt-4",
            chunk_size=20,
            chunk_overlap=10
        )
        embeding(split_docs, self.embeding_model)


if __name__ == "__main__":
    prompt = Prompt("banana fruit")
    build = Build(prompt)
    build.Building()