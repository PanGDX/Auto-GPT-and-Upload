import os,json

def find_file(file_name):
    """
    Search through the root_folder and all its subfolders for a file named file_name.
    Returns a list of full paths to the file if found, otherwise returns False.
    """
    matches = []
    for root, dirs, files in os.walk(os.getcwd()):
        if file_name in files:
            matches.append(os.path.join(root, file_name))
    try:
        return matches[0]
    except:
        return False
def find_files_with_keyword(keyword="", directory="."):
    """
    Search for text files in the given directory that include the specified keyword.

    :param keyword: The keyword to search for in files.
    :param directory: The directory to search in.
    :return: A list of filenames that contain the keyword.
    """
    matching_files = []

    # Walk through all files and directories within the specified directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file is a text file
            if file.endswith(".txt"):
                if keyword in file:
                    matching_files.append(file)
                elif keyword=="":
                    matching_files.append(file)

    return matching_files


def replace_comma_newline_advanced(text):
    """
    Replaces ',\n' with ',' and converts the first letter of the next word to lowercase,
    except if it is a word in the name list. Handles lines that end with '\n' and ',\n'.
    """
    # Splitting the text into lines
    lines = text.split("\n")
    for i in range(len(lines)):
        lines[i] = lines[i].strip()

    output = ""
    # Processing each line
    for i in range(len(lines) - 1):
        # If the line ends with a comma
        if lines[i] != "" and lines[i]!="\n":
            if lines[i][-1] == ",":
                output += f" {lines[i]}"  # not \n because have comma!
            else:
                output += f"{lines[i]}\n"
        # Joining the lines with comma
    return output


def skip_lines_and_return_content(file_dir:str, skip_to_line:int):
    """
    skip to line skip_to_line
    skip_to_line is saved as the last chapter's NEWCHAPTERNEWCHAPTER + 1 (0-index)
    

    """
    SPLITTER = "NEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTER"


    # Splitting the text by the SPLITTER and removing any leading or trailing newlines from each part
    with open(file_dir, "r", encoding="utf-8") as file:
        relevant_lines = (file.readlines())[skip_to_line-1:]
        
        relevant_content = "\n".join(relevant_lines)
        relevant_chapters = relevant_content.split(SPLITTER)
    
    return relevant_chapters





def position_of_next_line(
    all_sentence_ending, speech_ending, speech_start, length_of_message
):
    """
    Finds the position of the next newline character in a text, excluding those within speech marks.

    The function iterates through positions of all newline characters (sentence endings) and checks if they 
    are outside of speech marks. The closest newline character position, outside of speech marks and 
    after a specified index in the message, is then returned.

    Parameters:
    all_sentence_ending (list of int): A list of positions for all newline characters in the text.
    speech_ending (list of int): A list of positions indicating the end of speech segments.
    speech_start (list of int): A list of positions indicating the start of speech segments.
    length_of_message (int): The position in the text from which to search for the next newline character.

    Returns:
    int or None: The position of the closest newline character that is outside of speech marks and 
    after the specified index (length_of_message), or None if no such position exists.
    """
    # Initialize the variable to store the closest position of newline
    closest_newline_pos = None

    # Iterate through all newline characters
    for newline_pos in all_sentence_ending:
        # Check if the newline character is not within speech marks
        in_speech = False
        for start, end in zip(speech_start, speech_ending):
            if start <= newline_pos <= end:
                in_speech = True
                break

        # If the newline character is outside speech marks
        if not in_speech:
            # Calculate the difference from length of message
            difference = newline_pos - length_of_message

            # Check if this is the closest newline character so far
            if difference >= 0 and (
                closest_newline_pos is None
                or difference < closest_newline_pos - length_of_message
            ):
                closest_newline_pos = newline_pos

    return closest_newline_pos

def make_file(dir, name):

    """
    make file, extension includeed
    """
    if find_file(name) == False:
        print(f"Making file: {name}")
        with open(f"{dir}\\{name}", "w") as file:
            file.write("")
            file.close()

def json_loading(file_name):
    """
    searches and loads the json file or else return empty json
    """
    file_path = find_file(file_name)
    if file_path:
        textfile = open(file_path, "r")

        json_file = json.loads(textfile.read())
        return json_file
    else:
        return {}
    


def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        return f"Folder '{folder_name}' created successfully."
    else:
        return f"Folder '{folder_name}' already exists."


# Function to create a JSON file if it doesn't exist
def create_json_file(file_name, dump_json = ()):
    # Add .json extension if not present
    if not file_name.endswith('.json'):
        file_name += '.json'
        
    # Check if file already exists
    if not os.path.isfile(file_name):
        # Create an empty JSON file
        with open(file_name, 'w') as file:
            json.dump(dump_json, file, indent = 4)

        return f"JSON file '{file_name}' created successfully."
    else:
        return f"JSON file '{file_name}' already exists."

def deep_merge(orig_dict, new_dict):
    """
    Recursively merge two dictionaries, including nested dictionaries.
    """
    for key in new_dict:
        if key in orig_dict:
            if isinstance(orig_dict[key], dict) and isinstance(new_dict[key], dict):
                deep_merge(orig_dict[key], new_dict[key])
            else:
                orig_dict[key] = new_dict[key]
        else:
            orig_dict[key] = new_dict[key]

def modify_json_file(file_name, dump_json = {}):
    """
    Merge an existing JSON object (in a file) with a new JSON object.
    """
    
    if not file_name.endswith('.json'):
        file_name += '.json'

    json_obj = json_loading(file_name)
    deep_merge(json_obj, dump_json)

    with open(file_name, "w") as file:
        json.dump(json_obj, file, indent=4)

def search_file(file_path, search_string):
    
    search_string = search_string.strip().split("\n")[0]


    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            for line_number, line in enumerate(file, 1):
                if search_string in line:
                    return line_number
                    
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")