#!/usr/bin/env python3
"""
Custom exceptions for DocuDots PDF Structure Analysis Tool
Adobe India Hackathon - Challenge 1A
"""


class DocuDotsError(Exception):
    """Base exception class for DocuDots errors."""
    pass


class PDFValidationError(DocuDotsError):
    """Raised when PDF file validation fails."""
    
    def __init__(self, message: str, filename: str = None, details: dict = None):
        self.filename = filename
        self.details = details or {}
        super().__init__(message)


class PDFProcessingError(DocuDotsError):
    """Raised when PDF processing encounters an error."""
    
    def __init__(self, message: str, filename: str = None, stage: str = None):
        self.filename = filename
        self.stage = stage  # e.g., "text_extraction", "heading_classification"
        super().__init__(message)


class ConfigurationError(DocuDotsError):
    """Raised when configuration is invalid."""
    pass


class ResourceLimitError(DocuDotsError):
    """Raised when resource limits are exceeded."""
    
    def __init__(self, message: str, resource_type: str = None, limit: str = None):
        self.resource_type = resource_type  # e.g., "memory", "file_size", "processing_time"
        self.limit = limit
        super().__init__(message)


class HeadingDetectionError(DocuDotsError):
    """Raised when heading detection fails completely."""
    pass


class OutputGenerationError(DocuDotsError):
    """Raised when JSON output generation fails."""
    pass
