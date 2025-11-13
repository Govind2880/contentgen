import requests
import os
import logging
from typing import Dict, List, Any
from ..config.huggingface_config import HuggingFaceModelRegistry

class AdvancedToneAnalyzer:
    """Enhanced tone analyzer with multiple classification strategies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_tones = [
            "professional", "casual", "academic", "creative", 
            "persuasive", "formal", "humorous", "technical"
        ]
        
    async def analyze_tone_multi_model(self, text: str) -> Dict[str, Any]:
        """
        Analyze tone using multiple models for consensus
        """
        try:
            # Primary analysis with BART-MNLI
            primary_tone = await self._analyze_with_bart(text)
            
            # Secondary analysis for confidence
            confidence_scores = await self._get_tone_confidence_scores(text)
            
            return {
                "primary_tone": primary_tone,
                "confidence_scores": confidence_scores,
                "suggested_tone": primary_tone,
                "confidence_level": "high" if max(confidence_scores.values()) > 0.7 else "medium"
            }
            
        except Exception as e:
            self.logger.error(f"Multi-model tone analysis failed: {e}")
            return {
                "primary_tone": "professional",
                "confidence_scores": {"professional": 1.0},
                "suggested_tone": "professional",
                "confidence_level": "low"
            }
    
    async def _analyze_with_bart(self, text: str) -> str:
        """Analyze tone using BART model"""
        API_URL = f"https://api-inference.huggingface.co/models/{HuggingFaceModelRegistry.ZERO_SHOT_MODELS['bart-mnli']}"
        headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
        
        payload = {
            "inputs": text,
            "parameters": {
                "candidate_labels": self.available_tones,
                "multi_label": False
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['labels'][0]
    
    async def _get_tone_confidence_scores(self, text: str) -> Dict[str, float]:
        """Get confidence scores for all available tones"""
        try:
            API_URL = f"https://api-inference.huggingface.co/models/{HuggingFaceModelRegistry.ZERO_SHOT_MODELS['bart-mnli']}"
            headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
            
            payload = {
                "inputs": text,
                "parameters": {
                    "candidate_labels": self.available_tones,
                    "multi_label": True
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return dict(zip(result['labels'], result['scores']))
            
        except Exception as e:
            self.logger.warning(f"Confidence scoring failed: {e}")
            return {tone: 0.0 for tone in self.available_tones}