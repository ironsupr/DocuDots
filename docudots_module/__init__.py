"""
DocuDots - PDF Structure Extraction Module
==========================================

A robust Python module for extracting structured outlines from PDF documents.

Features:
- Multi-factor heading detection (font size, weight, positioning)
- Multilingual support
- Robust error handling and validation
- Retry logic with timeout and circuit breaker patterns
- Clean JSON output format

Usage:
    from docudots_module import PDFAnalyzer
    
    analyzer = PDFAnalyzer()
    result = analyzer.analyze_pdf("document.pdf")
    print(result)

Author: Adobe India Hackathon - Challenge 1A
Version: 1.0.0
"""

from .core import PDFAnalyzer
from .exceptions import (
    PDFAnalysisError,
    PDFValidationError,
    PDFCorruptError,
    PDFEmptyError,
    PDFLargeError,
    PDFPasswordError,
    AnalysisTimeoutError,
    CircuitBreakerOpenError
)
from .config import Config

__version__ = "1.0.0"
__author__ = "Adobe India Hackathon - Challenge 1A"
__all__ = [
    "PDFAnalyzer",
    "PDFAnalysisError",
    "PDFValidationError", 
    "PDFCorruptError",
    "PDFEmptyError",
    "PDFLargeError",
    "PDFPasswordError",
    "AnalysisTimeoutError",
    "CircuitBreakerOpenError",
    "Config"
]
