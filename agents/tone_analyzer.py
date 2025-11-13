import requests
from typing import Dict, Any
import logging
import os

class ToneAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_tones = ["professional", "casual", "academic", "creative", "persuasive"]
    
    async def analyze_tone(self, text: str) -> str:
        """
        Analyze input text to determine appropriate tone
        Uses Hugging Face zero-shot classification
        """
        try:
            API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
            headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
            
            payload = {
                "inputs": text,
                "parameters": {
                    "candidate_labels": self.available_tones,
                    "multi_label": False
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            best_tone = result['labels'][0]  # Get highest scoring tone
            
            return best_tone
            
        except Exception as e:
            self.logger.warning(f"Tone analysis failed: {e}, using default tone")
            return "professional"