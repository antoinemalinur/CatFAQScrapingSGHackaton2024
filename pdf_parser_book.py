# %%
import re, json
from pypdf import PdfReader

# %%
# creating a pdf reader object
reader = PdfReader('resources/cat_specs.pdf')

full_text = ""
index = 10
for i in range(34, 485):
    index += 1
    full_text += reader.pages[i].extract_text()
    print(index)

# %%
def load_index_table():
    full_table = ""
    for i in range(1, 9):
        full_table += reader.pages[i].extract_text()

    lines = full_table.splitlines()
    combined_lines = []
    buffer = ""
    for line in lines:
        # If a line starts with a number (indicating a new entry), save the buffer
        if re.match(r"^\d+(\.\d+)*\.", line):
            if buffer:
                combined_lines.append(buffer.strip())
            buffer = line
        else:
            buffer += " " + line  # Append multiline titles to the buffer
    if buffer:  # Append the last buffer
        combined_lines.append(buffer.strip())

    level_titles = {}
    for line in combined_lines:
        # Match level, title, and page number
        match = re.match(r"(\d+(\.\d+)*)\.\s+(.+?)\s+\.{3,}.*", line)
        if match:
            level = match.group(1)  # Hierarchical level
            title = match.group(3).strip()  # Title
            level_titles[level] = {}
            level_titles[level]['title'] = title

            matches_raw_title = re.match(r"^(.*?)(?=\s*\.{3,}.*)", line)
            if matches_raw_title:
                level_titles[level]['raw_title'] = matches_raw_title.group(1)
            

    return level_titles

index_map = load_index_table()
index_map
# %%

section_content = {}
keys = list(index_map.keys())
for i in range(len(keys) - 1):
    current_key = keys[i]
    next_key = keys[i + 1]
    current_title = index_map[current_key]['raw_title']
    next_title = index_map[next_key]['raw_title']
    pattern = rf"(?<={re.escape(current_title)})(.*?)(?={re.escape(next_title)})"
    matches = re.findall(pattern, full_text, re.DOTALL)

    section_content[current_key] = {}
    section_content[current_key]['title'] = index_map[current_key]['title']
    section_content[current_key]['raw_title'] = index_map[current_key]['raw_title']
    if len(matches) > 0:
        section_content[current_key]['content'] = matches[0].strip()

section_content
# %%
# Write the JSON data to the file
with open('resources/cat_specs.json', "w") as json_file:
    json.dump(section_content, json_file, indent=4)  # Use `indent=4` for pretty printing


# %%
