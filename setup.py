from utility import *
import os

def initialize_folders():
    create_folder("cleaned")
    create_folder("input-text")
    create_folder("output-text")

def create_story_list_file():
    storylist_path = "storylist.txt"
    if not os.path.exists(storylist_path):
        with open(storylist_path, "w") as file:
            pass

def get_story_titles():
    print("Input the titles of the stories. Write EXIT/enter to conclude the list.")
    titles = []
    while True:
        title = input(":").strip()
        if title.lower() == "exit" or title=="":
            break
        titles.append(title)
    return titles

def append_titles_to_file(titles, filename):
    with open(filename, "a") as file:
        for title in titles:
            file.write("\n" + title)

def initialize_api_keys():
    apikey_json = {
        "openAI": "Put OpenAI key here", 
        "deepL": "Put deepL key here",
        "claude": "Put claude anthropic key here"
    }
    create_json_file("APIKEY", apikey_json)

def create_uploaded_structure(filename):
    translated = {}
    with open(filename, "r", encoding="utf-8") as file:
        for title in file.readlines():
            translated[title.strip()] = {"Chapter": 0, "Line": 0}
    return translated

def create_uploaded_structure(filename):
    translated = {}
    with open(filename, "r", encoding="utf-8") as file:
        for title in file.readlines():
            translated[title.strip()] = {"Chapter": 0, "Line": 0}
    return translated

def create_translated_structure(filename):
    translated = {}
    with open(filename, "r", encoding="utf-8") as file:
        for title in file.readlines():
            translated[title.strip()] = {"Line": 0}
    return translated

def main():
    initialize_folders()
    create_story_list_file()
    titles = get_story_titles()
    append_titles_to_file(titles, "storylist.txt")
    initialize_api_keys()

    uploaded = create_uploaded_structure("storylist.txt")
    for key in ["Inkstone Uploaded", "Patreon Uploaded"]:
        create_json_file(key, uploaded)

    uploaded = create_translated_structure("storylist.txt")
    create_json_file("Translated", uploaded)

    print("Created with no issues.")

if __name__ == "__main__":
    main()
