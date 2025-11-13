from typing import Dict, Any, Optional
from ..models.tone_models import ToneAnalyzer
from ..models.generation_models import ContentGenerator
from ..storage.distributed_storage import DistributedStorage
from ..utils.image_processor import ImageProcessor

class OrchestratorAgent:
    def __init__(self, storage: DistributedStorage):
        self.storage = storage
        self.tone_analyzer = ToneAnalyzer()
        self.content_generator = ContentGenerator()
        self.image_processor = ImageProcessor()
    
    async def generate_content(self, 
                             input_data: str,
                             input_type: str = "keyword",
                             target_tone: Optional[str] = None,
                             target_length: Optional[int] = None) -> Dict[str, Any]:
        """
        Main orchestration method for content generation
        """
        # Process input based on type
        if input_type == "image":
            processed_input = await self.image_processor.extract_keywords(input_data)
        else:
            processed_input = input_data
        
        # Analyze and determine tone if not provided
        if not target_tone:
            target_tone = await self.tone_analyzer.analyze_tone(processed_input)
        
        # Generate content
        generated_content = await self.content_generator.generate(
            prompt=processed_input,
            tone=target_tone,
            max_length=target_length
        )
        
        # Prepare metadata
        metadata = {
            'input_type': input_type,
            'original_input': input_data,
            'processed_input': processed_input,
            'tone': target_tone,
            'target_length': target_length,
            'actual_length': len(generated_content),
            'model_used': self.content_generator.current_model
        }
        
        # Store in distributed storage
        content_hash = self.storage.store_content(generated_content, metadata)
        
        return {
            'content': generated_content,
            'content_hash': content_hash,
            'metadata': metadata
        }