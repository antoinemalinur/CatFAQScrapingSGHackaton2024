from rasa.engine.graph import GraphComponent
from rasa.shared.nlu.training_data.message import Message
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from typing import List, Dict, Any, Text
from rasa.nlu.featurizers.featurizer import Featurizer

import logging

logger = logging.getLogger(__name__)

@DefaultV1Recipe.register(component_types=[GraphComponent, Featurizer], is_trainable=False)
class BertQAComponent(GraphComponent):
    def __init__(self, component_config: Dict[Text, Any] = None):
        logger.info("BertQAComponent is initialized")

        super().__init__(component_config)
        self.tokenizer = AutoTokenizer.from_pretrained('./qa_finetuned_model')
        self.model = AutoModelForQuestionAnswering.from_pretrained('./qa_finetuned_model')

    def process(self, message: Message, **kwargs: Any) -> None:
        logger.info(f"BertQAComponent processing message: {message.text}")

        question = message.text
        context = self.get_faq_context(question)
        
        inputs = self.tokenizer(question, context, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            start_scores = outputs.start_logits
            end_scores = outputs.end_logits
            
            start_idx = torch.argmax(start_scores)
            end_idx = torch.argmax(end_scores) + 1
            answer = self.tokenizer.convert_tokens_to_string(
                self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][start_idx:end_idx])
            )
        
        message.set("bert_answer", answer, add_to_output=True)

    def get_faq_context(self, question: str) -> str:
        faq_data = {
            "What is the CATNMSPlan?": "The CATNMSPlan is a framework designed to help organizations manage their network services.",
            "What is the return policy?": "Our return policy allows returns within 30 days of purchase.",
        }
        return faq_data.get(question, "Sorry, I don't have information on that.")
