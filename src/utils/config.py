#!/usr/bin/env python3
"""
Configuration management for DocuDots PDF Structure Analysis Tool
Adobe India Hackathon - Challenge 1A
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
from .exceptions import ConfigurationError


@dataclass
class ProcessingLimits:
    """Processing limits and thresholds."""
    max_file_size_mb: int = 100  # Maximum PDF file size in MB
    max_pages: int = 1000        # Maximum number of pages per PDF
    max_processing_time_seconds: int = 300  # 5 minutes timeout
    max_headings_per_document: int = 50     # Maximum headings to extract
    max_text_blocks: int = 10000            # Maximum text blocks to process


@dataclass
class HeadingConfig:
    """Heading detection configuration."""
    score_threshold: int = 25               # Minimum score for heading candidates
    font_size_ratios: Dict[str, float] = None
    pattern_weights: Dict[str, int] = None
    
    def __post_init__(self):
        if self.font_size_ratios is None:
            self.font_size_ratios = {
                'H1': 1.5,  # H1 headings should be 1.5x body text size
                'H2': 1.2,  # H2 headings should be 1.2x body text size
                'H3': 1.1   # H3 headings should be 1.1x body text size
            }
        
        if self.pattern_weights is None:
            self.pattern_weights = {
                'font_size': 25,      # 25% weight for font size
                'typography': 25,     # 25% weight for bold/italic
                'position': 20,       # 20% weight for page position
                'text_patterns': 15,  # 15% weight for text patterns
                'context': 10,        # 10% weight for surrounding context
                'length': 5           # 5% weight for text length
            }


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_file_logging: bool = False
    log_file_path: str = "/app/logs/docudots.log"


class Config:
    """Main configuration class for DocuDots."""
    
    def __init__(self):
        self.processing_limits = ProcessingLimits()
        self.heading_config = HeadingConfig()
        self.logging_config = LoggingConfig()
        
        # Load environment variables
        self._load_from_environment()
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # Processing limits
        if max_size := os.getenv('DOCUDOTS_MAX_FILE_SIZE_MB'):
            self.processing_limits.max_file_size_mb = int(max_size)
        
        if max_pages := os.getenv('DOCUDOTS_MAX_PAGES'):
            self.processing_limits.max_pages = int(max_pages)
        
        if timeout := os.getenv('DOCUDOTS_PROCESSING_TIMEOUT'):
            self.processing_limits.max_processing_time_seconds = int(timeout)
        
        # Heading detection
        if threshold := os.getenv('DOCUDOTS_HEADING_THRESHOLD'):
            self.heading_config.score_threshold = int(threshold)
        
        # Logging
        if log_level := os.getenv('DOCUDOTS_LOG_LEVEL'):
            self.logging_config.level = log_level.upper()
        
        if enable_file_log := os.getenv('DOCUDOTS_ENABLE_FILE_LOGGING'):
            self.logging_config.enable_file_logging = enable_file_log.lower() == 'true'
    
    def get_supported_patterns(self) -> Dict[str, List[str]]:
        """Get supported heading patterns by language."""
        return {
            'en': [
                # H1 patterns - Major sections
                'abstract', 'introduction', 'conclusion', 'summary', 'overview',
                'background', 'methodology', 'results', 'discussion', 'references',
                'about', 'experience', 'education', 'skills', 'projects', 'contact',
                'objective', 'profile', 'qualifications', 'achievements', 'awards'
            ],
            'academic': [
                # Academic-specific patterns
                'literature review', 'data analysis', 'findings', 'implications',
                'future work', 'acknowledgments', 'appendix', 'bibliography'
            ],
            'business': [
                # Business document patterns
                'executive summary', 'market analysis', 'financial overview',
                'recommendations', 'action items', 'next steps'
            ]
        }
    
    def validate(self) -> bool:
        """Validate the configuration."""
        try:
            # Validate processing limits
            assert self.processing_limits.max_file_size_mb > 0, "Max file size must be positive"
            assert self.processing_limits.max_pages > 0, "Max pages must be positive"
            assert self.processing_limits.max_processing_time_seconds > 0, "Timeout must be positive"
            
            # Validate heading config
            assert self.heading_config.score_threshold >= 0, "Score threshold must be non-negative"
            assert all(ratio > 0 for ratio in self.heading_config.font_size_ratios.values()), \
                "Font size ratios must be positive"
            
            # Validate logging config
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            assert self.logging_config.level in valid_levels, f"Log level must be one of {valid_levels}"
            
            return True
            
        except AssertionError as e:
            raise ConfigurationError(f"Configuration validation failed: {e}")


# Global configuration instance
config = Config()
