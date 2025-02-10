import ollama
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
import chromadb
import os
import asyncio

from models import Prompt

client = chromadb.PersistentClient(path="../chroma_db")
collection = client.get_or_create_collection(name="my_collection")

async def generate_response_with_ollama(prompt, model, history, documents):
    llm = ChatOllama(model=model, base_url="http://localhost:11434")
    messages = []
    for msg in history:
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            messages.append(AIMessage(content=msg['content']))
        else:
            raise ValueError(f"Unsupported message type: {msg['role']}")

    context = "\n".join(documents)
    prompt_with_context = f"Documents content: {context}\n\nUser's question: {prompt}"
    messages.append(HumanMessage(content=prompt_with_context))

    try:
        response = llm(messages)
        return response.content
    except ValueError as e:
        print(f"Error generating response: {e}")
        return "An error occurred while processing your request."


async def data_from_web(prompt:Prompt, documents, model):
    print("LLM WORKING")
    response = ollama.embeddings(
        prompt=prompt.get_prompt(),
        model="mxbai-embed-large"
    )
    results = collection.query(
        query_embeddings=[response["embedding"]],
        n_results=1
    )
    data = results['documents'][0][0]
    output = ollama.generate(
        model=model,
        prompt=f"Using this document data: {documents} and using this web data: {data}. Respond to this prompt: {prompt}"
    )
    print(output['response'])
    return output['response']

async def response_img(images):
    print("ANALYZING PICTURES")
    descriptions = {}
    try:
        print(images)
        for image in images:

            image_path = f'./img/{image}'

            if not os.path.exists(image_path):
                print(f"ERROR: File {image_path} not found.")
                continue
            print('Processing IMAGE:', image)

            res = ollama.chat(
                model="llava",
                messages=[
                    {
                        'role': 'user',
                        'content': 'Describe this image:',
                        'images': [image_path]
                    }
                ]
            )
            description = res['message']['content']
            descriptions[image] = description
            print(f"Image Description for {image}: {description}")
        return descriptions
    except Exception as e:
        print(f"Error processing image: {e}")
        return {}

async def concurrent_generation(prompt, documents, model, images):
    response, descriptions = await asyncio.gather(
        data_from_web(prompt, documents, model),
        response_img(images)
    )
    return response, descriptions
