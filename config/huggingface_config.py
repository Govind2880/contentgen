import os
from typing import Dict, List
from .settings import HuggingFaceConfig

class HuggingFaceModelRegistry:
    """Registry for Hugging Face models used in the framework"""
    
    TEXT_GENERATION_MODELS = {
        "dialoGPT": "microsoft/DialoGPT-large",
        "blenderbot": "facebook/blenderbot-400M-distill",
        "flan-t5": "google/flan-t5-large",
        "gpt2": "gpt2",
        "distilgpt2": "distilgpt2"
    }
    
    IMAGE_CAPTIONING_MODELS = {
        "vit-gpt2": "nlpconnect/vit-gpt2-image-captioning",
        "blip": "Salesforce/blip-image-captioning-large"
    }
    
    ZERO_SHOT_MODELS = {
        "bart-mnli": "facebook/bart-large-mnli",
        "deberta-mnli": "microsoft/deberta-large-mnli"
    }
    
    @classmethod
    def get_model(cls, model_type: str, model_name: str) -> str:
        """Get model identifier by type and name"""
        model_map = {
            "text_generation": cls.TEXT_GENERATION_MODELS,
            "image_captioning": cls.IMAGE_CAPTIONING_MODELS,
            "zero_shot": cls.ZERO_SHOT_MODELS
        }
        
        if model_type in model_map and model_name in model_map[model_type]:
            return model_map[model_type][model_name]
        raise ValueError(f"Model {model_name} of type {model_type} not found")