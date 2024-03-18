from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
from webdriver_manager.firefox import GeckoDriverManager
import os
from utility import *

# Global variables
current_dir = os.path.dirname(os.path.realpath(__file__))
output_file = input("Output file name: ")
story_name = input("Story name: ")
url_to_scrape = input("Url of the chapter: ")
content = input("A part of the content of the chapter: ")
link_text = input("The text leading to the next chapter: ")

def formatting(url, next_link):
    if "http" in next_link:
        return next_link
    else:
        bracket_position = url.find("/", url.find("//") + 2)
        return url[:bracket_position] + next_link

def append_to_file(file_path, content):
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(content)
        file.write("\nNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTERNEWCHAPTER\n\n\n")

def find_divs_with_text(soup, search_text):
    search_text = search_text.strip()
    divs = soup.find_all(lambda tag: tag.name == "div" and search_text in tag.text)
    for div in divs:
        tag_class = " ".join(div.get("class", []))
        tag_id = div.get("id", "")
        return tag_class, tag_id
    return "", ""

def get_link(soup, text):
    text = text.lower().split(" ")
    for search_text in text:
        if search_text:
            for counter in range(5):
                matched_tags = soup.find_all(lambda tag: len(tag.find_all()) == counter and search_text in tag.text.lower())
                for tag in matched_tags:
                    if tag.name == "a":
                        return tag.get("href")
    raise ValueError("Failed to fetch the link with the given link-text")

def create_selenium_driver():
    options = Options()
    options.add_argument("--headless")
    service = Service(executable_path=GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)

def scrape_webpage(driver, url, link_text, content_class, content_id):
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        result = "\n".join([content.get_text(separator="\n") for content in soup.find_all("div", class_=content_class, id=content_id)])
        append_to_file(os.path.join(current_dir, "input-text", f"{output_file}.txt"), result)
        next_link = get_link(soup, link_text)
        if next_link:
            print(f"Navigating to the next link: {next_link}")
            scrape_webpage(driver, formatting(url, next_link), link_text, content_class, content_id)
        else:
            print("No next link found, or there was an error fetching it.")
    except Exception as e:
        print(f"An error occurred: {e}")

def access_website_with_selenium():
    driver = create_selenium_driver()
    try:
        driver.get(url_to_scrape)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        content_class, content_id = find_divs_with_text(soup, content)
        scrape_webpage(driver, url_to_scrape, link_text, content_class, content_id)
    finally:
        driver.quit()

def main():
    try:
        with open(os.path.join(current_dir, "input-text", f"{output_file}.txt"), "w") as file:
            pass
        with open(os.path.join(current_dir, "storylist.txt"), "a", encoding="utf-8") as file:
            file.write("\n" + story_name)
        # Initialize JSON files here as required
        access_website_with_selenium()
    except Exception as e:
        print(e)
        input()

if __name__ == "__main__":
    main()
