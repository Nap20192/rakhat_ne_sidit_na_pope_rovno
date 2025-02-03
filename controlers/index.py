import json

from langchain_core.documents import Document
from statsmodels.base.covtype import descriptions

from models import Prompt
from utils import *
from assignment4 import collection
class Build:

    def __init__(self, prompt:Prompt, model="llama2",embeding_model = "mxbai-embed-large"):
        self.prompt = prompt
        self.model = model
        self.embeding_model = embeding_model

    def Building(self):
        unified_scraping_flow(self.prompt)
        webflag, imgflag = self.prompt.get_flags()
        text = data_load()
        documents = [Document(page_content=i) for i in text]
        split_docs = split_documents(
            documents,
            model_name="gpt-4",
            chunk_size=80,
            chunk_overlap=3
        )
        embeding(split_docs,self.embeding_model,collection)
        response = data_from_web(self.prompt,documents,self.model)
        print(response)
        if imgflag:
            imgages = img_load()
            print(imgages)
            descriptions = response_img(imgages)
            return descriptions,response
        else:
            return response


if __name__ == "__main__":
    prompt = Prompt("HENTAI manga",imgflag=True)
    build = Build(prompt)
    build.Building()