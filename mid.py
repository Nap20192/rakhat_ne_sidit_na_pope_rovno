import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings
from langchain.embeddings import OllamaEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOllama
import streamlit as st
from fake_useragent import UserAgent
import json

# Web Scraping Function
def search_web(query, engine="Google"):
    if engine.lower() == "google":
        url = f"https://www.google.com/search?q={query}"
    elif engine.lower() == "bing":
        url = f"https://www.bing.com/search?q={query}"
    elif engine.lower() == "yandex":
        url = f"https://yandex.com/search/?text={query}"
    else:
        raise ValueError("Unsupported search engine")

    headers = {"User-Agent": UserAgent().random}
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'  # Explicitly set the encoding
    soup = BeautifulSoup(response.text, "html.parser")
    
    if engine.lower() == "google":
        results = soup.select("div.tF2Cxc")
        data = [{"title": r.select_one("h3").text, "snippet": r.select_one(".VwiC3b").text} for r in results]
    elif engine.lower() == "bing":
        results = soup.select("li.b_algo")
        data = [{"title": r.select_one("h2").text, "snippet": r.select_one("p").text} for r in results]
    elif engine.lower() == "yandex":
        results = soup.select("li.serp-item")
        data = [{"title": r.select_one("h2").text, "snippet": r.select_one("div.text-container").text} for r in results]
    else:
        data = []

    return data

# Save Data Function
def save_data(query, data):
    with open("search_results.json", "w", encoding="utf-8") as f:
        json.dump({"query": query, "data": data}, f, ensure_ascii=False, indent=4)

# Embedding Generation
def generate_embeddings(data):
    embeddings = OllamaEmbeddings()
    return [embeddings.embed_query(item["snippet"]) for item in data]

# ChromaDB Storage
client = chromadb.Client(Settings(chroma_api_impl="local"))
collection = client.get_or_create_collection("search_results")

def store_in_chromadb(data, embeddings):
    for item, emb in zip(data, embeddings):
        collection.add(
            documents=[item["snippet"]],
            metadatas=[{"title": item["title"]}],
            embeddings=[emb]
        )

# ChromaDB Query
def query_chromadb(query):
    embedding = OllamaEmbeddings().embed_query(query)
    results = collection.query(query_embeddings=[embedding], n_results=5)
    return results

# LangChain Agent Setup
def setup_agent():
    llm = ChatOllama()
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=query_chromadb,
        return_source_documents=True
    )
    return chain

# Streamlit Interface
def main():
    st.title("Web-Powered Chatbot")
    st.write("Ask me anything about recent events!")
    user_query = st.text_input("Your Question:")
    
    if user_query:
        with st.spinner("Searching the web and generating a response..."):
            scraped_data = search_web(user_query)
            if not scraped_data:
                st.error("No results found. Try a different query.")
                return
            
            save_data(user_query, scraped_data)
            embeddings = generate_embeddings(scraped_data)
            store_in_chromadb(scraped_data, embeddings)
            chain = setup_agent()
            response = chain.run({"question": user_query})
            
            st.subheader("Answer")
            st.write(response['answer'])
            
            st.subheader("Sources")
            for doc in response['source_documents']:
                st.write(f"- {doc['metadata']['title']}")

if __name__ == "__main__":
    main()
