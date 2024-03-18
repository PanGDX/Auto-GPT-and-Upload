import pyautogui, time, os, re, pyperclip, threading, keyboard
from utility import *





def main_process():
	current_dir = os.path.dirname(os.path.realpath(__file__))


	def detect_and_process_phrase(text):

		"""
		Detects the phrase 第*章 in the text, extracts the number from each instance, and deletes the lines containing the phrase.
		"""
		lines = text.split('\n')
		new_lines = []
		for line in lines:
			if re.search(r'Chapter .*', line):
				continue
			new_lines.append(line)

		return '\n'.join(new_lines)

		
	def copy_paste(text:str):
		pyperclip.copy(text)
		pyautogui.hotkey('ctrl', 'v')

	def loop_for_patreon_submission(title:str, content:str, choice:int):
		pyautogui.click(x=152, y=685) #go to create and press it
		time.sleep(2)
		pyautogui.click(x=804, y=456) #go to text
		time.sleep(10)
		
		pyautogui.click(x=1482, y=464) # go to select and press
		time.sleep(0.1) 

		pyautogui.click(x=1461, y=530 + (choice-1)*53) # go to select and press
		time.sleep(0.1) 


		pyautogui.click(x=612, y=336) #title press
		time.sleep(1)
		copy_paste(title)
		time.sleep(1)

		
		pyautogui.click(x=607, y=403) #go to textbox
		time.sleep(1) 
		copy_paste(content)
		time.sleep(1)



		pyautogui.click(1834, 975) #next
		time.sleep(1) 
		pyautogui.click(1834, 975) #submit
		time.sleep(5) 

		pyautogui.click(x=152, y=724) #click to close submit button
		time.sleep(0.5)


	def loop_for_webnovel_submission(title:str, content:str):
		# create
		pyautogui.click(1706,187) 
		time.sleep(5)
		
		# title
		pyautogui.click(642,400)
		copy_paste(title)
		time.sleep(1)

		
		# textbox
		pyautogui.click(656,489)
		copy_paste(content)
		time.sleep(1)
		
		#publish
		pyautogui.click(1769,188)
		time.sleep(5)
		
		#confirm
		pyautogui.click(1216,950)
		time.sleep(5)

	def open_inkstone_to_load():
		"""
		choice is 1-index
		"""
		pyautogui.click(425,111)
		copy_paste("https://inkstone.webnovel.com/novels/list?story=1")
		pyautogui.press('enter')  
		time.sleep(10)


	def open_inkstone_and_choice(choice:int):
		"""
		choice is 1-index
		"""
		pyautogui.click(425,111)
		copy_paste("https://inkstone.webnovel.com/novels/list?story=1")
		pyautogui.press('enter')  
		time.sleep(10)

		pyautogui.click(1671,447 + 142 * (choice-1))
		time.sleep(10)

	def open_patreon():
		pyautogui.click(425,111)
		copy_paste("https://www.patreon.com/FFAddict")
		pyautogui.press('enter')  
		time.sleep(5)



	lists_of_file = find_files_with_keyword(directory=f"{current_dir}\\input-text")
	for i in range(len(lists_of_file)):
		print(f"{i+1}:{lists_of_file[i]}")
	fileinputs = int(input("Input file (one index)(ORIGINAL FILE):"))
	print(lists_of_file[fileinputs - 1])
	filename = lists_of_file[fileinputs - 1]



	with open("storylist.txt","r",encoding = "utf-8") as storylist_file:
		story_list = (storylist_file.read()).split("\n")
		print("Choose the story name using the number")
		for i in range(len(story_list)):
			print(f"{i+1}: {story_list[i]}")
		PROPER_STORY_NAME = story_list[int(input(":"))-1]




	INKSTONE_ARRAY = [
		"Journalling in Marvel",
		"Cyberpunk: Legendary Life",
		"One Piece: Flevance"
	]
	PATREON_ARRAY= [
		"One Piece: Flevance",
		"Journalling in Marvel",
		"Cyberpunk: Legendary Life"
	]

	INKSTONE_CHOICE = INKSTONE_ARRAY.index(PROPER_STORY_NAME) + 1
	PATREON_CHOICE = PATREON_ARRAY.index(PROPER_STORY_NAME) + 1


	PATREON_CHAPTER = json_loading('Patreon Uploaded.json')[PROPER_STORY_NAME]["Chapter"]
	INKSTONE_CHAPTER = json_loading('Inkstone Uploaded.json')[PROPER_STORY_NAME]["Chapter"]

	HOW_MANY_CHAPTERS = int(input("How many chapters:"))
	INKSTONE_SUBMIT = str(input("Submit to Inkstone:"))
	PATREON_SUBMIT = str(input("Submit to Patreon:"))

	print("Go to Firefox")
	
	
	time.sleep(5)
	open_inkstone_to_load()

	if PATREON_SUBMIT.lower() == "y":

		print("Patreon submission starts")

		recent_chapters = json_loading("Patreon Uploaded.json")[PROPER_STORY_NAME]["Line"]
		relevant_chapters = skip_lines_and_return_content(f"output-text\\translation-{filename}", recent_chapters)


		chapter_counter = HOW_MANY_CHAPTERS
		

		open_patreon()


		search_string = ""
		try:
			for counter in range(len(relevant_chapters)):
				if chapter_counter > 0:
					content = detect_and_process_phrase(relevant_chapters[counter]).strip()
					if content != "":
						content = content.replace("\n\n", "\n")
						content = content.replace("\n\n", "\n")
						title = f"{PROPER_STORY_NAME} - Chapter {PATREON_CHAPTER}"


						print(title)
						loop_for_patreon_submission(title, content, PATREON_CHOICE)

						if counter+1<len(relevant_chapters):
							search_string = relevant_chapters[counter+1].strip()
						
						chapter_counter-=1
						PATREON_CHAPTER+=1

		except Exception as e:
			print(e)
		finally:
			line_number = -1
			if search_string != "":
				print("Searching!")
				line_number = search_file(f"output-text\\translation-{filename}", search_string)


				previous_json = json_loading("Patreon Uploaded.json")
				
				if previous_json[PROPER_STORY_NAME]["Line"] < line_number:
					updated_json = {PROPER_STORY_NAME:
						{
							"Line":line_number, 
							"Chapter":PATREON_CHAPTER
						}
					}
					modify_json_file("Patreon Uploaded.json", updated_json)



	if INKSTONE_SUBMIT.lower() == "y":

		recent_chapters = json_loading("Inkstone Uploaded.json")[PROPER_STORY_NAME]["Line"]
		relevant_chapters = skip_lines_and_return_content(f"output-text\\translation-{filename}", recent_chapters)
		time.sleep(5)
		print("Inkstone submission starts")
		chapter_counter = HOW_MANY_CHAPTERS
		open_inkstone_and_choice(INKSTONE_CHOICE)

		search_string = ""
		try:
			for counter in range(len(relevant_chapters)):
				if chapter_counter>0:
					
					output_content = "Future chapters (15+) at patreon.com/FFAddict. Thank you!\n\n"
					content = detect_and_process_phrase(relevant_chapters[counter]).strip()
					
					if content != "":
						content = content.replace("\n\n", "\n")
						content = content.replace("\n\n", "\n")
						
						output_content += content
						title = f"Chapter {INKSTONE_CHAPTER}"
						
						print(title)
						loop_for_webnovel_submission(title, output_content)
						
						
						if counter+1<len(relevant_chapters):
							search_string = relevant_chapters[counter+1].strip()
						INKSTONE_CHAPTER+=1
						chapter_counter-=1

		except Exception as e:
			print(e)
		finally:
			line_number = -1
			if search_string != "":
				print("Searching!")
				line_number = search_file(f"output-text\\translation-{filename}", search_string)
				previous_json = json_loading("Inkstone Uploaded.json")
				if previous_json[PROPER_STORY_NAME]["Line"] < line_number:
					updated_json = {PROPER_STORY_NAME:
						{
							"Line":line_number, 
							"Chapter":INKSTONE_CHAPTER
						}
					}
					modify_json_file("Inkstone Uploaded.json", updated_json)


def check_for_exit():
	while True:
		if keyboard.is_pressed('ctrl+c'):  # Detect CTRL-C key press
			print("CTRL-C pressed. Exiting...")
			os._exit(1)  # Forcefully exit the program


if __name__ == "__main__":
	# Start the exit listener in a separate thread
	exit_thread = threading.Thread(target=check_for_exit, daemon=True)
	exit_thread.start()

	# Run the main process
	main_process()