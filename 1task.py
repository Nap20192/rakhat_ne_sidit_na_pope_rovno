import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings
from langchain.embeddings import OllamaEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOllama
import streamlit as st

# Web Scraping Function
def search_web(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    return [{"title": r.select_one("h3").text, "snippet": r.select_one(".VwiC3b").text} for r in soup.select("div.tF2Cxc")]

# Embedding Generation
def generate_embeddings(data):
    embeddings = OllamaEmbeddings()
    return [embeddings.embed_query(item["snippet"]) for item in data]

# ChromaDB Storage
client = chromadb.Client()
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
