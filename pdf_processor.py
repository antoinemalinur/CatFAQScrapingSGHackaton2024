import re, json
from pypdf import PdfReader

class PdfProcessor:

    def __init__(self, pdf_file):
        self.reader = PdfReader(pdf_file)

    def read_pdf_pages(self, from_index, to_index):
        """
        Reads and extracts text from a range of pages in a PDF.

        This method iterates over the specified range of pages in a PDF file 
        and concatenates the extracted text into a single string.

        :param from_index: int
            The starting index (inclusive) of the page range to read. 
            Page indexing starts from 0.
        :param to_index: int
            The ending index (exclusive) of the page range to read.
        :return: str
            A single string containing the concatenated text of the specified 
            range of PDF pages.
        :raises IndexError:
            If the specified page indices are out of bounds of the PDF file.
        """
        full_text = ""
        for i in range(from_index, to_index):
            # Extract text from the current page and append it to the full text
            full_text += self.reader.pages[i].extract_text()
        return full_text

    def get_table_of_contents(self, table_of_contents_full_string):
        """
        Processes the table of contents string to create a structured dictionary.

        This method parses a string representing the table of contents (TOC) of a document.
        It combines multiline entries into single lines, extracts hierarchical levels (e.g., "1.1"),
        titles, and optionally the raw titles (up to ellipses).

        :param table_of_contents_full_string: str
            The full string representing the table of contents. Each line represents an entry
            and may span multiple lines for long titles.
        :return: dict
            A dictionary where keys are hierarchical levels (e.g., "1.1", "2.3.4") and values 
            are dictionaries containing:
                - `title`: The cleaned title of the TOC entry.
                - `raw_title`: The raw title of the entry (up to ellipses).
        """
        # Split the full index text into individual lines
        lines = table_of_contents_full_string.splitlines()
        combined_lines = []
        buffer = ""
        for line in lines:
            # If a line starts with a number (indicating a new entry), process it
            if re.match(r"^\d+(\.\d+)*\.", line):
                if buffer:
                    combined_lines.append(buffer.strip())
                buffer = line
            else:
                buffer += " " + line  # Append multiline titles to the buffer
        if buffer:  # Append the last buffer
            combined_lines.append(buffer.strip())

        table_of_contents = {}
        for line in combined_lines:
            # Match level, title, and page number
            match = re.match(r"(\d+(\.\d+)*)\.\s+(.+?)\s+\.{3,}.*", line)
            if match:
                level = match.group(1)  # Hierarchical level
                title = match.group(3).strip()  # Title
                table_of_contents[level] = {}
                table_of_contents[level]['title'] = title
                matches_raw_title = re.match(r"^(.*?)(?=\s*\.{3,}.*)", line)
                if matches_raw_title:
                    table_of_contents[level]['raw_title'] = matches_raw_title.group(1)
        return table_of_contents
    
    def parse_tree_with_multiline_titles(self, data):
        """
        Parses a hierarchical tree structure from text with multiline titles.

        This method processes a string representation of a hierarchical tree (e.g., a table of contents or index),
        combining multiline entries, and creating a nested dictionary structure. Each node in the tree contains
        the hierarchical level, title, page number, and a dictionary of subsections.

        :param data: str
            The input text representing the hierarchical tree. Each entry starts with a numeric hierarchical level
            (e.g., "1.", "1.1.", "1.1.1.") followed by a title, ellipses, and a page number.
        :return: dict
            A nested dictionary representing the hierarchical tree. Each node contains:
                - `title`: The title of the entry.
                - `page`: The page number where the entry appears.
                - `subsections`: A dictionary of subsections nested under the current entry.
        """
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

    def get_content_map(self, table_of_contents, full_content):
        """
        Extracts content for each section based on a table of contents and the full content.

        This method uses the table of contents to identify sections in the full content of a document.
        It extracts the text between titles of consecutive sections, mapping the extracted content 
        to the corresponding section from the table of contents.

        :param table_of_contents: dict
            A dictionary representing the table of contents, where keys are hierarchical levels (e.g., "1.1")
            and values are dictionaries containing:
                - `title`: The cleaned title of the section.
                - `raw_title`: The raw title of the section, used to match in the content.
        :param full_content: str
            The full text content of the document from which sections will be extracted.
        :return: dict
            A dictionary where keys are hierarchical levels (e.g., "1.1") and values are dictionaries containing:
                - `title`: The cleaned title of the section.
                - `raw_title`: The raw title of the section.
                - `content`: The text content of the section extracted from the full content.
        """
        section_content = {}
        keys = list(table_of_contents.keys())
        for i in range(len(keys) - 1):
            current_key = keys[i]
            next_key = keys[i + 1]
            current_title = table_of_contents[current_key]['raw_title']
            next_title = table_of_contents[next_key]['raw_title']
            pattern = rf"(?<={re.escape(current_title)})(.*?)(?={re.escape(next_title)})"
            matches = re.findall(pattern, full_content, re.DOTALL)
            section_content[current_key] = {}
            section_content[current_key]['title'] = table_of_contents[current_key]['title']
            section_content[current_key]['raw_title'] = table_of_contents[current_key]['raw_title']
            if len(matches) > 0:
                section_content[current_key]['content'] = matches[0].strip()
        return section_content

    def append_content_to_table_of_contents_tree(self, tree, section_content):
        """
        Appends section content to a hierarchical table of contents tree.

        This method recursively traverses a tree structure representing a table of contents (TOC)
        and appends content to the corresponding sections using a dictionary of section content.
        It ensures that each node in the tree that has a matching entry in the section content
        dictionary is updated with its respective content.

        :param tree: dict
            A nested dictionary representing the TOC tree. Each node should have:
                - `subsections`: A dictionary of child nodes (subsections).
                - Additional fields like `title` or `content` (if present).
        :param section_content: dict
            A dictionary where keys are section identifiers (e.g., "1.1") and values are dictionaries
            containing:
                - `content`: The text content of the section.
        """
        for key in tree:
            if key in section_content and 'content' in section_content[key]:
                tree[key]['content'] = section_content[key]['content']
            if tree[key]["subsections"]:
                self. append_content_to_table_of_contents_tree(tree[key]["subsections"], section_content)

    def extract_training_data(self, dir_output):
        """
        Extracts structured training data from a PDF and saves it in JSON files.

        This method processes a PDF to extract the table of contents (TOC) and the full document content.
        It maps the content to the sections defined by the TOC and constructs a hierarchical tree structure
        for the TOC. The extracted data is saved in two JSON files:
            - `cat_specs.json`: Contains section-wise content mapping.
            - `cat_specs_tree.json`: Contains a hierarchical tree representation of the TOC with appended content.

        :param dir_output: str
            The directory path where the output JSON files will be saved.
        """
        # Step 1: Extract the table of contents from the first few pages of the PDF
        table_of_contents_full_string = self.read_pdf_pages(1, 9)
        table_of_contents = self.get_table_of_contents(table_of_contents_full_string)

        # Step 2: Extract the main content from the relevant pages of the document
        full_content = self.read_pdf_pages(34, 485)
        section_content = self.get_content_map(table_of_contents, full_content)

        # Step 3: Build a hierarchical tree structure for the table of contents
        table_of_contents_tree = self.parse_tree_with_multiline_titles(table_of_contents_full_string)
        self.append_content_to_table_of_contents_tree(table_of_contents_tree, section_content)

        # Step 4: Save the extracted section content mapping to a JSON file
        with open(dir_output + 'cat_specs.json', "w") as json_file:
            json.dump(section_content, json_file, indent=4)  # Use `indent=4` for pretty printing

        # Save the hierarchical TOC tree with content to another JSON file
        with open(dir_output + 'cat_specs_tree.json', "w") as json_file:
            json.dump(table_of_contents_tree, json_file, indent=4)  # Use `indent=4` for pretty printing

