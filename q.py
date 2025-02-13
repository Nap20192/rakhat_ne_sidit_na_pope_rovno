import os

from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.document_loaders import WebBaseLoader
from fake_useragent import UserAgent

ua = UserAgent()
os.environ["USER_AGENT"] = ua.random
os.environ["SERPAPI_API_KEY"] = "d9a67728cd1fcce553648e220827779817f7bf9259ede9c74c35541dbba9adb5"  # Replace with your key

def search_google(query, num_results=3):
    search = SerpAPIWrapper(params={"user_agent": os.environ["USER_AGENT"]})
    results = search.run(query)
    return [result["link"] for result in results[:num_results] if "link" in result]

def load_pages(urls):
    loader = WebBaseLoader(urls)
    return loader.load()

def transform_docs(docs):
    transformer = Html2TextTransformer()
    return transformer.transform_documents(docs)

scraping_chain = (
        RunnablePassthrough()
        | RunnableLambda(search_google)
        | RunnableLambda(load_pages)
        | RunnableLambda(transform_docs)
)

print(scraping_chain.invoke('donald trump'))