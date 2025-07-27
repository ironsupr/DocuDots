"""
Configuration management for DocuDots PDF Analysis Module
=========================================================
"""

import os
from typing import Dict, Any


class Config:
    """
    Configuration class for DocuDots PDF analysis.
    
    This class centralizes all configuration options for the PDF analysis module,
    including processing limits, heading detection parameters, and system settings.
    """
    
    def __init__(self):
        """Initialize configuration with default values."""
        
        # File processing limits
        self.MAX_FILE_SIZE_MB = int(os.getenv('DOCUDOTS_MAX_FILE_SIZE_MB', '100'))
        self.MAX_PAGES = int(os.getenv('DOCUDOTS_MAX_PAGES', '1000'))
        self.MAX_PROCESSING_TIME_SECONDS = int(os.getenv('DOCUDOTS_MAX_PROCESSING_TIME', '300'))
        self.MAX_HEADINGS_PER_DOCUMENT = int(os.getenv('DOCUDOTS_MAX_HEADINGS', '50'))
        self.MAX_TEXT_BLOCKS = int(os.getenv('DOCUDOTS_MAX_TEXT_BLOCKS', '10000'))
        
        # Heading detection parameters
        self.HEADING_SCORE_THRESHOLD = int(os.getenv('DOCUDOTS_HEADING_THRESHOLD', '25'))
        self.FONT_SIZE_RATIOS = {
            'H1': float(os.getenv('DOCUDOTS_H1_RATIO', '1.5')),
            'H2': float(os.getenv('DOCUDOTS_H2_RATIO', '1.2')),
            'H3': float(os.getenv('DOCUDOTS_H3_RATIO', '1.1'))
        }
        
        # Pattern weights for heading detection
        self.PATTERN_WEIGHTS = {
            'font_size_large': int(os.getenv('DOCUDOTS_WEIGHT_SIZE_LARGE', '25')),
            'font_size_medium': int(os.getenv('DOCUDOTS_WEIGHT_SIZE_MEDIUM', '15')),
            'font_bold': int(os.getenv('DOCUDOTS_WEIGHT_BOLD', '15')),
            'text_short': int(os.getenv('DOCUDOTS_WEIGHT_SHORT', '10')),
            'text_caps': int(os.getenv('DOCUDOTS_WEIGHT_CAPS', '10')),
            'position_top': int(os.getenv('DOCUDOTS_WEIGHT_POSITION', '5')),
            'numeric_prefix': int(os.getenv('DOCUDOTS_WEIGHT_NUMERIC', '8')),
            'bullet_prefix': int(os.getenv('DOCUDOTS_WEIGHT_BULLET', '5'))
        }
        
        # Retry and timeout settings
        self.RETRY_MAX_ATTEMPTS = int(os.getenv('DOCUDOTS_RETRY_ATTEMPTS', '3'))
        self.RETRY_DELAY = float(os.getenv('DOCUDOTS_RETRY_DELAY', '1.0'))
        self.RETRY_BACKOFF = float(os.getenv('DOCUDOTS_RETRY_BACKOFF', '2.0'))
        
        # Circuit breaker settings
        self.CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv('DOCUDOTS_CB_THRESHOLD', '5'))
        self.CIRCUIT_BREAKER_TIMEOUT = int(os.getenv('DOCUDOTS_CB_TIMEOUT', '60'))
        
        # System resource monitoring
        self.MEMORY_LIMIT_MB = int(os.getenv('DOCUDOTS_MEMORY_LIMIT_MB', '512'))
        self.CPU_USAGE_THRESHOLD = float(os.getenv('DOCUDOTS_CPU_THRESHOLD', '80.0'))
        
        # Logging configuration
        self.LOG_LEVEL = os.getenv('DOCUDOTS_LOG_LEVEL', 'INFO')
        self.LOG_FORMAT = os.getenv('DOCUDOTS_LOG_FORMAT', 
                                   '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Multilingual support
        self.ENABLE_MULTILINGUAL = os.getenv('DOCUDOTS_MULTILINGUAL', 'true').lower() == 'true'
        self.SUPPORTED_LANGUAGES = os.getenv('DOCUDOTS_LANGUAGES', 'en,es,fr,de,it,pt,ru,zh,ja,ko,ar,hi').split(',')
        
        # Output formatting
        self.OUTPUT_ENCODING = os.getenv('DOCUDOTS_OUTPUT_ENCODING', 'utf-8')
        self.JSON_INDENT = int(os.getenv('DOCUDOTS_JSON_INDENT', '2'))
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return {
            'processing_limits': {
                'max_file_size_mb': self.MAX_FILE_SIZE_MB,
                'max_pages': self.MAX_PAGES,
                'max_processing_time_seconds': self.MAX_PROCESSING_TIME_SECONDS,
                'max_headings_per_document': self.MAX_HEADINGS_PER_DOCUMENT,
                'max_text_blocks': self.MAX_TEXT_BLOCKS
            },
            'heading_detection': {
                'score_threshold': self.HEADING_SCORE_THRESHOLD,
                'font_size_ratios': self.FONT_SIZE_RATIOS,
                'pattern_weights': self.PATTERN_WEIGHTS
            },
            'retry_settings': {
                'max_attempts': self.RETRY_MAX_ATTEMPTS,
                'delay': self.RETRY_DELAY,
                'backoff': self.RETRY_BACKOFF
            },
            'circuit_breaker': {
                'failure_threshold': self.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                'timeout': self.CIRCUIT_BREAKER_TIMEOUT
            },
            'system_resources': {
                'memory_limit_mb': self.MEMORY_LIMIT_MB,
                'cpu_usage_threshold': self.CPU_USAGE_THRESHOLD
            },
            'logging': {
                'level': self.LOG_LEVEL,
                'format': self.LOG_FORMAT
            },
            'multilingual': {
                'enabled': self.ENABLE_MULTILINGUAL,
                'supported_languages': self.SUPPORTED_LANGUAGES
            },
            'output': {
                'encoding': self.OUTPUT_ENCODING,
                'json_indent': self.JSON_INDENT
            }
        }
    
    def validate(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If configuration values are invalid
        """
        if self.MAX_FILE_SIZE_MB <= 0:
            raise ValueError("MAX_FILE_SIZE_MB must be positive")
        
        if self.MAX_PAGES <= 0:
            raise ValueError("MAX_PAGES must be positive")
        
        if self.MAX_PROCESSING_TIME_SECONDS <= 0:
            raise ValueError("MAX_PROCESSING_TIME_SECONDS must be positive")
        
        if not all(ratio > 0 for ratio in self.FONT_SIZE_RATIOS.values()):
            raise ValueError("All font size ratios must be positive")
        
        if self.RETRY_MAX_ATTEMPTS < 1:
            raise ValueError("RETRY_MAX_ATTEMPTS must be at least 1")
        
        if self.RETRY_DELAY < 0:
            raise ValueError("RETRY_DELAY must be non-negative")
        
        return True
