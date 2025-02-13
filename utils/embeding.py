import ollama
from langchain_core.documents import Document

def embeding(docs: list[Document], embeding_model ="mxbai-embed-large",collection=None):
    for i, doc in enumerate(docs):
        text = doc.page_content
        print(text)
        response = ollama.embed(
            model=embeding_model,
            input=text
        )
        embeddings = response["embeddings"]
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=embeddings,
        )
    print("EMBEDDINGS GENERATED")
