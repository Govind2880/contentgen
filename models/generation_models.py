import requests
import os
from typing import List, Dict, Any
from ..config.huggingface_config import HuggingFaceConfig

class HuggingFaceModelManager:
    def __init__(self, config: HuggingFaceConfig):
        self.config = config
        self.available_models = {
            "text_generation": [
                "microsoft/DialoGPT-large",
                "facebook/blenderbot-400M-distill",
                "google/flan-t5-large"
            ],
            "image_to_text": [
                "nlpconnect/vit-gpt2-image-captioning",
                "Salesforce/blip-image-captioning-large"
            ]
        }
    
    def switch_model(self, model_type: str, model_name: str):
        """Dynamically switch between different Hugging Face models"""
        if model_name in self.available_models.get(model_type, []):
            self.current_model = model_name
            return True
        return False
    
    def get_available_models(self) -> Dict[str, List[str]]:
        return self.available_models