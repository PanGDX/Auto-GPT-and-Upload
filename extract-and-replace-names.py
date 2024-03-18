from openai import OpenAI
import os
import re
import argostranslate.package
import argostranslate.translate
from utility import *

def translate_text(string):
    from_code, to_code = "zh", "en"
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next((pkg for pkg in available_packages if pkg.from_code == from_code and pkg.to_code == to_code), None)
    if package_to_install:
        argostranslate.package.install_from_path(package_to_install.download())
        return argostranslate.translate.translate(string, from_code, to_code)
    return string

def name_translation_aid(namelist, client, context):
    def submit_to_gpt(system_message, chunk, temperature=0.7):
        completion = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": system_message}, 
                {"role": "user", "content": chunk}], temperature = temperature
        )
        return completion.choices[0].message.content

    def return_segmented_namelist(namelist):
        list_ = namelist.split("\n")
        output_list = []
        
        counter = 0
        sub_namelist = ""
        for name in list_:
            if counter > 30:
                output_list.append(sub_namelist)
                sub_namelist = ""
                counter = 0
            else:
                sub_namelist += f"{name}\n"
                counter+=1
        output_list.append(sub_namelist)
        return output_list

    translation_prompt = f"""
# Mission
Translate names from Chinese to English in the context of {context}. Inaccuracies are acceptable

# Output Format
Only output the following, line by line.
(Chinese name) - (Translated English name)
No additional comments needed.
    """

    reduction_promt = f"""
# Mission
Take the names and eliminate ones that do not seem relevant to the context of {context}.
The condition for relevancy are: names of characters and names of organisations.

# Output Format
Only output the following, line by line.
(Chinese name) - (Translated English name)
No additional comments needed.
    """
    print("Starting translation")

    segmented_namelist = return_segmented_namelist(namelist)

    translated_names = ""
    for sub_namelist in segmented_namelist:
        all_translated = submit_to_gpt(translation_prompt, sub_namelist)
        reduced_translated = submit_to_gpt(reduction_promt,all_translated)
        translated_names += reduced_translated

    translated_names = translated_names.split("\n")
    gpt_translated_dict = {line.split("-")[0].strip(): line.split("-")[1].strip() for line in translated_names if line}
    
    pip_translated_dict = {}
    for name in gpt_translated_dict:
        pip_translated_dict[name] = translate_text(name)
    
    return gpt_translated_dict,pip_translated_dict

def extract_chinese(text):
    pattern = r'[\u4e00-\u9fff]+'
    return re.findall(pattern, text)

def sorting(lst):
    return sorted(lst, key=len)

def send_gpt(client, system_message, user_message):
    try:
        print("Processing chunk names")
        completion = client.chat.completions.create(model="gpt-3.5-turbo-1106", messages=[{"role": "system", "content": system_message}, {"role": "user", "content": user_message}], temperature=0.7)
        return completion.choices[0].message.content
    except Exception as e:
        print("ERROR OCCURRED", e)

def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    APIKEY = json_loading('APIKEY.json')['openAI']
    client = OpenAI(api_key=APIKEY)
    command_input = """
    # Mission
    Extract all names of organisations and characters from the text and list them

    # Expected Input
    A text containing a story

    # Expected Output
    Only output the names, separated by a newline.
    """
    lists_of_file = find_files_with_keyword(directory=os.path.join(current_dir, "input-text"))
    for i, filename in enumerate(lists_of_file, 1):
        print(f"{i}: {filename}")

    file_choice = int(input("Input file index (ORIGINAL FILE): ")) - 1
    print("Selected:", lists_of_file[file_choice])
    story_name = os.path.splitext(lists_of_file[file_choice])[0]

    final_list = []
    try:
        with open(os.path.join(current_dir, "input-text", lists_of_file[file_choice]), "r", encoding="utf-8") as file:

            splitter = "NEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTER"
            content = [part.strip() for part in file.read().split(splitter) if part.strip()]


        for user_message in content:
            if content != "":
                print(f"Processing names")
                namelist = send_gpt(client, command_input, user_message).split("\n")
                for line in namelist:
                    chinese_extracted = extract_chinese(line)
                    final_list.extend([name for name in chinese_extracted if len(name) >= 2])

    except IndexError:
        print("Ended")
    except Exception as e:
        print(e)
    finally:
        final_list = sorting(list(set(final_list)))
        string_name_list = "\n".join(final_list)

        with open(os.path.join(current_dir, "input-text", lists_of_file[file_choice]), "r", encoding="utf-8") as file:
            file_text = file.read()

        print("Completed list processing. Eliminating unnecessary names. Please wait")
        
        context = str(input("Context:"))
        gpt_namelist_dict, pip_namelist_dict = name_translation_aid(string_name_list, client, context)

        

        try:
            for counter, name in enumerate(pip_namelist_dict, 1):
                gpt_name = "GPT Translation encountered an error/missing this name"
                try:
                    gpt_name = gpt_namelist_dict[name]
                except:
                    pass 

                english_name = input(f"""
                \n{counter}. 
Replace {name} with? (empty = no replace)
Suggestions:
ChatGPT Direct Translate: {gpt_name}
Translate directly: {pip_namelist_dict[name]}
                """)
                if english_name:
                    file_text = file_text.replace(name, english_name)
        except:
            with open(os.path.join(current_dir, "cleaned", f"cleaned-{story_name}.txt"), "w", encoding="utf-8") as file:
                file.write(file_text)

if __name__ == '__main__':
    main()
