import json
import pickle
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional
import shutil
from datetime import datetime

class DistributedStorage:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def _get_content_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_storage_path(self, content_hash: str) -> Path:
        # Distributed file structure: base/hash[:2]/hash[2:4]/full_hash
        return self.base_path / content_hash[:2] / content_hash[2:4]
    
    def store_content(self, content: str, metadata: Dict[str, Any]) -> str:
        content_hash = self._get_content_hash(content)
        storage_path = self._get_storage_path(content_hash)
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # Store content
        content_file = storage_path / f"{content_hash}.txt"
        content_file.write_text(content)
        
        # Store metadata
        metadata_file = storage_path / f"{content_hash}_meta.json"
        metadata['created_at'] = datetime.utcnow().isoformat()
        metadata['content_hash'] = content_hash
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        return content_hash
    
    def retrieve_content(self, content_hash: str) -> Optional[Dict[str, Any]]:
        storage_path = self._get_storage_path(content_hash)
        content_file = storage_path / f"{content_hash}.txt"
        metadata_file = storage_path / f"{content_hash}_meta.json"
        
        if not content_file.exists() or not metadata_file.exists():
            return None
            
        content = content_file.read_text()
        metadata = json.loads(metadata_file.read_text())
        
        return {
            'content': content,
            'metadata': metadata
        }
    
    def list_contents(self, pattern: str = "*") -> list:
        """List all stored contents with their metadata"""
        contents = []
        for hash_dir in self.base_path.glob("[0-9a-f][0-9a-f]"):
            for sub_dir in hash_dir.glob("[0-9a-f][0-9a-f]"):
                for meta_file in sub_dir.glob("*_meta.json"):
                    try:
                        metadata = json.loads(meta_file.read_text())
                        contents.append(metadata)
                    except:
                        continue
        return contents