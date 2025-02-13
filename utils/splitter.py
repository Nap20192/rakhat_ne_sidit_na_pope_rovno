from random import random
import string
from transformers import AutoTokenizer

from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

def split_documents(
    documents: list[Document],
    model_name: str = "gpt-4",
    chunk_size: int = 100,
    chunk_overlap: int = 20
) -> list[Document]:

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        model_name=model_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separator=" "  # Avoid splitting mid-word
    )
    split_docs = text_splitter.split_documents(documents)
    print("Split documents:")
    print(split_docs)
    return split_docs
