import ollama
from langchain_core.documents import Document
from assignment4 import collection


def embeding(docs: list[Document], embeding_model ="mxbai-embed-large"):
    for i, doc in enumerate(docs):
        text = doc.page_content
        print(text)
        response = ollama.embed(
            model=embeding_model,
            input=text
        )
        embeddings = response["embedding"]
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=embeddings,
        )
    print("EMBEDDINGS GENERATED")
