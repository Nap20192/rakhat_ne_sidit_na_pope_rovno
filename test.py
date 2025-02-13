from models import *
from utils import *
from controlers import *
def main():
    user =User(user_id = '1123', username = 'vnkjd', chat_id = '708973515')

    prompt = Prompt("what you know about current president of usa",imgflag=False,webflag=True)
    build = Build(user,prompt,history = history_load())
    build.building()

if __name__ == "__main__":
    main()