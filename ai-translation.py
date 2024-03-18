from openai import OpenAI
import re
from utility import *
import anthropic



def send_gpt(gpt_client, system_message, user_message, claude_client):
	def submit_to_gpt(system_message, chunk):
		completion = gpt_client.chat.completions.create(
			model="gpt-4-0125-preview",
			messages=[{"role": "system", "content": system_message}, {"role": "user", "content": chunk}],
		)
		return completion.choices[0].message.content

	def submit_to_claude(system_message, chunk):
		message = claude_client.messages.create(
			model="claude-3-opus-20240229",
			max_tokens = 4096,
			temperature=0.7,
			system=system_message,
			messages=[
				{"role": "user", "content": chunk}
			]
		)
		return message.content[0].text

	try:
		length_of_message = len(user_message) // 2
		sentence_endings = [m.start() for m in re.finditer(r"\n", user_message)]
		speech_ending = [m.end() for m in re.finditer(r'(?<=")', user_message)]
		speech_start = [m.start() for m in re.finditer(r'(?<=")', user_message)]

		split_position = position_of_next_line(sentence_endings, speech_ending, speech_start, length_of_message)
		first_chunk = user_message[:split_position + 1]
		second_chunk = user_message[split_position + 1:]

		USE_GPT = False
		if(USE_GPT):
			final_text = submit_to_gpt(system_message, first_chunk) + submit_to_gpt(system_message, second_chunk)
		else:
			final_text = submit_to_claude(system_message, first_chunk) + submit_to_claude(system_message, second_chunk)
		
		
		return final_text
	except Exception as e:
		print("ERROR OCCURRED\n", e)

def main():
	
	GPT_KEY = json_loading('APIKEY.json')['openAI']
	CLAUDE_KEY = json_loading('APIKEY.json')['claude']

	gpt_client = OpenAI(api_key=GPT_KEY)
	claude_client = anthropic.Anthropic(api_key=CLAUDE_KEY)


	lists_of_file = find_files_with_keyword("","input-text")
	for i, filename in enumerate(lists_of_file, 1):
		print(f"{i}: {filename}")

	file_choice = int(input("Input file index (ORIGINAL FILE): ")) - 1
	print("Selected:", lists_of_file[file_choice])
	story_name = lists_of_file[file_choice]

	proper_story_name = select_story_name()


	recent_line = json_loading("Translated.json")[proper_story_name]["Line"]
	relevant_chapters = skip_lines_and_return_content(f"cleaned\\cleaned-{story_name}", recent_line)

	make_file("output-text", f"translation-{story_name}")

	

	counter_limit = input("How many chapters to translate? Enter for ALL chapters: ")
	counter_limit = int(counter_limit) if counter_limit else 999999

	context = input("Context (The context is of...): ")
	names = gather_names()

	commands = build_commands(context, names)

	try:
		for current_chapter in range(len(relevant_chapters)):
			if counter_limit:
				print(f"Requesting chapter")

				print(relevant_chapters[current_chapter])				
				response = send_gpt(gpt_client, commands, relevant_chapters[current_chapter],claude_client)

				print(response)

				with open(f"output-text\\translation-{story_name}", "a", encoding="utf-8") as append_to_file:
					append_to_file.write(str(response) + "\n\nNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTER\n\n")
				
				search_line = relevant_chapters[current_chapter+1].strip().split("\n")
				search_string = "\n".join(search_line[:10])
				print(f"Search string:{search_string}")

				counter_limit -= 1
	except Exception as e:
		print(e)
	finally:
		line_number = search_file(f"cleaned\\cleaned-{story_name}", search_string)
		updated_json = {proper_story_name:
			{
				"Line":line_number
			}
		}
		modify_json_file("Translated.json", updated_json)


def select_story_name():
	print("Choose the story name using the number")
	storylist_file = open("storylist.txt", "r")
	storylist = storylist_file.read().split("\n")

	for i, story in enumerate(storylist, 1):
		print(f"{i}: {story}")
	return storylist[int(input(":"))-1]

def gather_names():
	names = ""
	while True:
		name_temp = input("Key Names? (empty = break): ")
		if not name_temp:
			break
		names += (name_temp + "\n")
	return names

def build_commands(context, names):
	base_command = f"""
	# Mission
	You are a highly skilled translator with expertise in many languages. 
	You are to accurately translate from Chinese to English following the context given. 
	Then, correct any sentence structure errors. The USER will give you a text input. 

	# Context
	- The context is of: {context}

	# Instructions
	- Only output the edited and translated version
	- Preserve all dialogues.
	- Minimal edits to the story.
	"""
	return base_command if not names else base_command + f"\n# Name list\n{names}"

if __name__ == '__main__':
	main()
