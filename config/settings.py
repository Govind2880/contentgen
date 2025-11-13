import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class HuggingFaceConfig:
    api_key: str
    base_url: str = "https://api-inference.huggingface.co/models"
    timeout: int = 30
    max_retries: int = 3

@dataclass
class StorageConfig:
    distributed_storage_path: str = "./storage/distributed"
    content_archive_path: str = "./storage/archive"
    max_file_size: int = 100 * 1024 * 1024  # 100MB

@dataclass
class AgentConfig:
    max_content_length: int = 5000
    default_tone: str = "professional"
    available_tones: list = None
    
    def __post_init__(self):
        if self.available_tones is None:
            self.available_tones = ["professional", "casual", "academic", "creative", "persuasive"]

class Config:
    def __init__(self):
        self.huggingface = HuggingFaceConfig(
            api_key=os.getenv("HUGGINGFACE_API_KEY", "")
        )
        self.storage = StorageConfig()
        self.agents = AgentConfig()