import chromadb

class User:
    client = chromadb.PersistentClient(path="./chroma_db")
    def __init__(self,user_id, username, chat_id):
        self.user_id = user_id
        self.username = username
        self.chat_id = chat_id
        self.collection = self.client.get_or_create_collection(name=user_id)

    def get_data(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "chat_id": self.chat_id,
        }

    def get_collection(self):
        return self.collection






