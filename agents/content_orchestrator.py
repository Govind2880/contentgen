import logging
from typing import Dict, Any, List
from ..models.content_generator import ContentGenerator
from ..models.tone_analyzer import AdvancedToneAnalyzer

class ContentOrchestrator:
    """Handles complex content generation workflows"""
    
    def __init__(self):
        self.content_generator = ContentGenerator()
        self.tone_analyzer = AdvancedToneAnalyzer()
        self.logger = logging.getLogger(__name__)
    
    async def generate_content_variations(self, 
                                        prompt: str, 
                                        tones: List[str] = None,
                                        lengths: List[int] = None) -> Dict[str, Any]:
        """Generate multiple content variations"""
        if tones is None:
            tones = ["professional", "casual", "creative"]
        
        if lengths is None:
            lengths = [200, 500, 1000]
        
        variations = {}
        
        for tone in tones:
            variations[tone] = {}
            for length in lengths:
                content = await self.content_generator.generate(
                    prompt=prompt,
                    tone=tone,
                    max_length=length
                )
                variations[tone][f"{length}_chars"] = content
        
        return variations
    
    async def optimize_content(self, 
                             original_content: str, 
                             target_tone: str,
                             target_length: int = None) -> str:
        """Optimize existing content for different tone/length"""
        # Analyze current tone
        analysis = await self.tone_analyzer.analyze_tone_multi_model(original_content)
        current_tone = analysis["primary_tone"]
        
        if current_tone == target_tone and not target_length:
            return original_content  # No optimization needed
        
        # Generate optimized version
        prompt = f"Optimize this content for {target_tone} tone: {original_content}"
        optimized = await self.content_generator.generate(
            prompt=prompt,
            tone=target_tone,
            max_length=target_length
        )
        
        return optimized