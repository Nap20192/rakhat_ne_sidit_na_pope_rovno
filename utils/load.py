import json
import pathlib

def data_load():
    with open("./scraped_data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data = data["data"]
    text = []
    for item in data:
        for it in item["data"]:
            text.append(it)
    print("DATA LOADED")
    return text

def history_save(history):
    with open("./history.json", "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=4)

def history_load():
    try:
        with open("./history.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except:
        return []

def history_clear():
    try:
        with open("./history.json", "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=4)
        with open("./img_history.json", "w", encoding="utf-8") as file:
            json.dump({}, file, ensure_ascii=False, indent=4)
    except:
        pass

def img_history_load():
    try:
        with open("./img_history.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except:
        return []

def img_history_save(img_history):
    with open("./img_history.json", "w", encoding="utf-8") as file:
        json.dump(img_history, file, ensure_ascii=False, indent=4)

def img_load():
    directory = pathlib.Path("./img")
    file_names = [file.name for file in directory.rglob("*") if file.is_file()]
    return file_names