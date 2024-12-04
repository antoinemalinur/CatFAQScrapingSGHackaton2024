# **Cat Smart Assistant**

## **Description**
Smart Cat Assistant is a chatbot project built with **Rasa** and a fine-tuned Question-Answering model (BERT). It is designed to provide precise answers to user questions using advanced NLP techniques.

---

## **Features**
- Handles natural language queries based on a fine-tuned QA model.
- Integrated with Rasa for intent recognition and action execution.
- Tools for preprocessing:
  - Extract structured data from PDF documents (e.g., Table of Contents, FAQs).
  - Scrape FAQ content from web pages using BeautifulSoup.

---

## **Requirements**
- **Python**: Version 3.8 or 3.9
- **pip**: Latest version
- **Rasa**: Version 3.6.20 (Installed in a virtual environment)

---

## **Installation**

### **1. Clone the repository**
Clone the project repository to your local machine:
```bash
git clone https://sgithub.fr.world.socgen/kit/smart-cat-assistant.git
```

### **2. Set up a virtual environment**
To ensure isolated dependencies for the project, create and activate a virtual environment:
```bash
python3 -m venv rasa_env
source rasa_env/bin/activate
```

### **3. Start the RASA action server**
```bash
rasa run actions
```

#### **4. Start RASA API**
```bash
rasa run --enable-api --credentials credentials.yml --debug --cors "*"
```

#### **5. Start the web application**
To launch the user interface start the `webapp.py` script:

```bash
python webapp.py
```

