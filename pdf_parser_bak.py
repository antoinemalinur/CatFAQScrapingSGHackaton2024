# %%
import re
from pypdf import PdfReader

# %%
# creating a pdf reader object
reader = PdfReader('resources/cat_specs.pdf')

# %%
def load_index_table():
    consolidated_index = ""
    for i in range(1, 9):
        for l in reader.pages[i].extract_text():
            consolidated_index += l
    return consolidated_index


def load_all_content():
    consolidated_index = ""
    for i in range(1, 9):
        for l in reader.pages[i].extract_text():
            consolidated_index += l
    return consolidated_index


def parse_tree_with_multiline_titles(data):
    # Remove excess whitespace and join lines that belong together
    lines = data.splitlines()
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

    tree = {}
    stack = []

    # Parse each combined line
    for line in combined_lines:
        # Match level, title, and page number
        match = re.match(r"(\d+(\.\d+)*)\.\s+(.+?)\s+\.{3,}\s+(\d+)", line)
        if match:
            level = match.group(1)  # Hierarchical level
            title = match.group(3).strip()  # Title
            page = int(match.group(4))  # Page number
            
            depth = level.count(".")  # Determine depth based on number of dots
            
            while len(stack) > depth:
                stack.pop()
            
            # Navigate to the correct position in the tree
            current = tree
            for key in stack:
                current = current[key]["subsections"]
            
            # Add the new entry
            current[level] = {"start_title": title, "start_page": page, "subsections": {}}
            stack.append(level)
    
    return tree

def compute_end_pages_with_title(tree):
    """
    Add 'end_page' and 'end_page_title' to each section in the tree.
    """
    def set_end_pages(tree, parent_end_page=None, parent_end_title=None):
        keys = list(tree.keys())
        for i, key in enumerate(keys):
            current_section = tree[key]
            # If there's a next section at the same level, use its start page
            if i + 1 < len(keys):
                next_key = keys[i + 1]
                current_section["end_page"] = tree[next_key]["start_page"] - 1
                current_section["end_page_title"] = tree[next_key]["start_title"]
            else:
                # If it's the last section, propagate parent end page and title
                current_section["end_page"] = parent_end_page
                current_section["end_page_title"] = parent_end_title
            
            # Recursively calculate for subsections
            if current_section["subsections"]:
                # Pass the end_page and end_title of the current section to its subsections
                set_end_pages(
                    current_section["subsections"],
                    current_section["end_page"],
                    current_section["end_page_title"]
                )
    
    # Start processing the root tree
    set_end_pages(tree)
    return tree


def extract_section_content_from_text(full_text, tree):
    """
    Extracts content for each section in the hierarchical tree based on the section headers in the text.

    :param full_text: The entire input text as a single string.
    :param tree: Hierarchical tree structure with section identifiers.
    :return: Updated tree with a 'content' field for each section.
    """
    # Split the text into sections based on section headers (e.g., "2.4.1.1", "2.4.1.2")
    sections = re.split(r"ˆ(\d+(\.\d+)+\.\s)", full_text)
    
    # Combine the section identifiers with their content
    structured_sections = []
    for i in range(1, len(sections), 2):
        section_number = sections[i].strip()  # e.g., "2.4.1.1"
        section_content = sections[i + 1].strip()  # Content after the section number
        structured_sections.append((section_number, section_content))

    def match_and_assign_content(tree, sections):
        """
        Recursively match section numbers from the tree to the sections in the text
        and assign the content.
        """
        for key, node in tree.items():
            # Match the section number
            matched_section = next((s for s in sections if s[0] == key), None)
            if matched_section:
                node["content"] = matched_section[1]
            else:
                node["content"] = ""

            # Recursively process subsections
            if "subsections" in node and node["subsections"]:
                match_and_assign_content(node["subsections"], sections)

    # Match and assign content to the tree
    match_and_assign_content(tree, structured_sections)
    return tree


# %%
index_table = load_index_table()

parsed_tree = parse_tree_with_multiline_titles(index_table)

parsed_tree_with_end_page = compute_end_pages_with_title(parsed_tree)

# %%
full_text = ""
index = 10
for i in range(35, 485):
    index += 1
    full_text += reader.pages[i].extract_text()
    print(index)

# %%
parsed_tree_with_content = extract_section_content_from_text(full_text, parsed_tree_with_end_page)

# %%
import pprint
pprint.pprint(parsed_tree_with_end_page)
# %%

#sections = re.split(r"(\d+(\.\d+)*\.)?\s*(.+?)\s*(?:\.\s*|\s+)", full_text)

section_header_pattern = re.compile(r"^(\d+(\.\d+)*\.)?\s*(.+?)$", re.MULTILINE)

matches = list(section_header_pattern.finditer(full_text))
    
sections = {}
    
for i, match in enumerate(matches):
    section_number = match.group(1).strip() if match.group(1) else None
    section_title = match.group(3).strip()
    start_pos = match.end()

    # Determine the end position of the content
    if i + 1 < len(matches):
        end_pos = matches[i + 1].start()
    else:
        end_pos = len(full_text)

    # Extract content for this section
    content = full_text[start_pos:end_pos].strip()

    if section_number:
        sections[section_number] = {
            "title": section_title,
            "content": content
        }
sections

1 == 1

# %%
