import requests
import os
from typing import Optional
import logging

class ContentGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_model = "microsoft/DialoGPT-large"
        self.headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
    
    async def generate(self, 
                      prompt: str, 
                      tone: str = "professional",
                      max_length: Optional[int] = None) -> str:
        """
        Generate content using Hugging Face API with tone and length control
        """
        try:
            # Enhance prompt with tone and length instructions
            enhanced_prompt = self._build_enhanced_prompt(prompt, tone, max_length)
            
            API_URL = f"https://api-inference.huggingface.co/models/{self.current_model}"
            
            payload = {
                "inputs": enhanced_prompt,
                "parameters": {
                    "max_length": max_length or 300,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(API_URL, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result[0]['generated_text']
            
            return self._post_process_content(generated_text, tone)
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            raise
    
    def _build_enhanced_prompt(self, prompt: str, tone: str, max_length: Optional[int]) -> str:
        tone_instructions = {
            "professional": "Write in a professional, formal tone suitable for business communication.",
            "casual": "Write in a casual, friendly tone as if talking to a friend.",
            "academic": "Write in an academic, scholarly tone with precise language.",
            "creative": "Write in a creative, imaginative tone with vivid descriptions.",
            "persuasive": "Write in a persuasive, compelling tone that convinces the reader."
        }
        
        base_instruction = tone_instructions.get(tone, tone_instructions["professional"])
        
        if max_length:
            length_instruction = f" Keep the response under {max_length} characters."
        else:
            length_instruction = ""
        
        return f"{base_instruction}{length_instruction}\n\nTopic: {prompt}\n\nResponse:"
    
    def _post_process_content(self, content: str, tone: str) -> str:
        """Clean and format generated content"""
        # Remove any duplicate sections or artifacts
        content = content.strip()
        
        # Ensure proper sentence structure
        if not content.endswith(('.', '!', '?')):
            content += '.'
            
        return content