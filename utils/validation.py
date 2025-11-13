import re
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse
import base64

class InputValidator:
    """Validation utilities for input data"""
    
    @staticmethod
    def validate_keyword_input(keyword: str) -> Tuple[bool, str]:
        """Validate keyword input"""
        if not keyword or not keyword.strip():
            return False, "Keyword cannot be empty"
        
        if len(keyword.strip()) < 2:
            return False, "Keyword must be at least 2 characters long"
        
        if len(keyword) > 200:
            return False, "Keyword must be less than 200 characters"
        
        # Check for potentially harmful patterns
        harmful_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+="
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, keyword, re.IGNORECASE):
                return False, "Input contains potentially harmful content"
        
        return True, "Valid"
    
    @staticmethod
    def validate_image_input(image_data: str) -> Tuple[bool, str]:
        """Validate image input (base64 or URL)"""
        if image_data.startswith('http'):
            # Validate URL
            try:
                result = urlparse(image_data)
                if all([result.scheme, result.netloc]):
                    return True, "Valid URL"
                else:
                    return False, "Invalid URL format"
            except:
                return False, "Invalid URL"
        else:
            # Validate base64
            try:
                base64.b64decode(image_data)
                return True, "Valid base64 image"
            except:
                return False, "Invalid base64 image data"
    
    @staticmethod
    def validate_tone(tone: str, available_tones: List[str]) -> Tuple[bool, str]:
        """Validate tone parameter"""
        if tone not in available_tones:
            return False, f"Tone must be one of: {', '.join(available_tones)}"
        return True, "Valid tone"
    
    @staticmethod
    def validate_length(length: int) -> Tuple[bool, str]:
        """Validate content length parameter"""
        if length < 50:
            return False, "Content length must be at least 50 characters"
        if length > 5000:
            return False, "Content length must be less than 5000 characters"
        return True, "Valid length"

class ContentSanitizer:
    """Sanitization utilities for generated content"""
    
    @staticmethod
    def sanitize_generated_content(content: str) -> str:
        """Sanitize generated content to remove potential issues"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()
        
        # Ensure proper sentence endings
        if content and not content[-1] in '.!?':
            content += '.'
        
        # Remove any potential HTML/JS injections
        content = re.sub(r'<script.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        
        return content
    
    @staticmethod
    def truncate_content(content: str, max_length: int) -> str:
        """Truncate content to specified length at sentence boundary"""
        if len(content) <= max_length:
            return content
        
        # Find the last sentence end before max_length
        truncated = content[:max_length]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        sentence_end = max(last_period, last_exclamation, last_question)
        
        if sentence_end > 0:
            return content[:sentence_end + 1]
        else:
            return content[:max_length - 3] + '...'