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
    # Split documents and preserve metadata
    split_docs = text_splitter.split_documents(documents)
    print("Split documents:")
    print(split_docs)
    return split_docs

def tokenize_chunks(
        split_docs: list[Document],
        tokenizer_name: str = "bert-base-uncased",
        add_special_tokens: bool = True
) -> list[dict]:
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

    tokenized_chunks = []
    for doc in split_docs:
        tokens = tokenizer.encode(
            doc.page_content,
            add_special_tokens=add_special_tokens
        )
        tokenized_chunks.append({
            "input_ids": tokens,
            "attention_mask": [1] * len(tokens),  # For models needing masks
            "metadata": doc.metadata  # Preserve original metadata
        })

    print("Tokenized chunks:")
    print(tokenized_chunks)

    return tokenized_chunks

if __name__ == "__main__":
    text = data_load()
    documents = [Document(page_content=i) for i in text]

    split_docs = split_documents(
        documents,
        model_name="gpt-4",
        chunk_size=20,
        chunk_overlap=10
    )

    for i in split_docs:
        print(i.page_content)