import requests
import os
import logging
from typing import Optional, Dict, List
from ..config.huggingface_config import HuggingFaceModelRegistry, HuggingFaceConfig

class HuggingFaceModelManager:
    """Manager for Hugging Face model operations"""
    
    def __init__(self, config: HuggingFaceConfig):
        self.config = config
        self.available_models = HuggingFaceModelRegistry.TEXT_GENERATION_MODELS
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to different text generation model"""
        if model_name in self.available_models:
            self.current_model = self.available_models[model_name]
            return True
        return False
    
    def get_available_models(self) -> Dict[str, str]:
        return self.available_models

class ContentGenerator:
    """Main content generation class using Hugging Face models"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_manager = HuggingFaceModelManager(HuggingFaceConfig(api_key=os.getenv("HUGGINGFACE_API_KEY")))
        self.current_model = self.model_manager.available_models["dialoGPT"]
        self.headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
    
    async def generate(self, 
                      prompt: str, 
                      tone: str = "professional",
                      max_length: Optional[int] = None) -> str:
        """Generate content using Hugging Face API"""
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
            
            response = requests.post(API_URL, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result[0]['generated_text']
            
            return self._post_process_content(generated_text, tone)
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            raise
    
    def _build_enhanced_prompt(self, prompt: str, tone: str, max_length: Optional[int]) -> str:
        """Build enhanced prompt with tone and length instructions"""
        tone_instructions = {
            "professional": "Write in a professional, formal tone suitable for business communication.",
            "casual": "Write in a casual, friendly tone as if talking to a friend.",
            "academic": "Write in an academic, scholarly tone with precise language.",
            "creative": "Write in a creative, imaginative tone with vivid descriptions.",
            "persuasive": "Write in a persuasive, compelling tone that convinces the reader.",
            "formal": "Write in a formal, structured tone with proper etiquette.",
            "humorous": "Write in a humorous, witty tone with appropriate jokes.",
            "technical": "Write in a technical, detailed tone with specific terminology."
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
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to different text generation model"""
        return self.model_manager.switch_model(model_name)