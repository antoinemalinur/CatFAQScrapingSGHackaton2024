from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import Tracker
from rasa_sdk.events import SlotSet
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch

class ActionAnswerQuestion(Action):
    def name(self):
        return "action_answer_question"

    def run(self, dispatcher, tracker, domain):
        question = tracker.latest_message['text']
        context = self.get_faq_context(question)  # You can get FAQ data from your own source or predefined context.

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
    
    def get_faq_context(self, question):
        # In your case, this method can fetch the FAQ context from a database, a file, or a predefined list
        # Example context:
        faq_data = {
            "What is the CATNMSPlan?": "The CATNMSPlan is a framework designed to help organizations manage their network services.",
            "What is the return policy?": "Our return policy allows returns within 30 days of purchase.",
            # Add other FAQ mappings here
        }

        # Use a default message if no context is found
        return faq_data.get(question, "Sorry, I don't have information on that.")
