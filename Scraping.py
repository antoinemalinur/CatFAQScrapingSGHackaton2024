import json
import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.catnmsplan.com/faq?search_api_fulltext=&field_topics=All&sort_by=field_faq_number'

# Get the url
response = requests.get(url)
#Chekc success
response.raise_for_status()

# Parse html
soup = BeautifulSoup(response.text, 'html.parser')

# Get the title section
section_headers = soup.find_all('div', class_='view-grouping-header')  # Titres des sections
#Delete the first one to clean data
del section_headers[0]  # Supprime la première section si nécessaire

# Section content
sections = soup.find_all('div', class_='view-grouping-content')

#Delete the first one to clean data
del sections[0]  # Supprime la première section si nécessaire

#Check consistecy
if len(section_headers) != len(sections):
    print("Inconsistent number of sections")
else:
    squad_data = {"data": []}

    # For each section get answer and question
    for idx, (header, section) in enumerate(zip(section_headers, sections)):
        # Title
        raw_section_title = header.get_text(strip=True)
        section_title = re.sub(r"^[A-Z]\.\s*", "", raw_section_title)  # Supprime "A. ", "B. ", etc.
        print(f"--- Section {idx + 1}: {section_title} --- Done")

        # init
        context = section_title

        # init
        qas = []

        paragraphs = []


        # For each row
        faq_items = section.find_all('div', class_='views-row')
        for faq_idx, faq in enumerate(faq_items):
            try:
                # Get question and delete A. B. etc
                raw_question = faq.find('div', class_='col faq_question').get_text(strip=True)
                question = re.sub(r"^[A-Z]\d+\.\s*", "", raw_question)
                # Get answer
                answer = faq.find('div', class_='views-field-field-answer').get_text(strip=True)
                if question and answer:
                    paragraphs.append({
                        "context": answer,  # Use the answer
                        "qas": [
                            {
                                "question": question,
                                "id": f"faq-{idx + 1}-{faq_idx + 1}",
                                "answers": [
                                    {
                                        "text": answer,
                                        "answer_start": 0  # Always starts at 0
                                    }
                                ],
                                "is_impossible": False
                            }
                        ]
                    })
            except AttributeError:
                # Skip issue
                continue
        squad_data["data"].append({
            "title": section_title,
            "paragraphs": paragraphs
        })
# save to root
with open("squad_faq.json", "w", encoding="utf-8") as file:
    json.dump(squad_data, file, ensure_ascii=False, indent=2)
    print("Dataset SQuAD généré avec succès : squad_faq.json")