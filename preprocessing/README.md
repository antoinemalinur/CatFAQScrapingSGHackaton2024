# SmartCAT Solution
## 1. PdfProcessor Class Documentation

### Overview
The `PdfProcessor` class provides functionality to process a PDF file by extracting structured training data, including section-wise content and a hierarchical tree representation of the table of contents (TOC). The class exposes one public method, `extract_training_data`, which saves the extracted data as JSON files.

### Usage

#### Initialization
To use the `PdfProcessor` class, initialize it with the path to the PDF file you want to process:

```python
from PdfProcessor import PdfProcessor

# Initialize the PdfProcessor with the path to the PDF file
processor = PdfProcessor('resources/cat_specs.pdf')
processor.extract_training_data('resources/')

