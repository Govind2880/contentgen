import uvicorn
from api.routes import app
import logging
from storage.distributed_storage import DistributedStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_storage():
    """Initialize distributed storage"""
    storage = DistributedStorage("./storage/distributed")
    logger.info("Distributed storage initialized")
    return storage

if __name__ == "__main__":
    logger.info("Starting Intelligent Content Generation Framework")
    
    # Initialize components
    storage = initialize_storage()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )