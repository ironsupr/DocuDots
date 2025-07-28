"""
Custom exceptions for DocuDots PDF Structure Analysis Module
============================================================
"""


class PDFAnalysisError(Exception):
    """Base exception class for PDF analysis errors."""
    pass


class PDFValidationError(PDFAnalysisError):
    """Raised when PDF file validation fails."""
    
    def __init__(self, message: str, filename: str = None, details: dict = None):
        self.filename = filename
        self.details = details or {}
        super().__init__(message)


class PDFCorruptError(PDFValidationError):
    """Raised when PDF file is corrupted or unreadable."""
    pass


class PDFEmptyError(PDFValidationError):
    """Raised when PDF file is empty or has no content."""
    pass


class PDFLargeError(PDFValidationError):
    """Raised when PDF file exceeds size limits."""
    pass


class PDFPasswordError(PDFValidationError):
    """Raised when PDF file is password protected."""
    pass


class AnalysisTimeoutError(PDFAnalysisError):
    """Raised when analysis times out."""
    pass


class CircuitBreakerOpenError(PDFAnalysisError):
    """Raised when circuit breaker is open due to repeated failures."""
    pass


class ConfigurationError(PDFAnalysisError):
    """Raised when configuration is invalid."""
    pass


class ResourceLimitError(PDFAnalysisError):
    """Raised when resource limits are exceeded."""
    
    def __init__(self, message: str, resource_type: str = None, limit: str = None):
        self.resource_type = resource_type
        self.limit = limit
        super().__init__(message)


class HeadingDetectionError(PDFAnalysisError):
    """Raised when heading detection fails completely."""
    pass


class OutputGenerationError(PDFAnalysisError):
    """Raised when JSON output generation fails."""
    pass
