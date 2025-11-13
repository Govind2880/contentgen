from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import base64
import logging

from ..agents.orchestrator import OrchestratorAgent
from ..storage.distributed_storage import DistributedStorage
from ..storage.content_manager import ContentManager
from ..utils.validation import InputValidator, ContentSanitizer
from ..models.tone_models import AdvancedToneAnalyzer
from .middleware import LoggingMiddleware, RateLimitingMiddleware, SecurityHeadersMiddleware

app = FastAPI(
    title="Intelligent Content Generation Framework",
    description="A distributed agentic framework for dynamic content generation",
    version="1.0.0"
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitingMiddleware, requests_per_minute=60)
app.add_middleware(SecurityHeadersMiddleware)

# Initialize components
storage = DistributedStorage("./storage/distributed")
content_manager = ContentManager(storage)
orchestrator = OrchestratorAgent(storage)
tone_analyzer = AdvancedToneAnalyzer()
input_validator = InputValidator()

logger = logging.getLogger(__name__)

class ContentRequest(BaseModel):
    input_data: str
    input_type: str = "keyword"
    tone: Optional[str] = None
    length: Optional[int] = None
    enhance_with_objects: bool = False

class ContentResponse(BaseModel):
    content: str
    content_hash: str
    metadata: dict
    processing_time: Optional[float] = None

class AnalyticsResponse(BaseModel):
    total_content_generated: int
    tone_distribution: dict
    length_distribution: dict
    daily_stats: dict
    model_usage: dict

class ToneAnalysisRequest(BaseModel):
    text: str

class ToneAnalysisResponse(BaseModel):
    primary_tone: str
    confidence_scores: Dict[str, float]
    suggested_tone: str
    confidence_level: str

@app.post("/generate-content", response_model=ContentResponse)
async def generate_content(
    request: ContentRequest,
    background_tasks: BackgroundTasks
):
    """Generate content with dynamic tone and length control"""
    try:
        # Validate input
        if request.input_type == "keyword":
            is_valid, message = input_validator.validate_keyword_input(request.input_data)
        else:
            is_valid, message = input_validator.validate_image_input(request.input_data)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        if request.tone:
            is_valid, message = input_validator.validate_tone(
                request.tone, 
                tone_analyzer.available_tones
            )
            if not is_valid:
                raise HTTPException(status_code=400, detail=message)
        
        if request.length:
            is_valid, message = input_validator.validate_length(request.length)
            if not is_valid:
                raise HTTPException(status_code=400, detail=message)
        
        # Generate content
        import time
        start_time = time.time()
        
        result = await orchestrator.generate_content(
            input_data=request.input_data,
            input_type=request.input_type,
            target_tone=request.tone,
            target_length=request.length
        )
        
        processing_time = time.time() - start_time
        
        # Sanitize and store with analytics
        sanitized_content = ContentSanitizer.sanitize_generated_content(result['content'])
        content_hash = content_manager.store_content_with_analytics(
            sanitized_content, 
            result['metadata']
        )
        
        return ContentResponse(
            content=sanitized_content,
            content_hash=content_hash,
            metadata=result['metadata'],
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-from-image", response_model=ContentResponse)
async def generate_from_image(
    file: UploadFile = File(...),
    tone: Optional[str] = None,
    length: Optional[int] = None
):
    """Generate content from uploaded image"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and encode image
        image_data = await file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        result = await orchestrator.generate_content(
            input_data=base64_image,
            input_type="image",
            target_tone=tone,
            target_length=length
        )
        
        # Store with analytics
        content_hash = content_manager.store_content_with_analytics(
            result['content'], 
            result['metadata']
        )
        
        return ContentResponse(
            content=result['content'],
            content_hash=content_hash,
            metadata=result['metadata']
        )
        
    except Exception as e:
        logger.error(f"Image content generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-tone", response_model=ToneAnalysisResponse)
async def analyze_tone(request: ToneAnalysisRequest):
    """Analyze tone of input text"""
    try:
        analysis_result = await tone_analyzer.analyze_tone_multi_model(request.text)
        return ToneAnalysisResponse(**analysis_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/content/{content_hash}")
async def get_content(content_hash: str):
    """Retrieve generated content by hash"""
    content_data = storage.retrieve_content(content_hash)
    if not content_data:
        raise HTTPException(status_code=404, detail="Content not found")
    return content_data

@app.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """Get framework analytics"""
    analytics = content_manager.get_analytics()
    return AnalyticsResponse(**analytics)

@app.get("/search-content")
async def search_content(
    tone: Optional[str] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    date_from: Optional[str] = None
):
    """Search generated content with filters"""
    results = content_manager.search_content(
        tone=tone,
        min_length=min_length,
        max_length=max_length,
        date_from=date_from
    )
    return {"results": results, "count": len(results)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "framework": "Intelligent Content Generation",
        "version": "1.0.0",
        "components": {
            "storage": "operational",
            "agents": "operational",
            "models": "operational"
        }
    }

@app.get("/models/available")
async def get_available_models():
    """Get available Hugging Face models"""
    from ..config.huggingface_config import HuggingFaceModelRegistry
    return {
        "text_generation": HuggingFaceModelRegistry.TEXT_GENERATION_MODELS,
        "image_captioning": HuggingFaceModelRegistry.IMAGE_CAPTIONING_MODELS,
        "zero_shot": HuggingFaceModelRegistry.ZERO_SHOT_MODELS
    }