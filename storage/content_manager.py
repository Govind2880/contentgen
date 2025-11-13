import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from storage.distributed_storage import DistributedStorage

class ContentManager:
    """High-level content management with analytics and lifecycle management"""
    
    def __init__(self, storage: DistributedStorage):
        self.storage = storage
        self.analytics_file = Path(storage.base_path) / "analytics.json"
        self._ensure_analytics_file()
    
    def _ensure_analytics_file(self):
        """Ensure analytics file exists"""
        if not self.analytics_file.exists():
            self.analytics_file.parent.mkdir(parents=True, exist_ok=True)
            initial_analytics = {
                "total_content_generated": 0,
                "tone_distribution": {},
                "length_distribution": {},
                "daily_stats": {},
                "model_usage": {}
            }
            self.analytics_file.write_text(json.dumps(initial_analytics, indent=2))
    
    def store_content_with_analytics(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store content and update analytics"""
        content_hash = self.storage.store_content(content, metadata)
        self._update_analytics(metadata)
        return content_hash
    
    def _update_analytics(self, metadata: Dict[str, Any]):
        """Update analytics with new content metadata"""
        analytics = json.loads(self.analytics_file.read_text())
        
        # Update basic stats
        analytics["total_content_generated"] += 1
        
        # Update tone distribution
        tone = metadata.get('tone', 'unknown')
        analytics["tone_distribution"][tone] = analytics["tone_distribution"].get(tone, 0) + 1
        
        # Update length distribution
        length = metadata.get('actual_length', 0)
        length_range = f"{(length // 100) * 100}-{(length // 100) * 100 + 99}"
        analytics["length_distribution"][length_range] = analytics["length_distribution"].get(length_range, 0) + 1
        
        # Update daily stats
        today = datetime.utcnow().strftime("%Y-%m-%d")
        analytics["daily_stats"][today] = analytics["daily_stats"].get(today, 0) + 1
        
        # Update model usage
        model = metadata.get('model_used', 'unknown')
        analytics["model_usage"][model] = analytics["model_usage"].get(model, 0) + 1
        
        self.analytics_file.write_text(json.dumps(analytics, indent=2))
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics"""
        return json.loads(self.analytics_file.read_text())
    
    def search_content(self, 
                      tone: Optional[str] = None,
                      min_length: Optional[int] = None,
                      max_length: Optional[int] = None,
                      date_from: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search content with filters"""
        all_contents = self.storage.list_contents()
        
        filtered_contents = []
        for content_meta in all_contents:
            # Filter by tone
            if tone and content_meta.get('tone') != tone:
                continue
            
            # Filter by length
            content_length = content_meta.get('actual_length', 0)
            if min_length and content_length < min_length:
                continue
            if max_length and content_length > max_length:
                continue
            
            # Filter by date
            if date_from:
                content_date = datetime.fromisoformat(content_meta.get('created_at', '').replace('Z', '+00:00'))
                filter_date = datetime.fromisoformat(date_from)
                if content_date < filter_date:
                    continue
            
            filtered_contents.append(content_meta)
        
        return filtered_contents
    
    def cleanup_old_content(self, days_old: int = 30):
        """Remove content older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        all_contents = self.storage.list_contents()
        
        for content_meta in all_contents:
            content_date = datetime.fromisoformat(content_meta.get('created_at', '').replace('Z', '+00:00'))
            if content_date < cutoff_date:
                # Implementation for actual deletion would go here
                self.logger.info(f"Marked content {content_meta['content_hash']} for deletion")