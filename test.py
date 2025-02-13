from models import *
from utils import *
from controlers import *
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import ollama 
from fake_useragent import UserAgent
import os
os.environ["SERPAPI_API_KEY"] = "d9a67728cd1fcce553648e220827779817f7bf9259ede9c74c35541dbba9adb5"  
os.environ['USER_AGENT'] = UserAgent().random
def response(prompt, model, collection):
    print("LLM WORKING")
    
    llm = ChatOllama(model=model, base_url="http://localhost:11434")
    
    try:
        embed_response = ollama.embeddings(model="mxbai-embed-large", prompt=prompt)
        embedding = embed_response["embedding"]
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None
    
    try:
        results = collection.query(
            query_embeddings=[embedding],
            n_results=1
        )
        data = results['documents'][0][0] 
    except Exception as e:
        print(f"Error querying collection: {e}")
        return None
    
    augmented_prompt = f"Context: {data}\n\nQuestion: {prompt}\n\nAnswer:"
    
    try:
        messages = [HumanMessage(content=augmented_prompt)]
        llm_response = llm.invoke(messages)
        return llm_response.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

user = User('1123', 'vnkjd', '708973515')

embeding_chain=( 
    RunnablePassthrough()
    | RunnableLambda(scraping_chain.invoke)
    | RunnableLambda(split_documents)
    | RunnableLambda(lambda docs: embeding(docs,collection =user.get_collection()))  
)

embeding_chain.invoke('world war') 
prompt = "talk about world war"

print(response(prompt, 'llama2-uncensored', user.get_collection()))