import requests
import base64
from typing import List, Dict, Any
import os
import logging
from ..config.huggingface_config import HuggingFaceModelRegistry

class AdvancedImageProcessor:
    """Enhanced image processing with multiple model support"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
        self.current_model = HuggingFaceModelRegistry.get_model("image_captioning", "vit-gpt2")
    
    async def extract_keywords(self, image_data: str) -> str:
        """Extract comprehensive description from image"""
        try:
            # Primary caption generation
            primary_caption = await self._generate_primary_caption(image_data)
            
            # Enhanced description with object detection
            enhanced_description = await self._enhance_with_object_detection(image_data, primary_caption)
            
            return enhanced_description
            
        except Exception as e:
            self.logger.error(f"Image processing failed: {e}")
            raise Exception(f"Image processing failed: {e}")
    
    async def _generate_primary_caption(self, image_data: str) -> str:
        """Generate primary image caption"""
        API_URL = f"https://api-inference.huggingface.co/models/{self.current_model}"
        
        if image_data.startswith('http'):
            payload = {"inputs": image_data}
        else:
            payload = {
                "inputs": {
                    "image": image_data
                }
            }
        
        response = requests.post(API_URL, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result[0]['generated_text']
    
    async def _enhance_with_object_detection(self, image_data: str, base_caption: str) -> str:
        """Enhance caption with object detection context"""
        try:
            model_name = HuggingFaceModelRegistry.get_model("object_detection", "detr")
            object_detection_url = f"https://api-inference.huggingface.co/models/{model_name}"
            
            if image_data.startswith('http'):
                payload = {"inputs": image_data}
            else:
                payload = {
                    "inputs": {
                        "image": image_data
                    }
                }
            
            response = requests.post(object_detection_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                objects = response.json()
                key_objects = [obj['label'] for obj in objects if obj['score'] > 0.7][:5]
                
                if key_objects:
                    objects_text = ", ".join(key_objects)
                    return f"{base_caption}. Key elements include: {objects_text}."
            
            return base_caption
            
        except Exception as e:
            self.logger.warning(f"Object detection enhancement failed: {e}")
            return base_caption
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to different image processing model"""
        try:
            self.current_model = HuggingFaceModelRegistry.get_model("image_captioning", model_name)
            return True
        except ValueError:
            self.logger.error(f"Image model {model_name} not found")
            return False