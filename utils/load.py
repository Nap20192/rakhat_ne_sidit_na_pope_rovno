import json
import pathlib

def data_load():
    with open("../cash/scraped_data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data = data["data"]
    text = []
    for item in data:
        for it in item["data"]:
            text.append(it)
    return text

def img_load():
    directory = pathlib.Path("../img")
    file_names = [file.name for file in directory.rglob("*") if file.is_file()]
    return file_names