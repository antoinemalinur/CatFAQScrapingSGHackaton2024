import re, json
from pypdf import PdfReader

class PdfProcessor:

    def __init__(self, pdf_file):
        self.reader = PdfReader(pdf_file)

    def read_pdf_pages(self, from_index, to_index):
        full_text = ""
        for i in range(from_index, to_index):
            full_text += self.reader.pages[i].extract_text()
        return full_text

    def get_index_map(self, full_index):
        lines = full_index.splitlines()
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

        index_map = {}
        for line in combined_lines:
            # Match level, title, and page number
            match = re.match(r"(\d+(\.\d+)*)\.\s+(.+?)\s+\.{3,}.*", line)
            if match:
                level = match.group(1)  # Hierarchical level
                title = match.group(3).strip()  # Title
                index_map[level] = {}
                index_map[level]['title'] = title

                matches_raw_title = re.match(r"^(.*?)(?=\s*\.{3,}.*)", line)
                if matches_raw_title:
                    index_map[level]['raw_title'] = matches_raw_title.group(1)
        return index_map
    
    def parse_tree_with_multiline_titles(self, data):
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
                current[level] = {"title": title, "page": page, "subsections": {}}
                stack.append(level)
        
        return tree


    def get_content_map(self, index_map, full_content):
        section_content = {}
        keys = list(index_map.keys())
        for i in range(len(keys) - 1):
            current_key = keys[i]
            next_key = keys[i + 1]
            current_title = index_map[current_key]['raw_title']
            next_title = index_map[next_key]['raw_title']
            pattern = rf"(?<={re.escape(current_title)})(.*?)(?={re.escape(next_title)})"
            matches = re.findall(pattern, full_content, re.DOTALL)

            section_content[current_key] = {}
            section_content[current_key]['title'] = index_map[current_key]['title']
            section_content[current_key]['raw_title'] = index_map[current_key]['raw_title']
            if len(matches) > 0:
                section_content[current_key]['content'] = matches[0].strip()
        return section_content


    def append_content_to_index_map_tree(self, tree, section_content):
        for key in tree:
            if key in section_content and 'content' in section_content[key]:
                tree[key]['content'] = section_content[key]['content']

            if tree[key]["subsections"]:
                self. append_content_to_index_map_tree(tree[key]["subsections"], section_content)


    def extract_training_data(self, dir_output):
        full_index = self.read_pdf_pages(1, 9)
        index_map = self.get_index_map(full_index)

        full_content = self.read_pdf_pages(34, 485)
        section_content = self.get_content_map(index_map, full_content)

        index_map_tree = self.parse_tree_with_multiline_titles(full_index)
        self.append_content_to_index_map_tree(index_map_tree, section_content)

        with open(dir_output + 'cat_specs.json', "w") as json_file:
            json.dump(section_content, json_file, indent=4)  # Use `indent=4` for pretty printing

        with open(dir_output + 'cat_specs_tree.json', "w") as json_file:
            json.dump(index_map_tree, json_file, indent=4)  # Use `indent=4` for pretty printing

