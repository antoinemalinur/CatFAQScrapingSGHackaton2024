from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import Tracker
from rasa_sdk.events import SlotSet
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
import os
import json

class ActionAnswerQuestion(Action):
    def __init__(self):
        # Load the FAQ JSON file into memory (only once during initialization)
        faq_path = os.path.join(os.getcwd(), 'data', 'squad_faq.json')
        with open(faq_path, 'r') as f:
            self.faq_data = json.load(f)

    def name(self):
        return "action_answer_question"

    def run(self, dispatcher, tracker, domain):
        question = tracker.latest_message['text']
        context = self.get_faq_context(question)  # You can get FAQ data from your own source or predefined context.

        print(question)
        print(context)
        # Load the fine-tuned BERT model
        tokenizer = AutoTokenizer.from_pretrained("./qa_finetuned_model")
        model = AutoModelForQuestionAnswering.from_pretrained("./qa_finetuned_model")

        # Prepare inputs for BERT model
        inputs = tokenizer(question, context, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            start_scores = outputs.start_logits
            end_scores = outputs.end_logits

            start_idx = torch.argmax(start_scores)
            end_idx = torch.argmax(end_scores) + 1
            answer = tokenizer.convert_tokens_to_string(
                tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][start_idx:end_idx])
            )
        
        # Send the response back to the user
        dispatcher.utter_message(text=f"The answer is: {answer}")
        return []
    
    def get_faq_context(self, question: str) -> str:
        # Search through the loaded faq_data to find the relevant context
        print(question)
        for category in self.faq_data.get('data', []):
            print(category)
            for paragraph in category.get('paragraphs', []):
                print(paragraph)
                for qas in paragraph.get('qas', []):
                    if qas.get('question').lower() == question.lower():
                        return paragraph.get('context', "Sorry, I don't have information on that.")
        return "Sorry, I don't have information on that."

