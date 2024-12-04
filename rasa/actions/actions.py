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
        import json
        with open("./data/cat_specs.json", 'r') as f:
            cat_specs_data = json.load(f)

        self.chunks = [value["content"] for key, value in cat_specs_data.items() if
                  "content" in value and value["content"] != ""]
        # Charger le modèle SentenceTransformer pour les embeddings
        self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        chunk_embeddings = self.embedder.encode(self.chunks)

        # Build FAISS index
        self.dimension = chunk_embeddings.shape[1]
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(np.array(chunk_embeddings))

        # Charger le modèle T5 fine-tuné
        self.model_name = "./qa_finetuned_model"
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)

    def name(self):
        return "action_answer_question"

    def run(self, dispatcher, tracker, domain):
        # Obtenir la question de l'utilisateur
        user_question = tracker.latest_message['text']


        # Encoder la question
        query_embedding = self.embedder.encode([user_question])
        _, indices = self.index.search(np.array(query_embedding), k=5)  # Retrieve top 3 matches
        retrieved_chunks = [self.chunks[i] for i in indices[0]]
        context = " ".join(retrieved_chunks)

        input_text = f"question: {user_question} context: {context}"
        inputs = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
        outputs = self.model.generate(inputs.input_ids, max_length=1024, num_beams=4, early_stopping=True)
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Envoyer la réponse à l'utilisateur
        dispatcher.utter_message(text=f"The answer is: {answer}")
        return []
