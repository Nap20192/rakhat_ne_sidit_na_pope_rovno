import ollama
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from assignment4 import collection
import os

from models import Prompt


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


def data_from_web(prompt:Prompt, documents, model):
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
    return output['response']

def response_img(images):
    print("ANALYZING PICTURES")
    descriptions = {}
    try:
        for image in images:
            image_path = f'../img/{image}'

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
