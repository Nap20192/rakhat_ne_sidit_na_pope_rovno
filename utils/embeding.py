import ollama
from langchain_core.documents import Document
from assignment4 import collection


def embeding(docs: list[Document], embeding_model ="mxbai-embed-large") -> None:
    for i, doc in enumerate(docs):
        text = doc.page_content
        metadata = doc.get("metadata", {})
        print(text)
        response = ollama.embed(
            model=embeding_model,
            input=text
        )
        embeddings = response["embedding"]
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=embeddings,
            metadatas=[metadata]
        )
    print("EMBEDDINGS GENERATED")
