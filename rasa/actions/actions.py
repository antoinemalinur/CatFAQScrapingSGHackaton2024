from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import Tracker
from rasa_sdk.events import SlotSet
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
import os
import json
import numpy as np
import faiss
from transformers import pipeline, T5Tokenizer, T5ForQuestionAnswering, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer



class ActionAnswerQuestion(Action):
    def __init__(self):
        #Read the formated data (cat.pdf spec)
        import json
        with open("./data/cat_specs.json", 'r') as f:
            cat_specs_data = json.load(f)


        #Encode the content
        self.chunks = [value["content"] for key, value in cat_specs_data.items() if
                  "content" in value and value["content"] != ""]
        self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        chunk_embeddings = self.embedder.encode(self.chunks)

        #Index using faiss
        self.dimension = chunk_embeddings.shape[1]
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(np.array(chunk_embeddings))

        #Set the model pretained
        self.model_name = "./qa_finetuned_model"
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)

    def name(self):
        return "action_answer_question"

    def run(self, dispatcher, tracker, domain):
        #get the question from user
        user_question = tracker.latest_message['text']

        #Encode the question
        query_embedding = self.embedder.encode([user_question])

        #Get the first 5 context found from FISS
        _, indices = self.index.search(np.array(query_embedding), k=5)

        #Concat all contexts
        retrieved_chunks = [self.chunks[i] for i in indices[0]]
        context = " ".join(retrieved_chunks)

        #Create the input text with the concatenated context
        input_text = f"question: {user_question} context: {context}"
        inputs = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
        outputs = self.model.generate(inputs.input_ids, max_length=1024, num_beams=4, early_stopping=True)

        #Using the model trained
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        #Display answer
        dispatcher.utter_message(text=f"The answer is: {answer}")
        return []


class ActionDefaultFallback(Action):
    def name(self):
        return "action_default_fallback"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text=f"Our bot is not trained on this type of interactions. Please reformulate your interaction.")
        return []
