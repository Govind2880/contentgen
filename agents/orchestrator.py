import logging
from typing import Dict, Any, Optional
from ..models.tone_analyzer import AdvancedToneAnalyzer
from ..models.content_generator import ContentGenerator
from ..storage.distributed_storage import DistributedStorage
from ..utils.image_processor import AdvancedImageProcessor

class OrchestratorAgent:
    def __init__(self, storage: DistributedStorage):
        self.storage = storage
        self.tone_analyzer = AdvancedToneAnalyzer()
        self.content_generator = ContentGenerator()
        self.image_processor = AdvancedImageProcessor()
        self.logger = logging.getLogger(__name__)
    
    async def generate_content(self, 
                             input_data: str,
                             input_type: str = "keyword",
                             target_tone: Optional[str] = None,
                             target_length: Optional[int] = None) -> Dict[str, Any]:
        """
        Main orchestration method for content generation
        """
        try:
            # Process input based on type
            if input_type == "image":
                self.logger.info("Processing image input")
                processed_input = await self.image_processor.extract_keywords(input_data)
            else:
                processed_input = input_data
            
            # Analyze and determine tone if not provided
            if not target_tone:
                self.logger.info("Analyzing tone automatically")
                tone_analysis = await self.tone_analyzer.analyze_tone_multi_model(processed_input)
                target_tone = tone_analysis["suggested_tone"]
            
            # Generate content
            self.logger.info(f"Generating content with tone: {target_tone}")
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
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            raise