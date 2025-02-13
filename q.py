from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
import re

def extract_images(text):
    return re.findall(r'!\[.*?\]\((.*?)\)', text)

def format_output(docs):
    return [
        {
            "url": doc.metadata["source"],
            "data": doc.page_content.split("\n"),
            "img_links": extract_images(doc.page_content)
        }
        for doc in docs
    ]
scraping_chain = (
    RunnablePassthrough()  # Принимает список URL
    | RunnableLambda(lambda urls: AsyncHtmlLoader(urls).load())  # Загрузка
    | Html2TextTransformer(ignore_images=False)  # Конвертация в Markdown
    | RunnableLambda(format_output)  # Финализация формата
)

urls = ["https://example.com", "https://lilianweng.github.io/posts/2023-06-23-agent/"]
result = scraping_chain.invoke(urls)

if __name__ 