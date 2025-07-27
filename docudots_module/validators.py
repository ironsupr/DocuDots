"""
Input validation utilities for DocuDots PDF Analysis Module
===========================================================
"""

import os
from pathlib import Path
from typing import Optional, Tuple
import logging

import fitz  # PyMuPDF

from exceptions import (
    PDFValidationError, 
    PDFCorruptError, 
    PDFEmptyError, 
    PDFLargeError, 
    PDFPasswordError,
    ResourceLimitError
)
from config import Config


class InputValidator:
    """
    Comprehensive input validation for PDF files and system resources.
    
    This class provides validation for PDF files including file existence,
    structure integrity, size limits, and content accessibility.
    """
    
    def __init__(self, config: Config):
        """
        Initialize validator with configuration.
        
        Args:
            config (Config): Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def validate_pdf_file(self, pdf_path: Path) -> bool:
        """
        Comprehensive PDF file validation.
        
        Args:
            pdf_path (Path): Path to the PDF file
            
        Returns:
            bool: True if validation passes
            
        Raises:
            PDFValidationError: If validation fails
        """
        try:
            # Check if file exists
            if not pdf_path.exists():
                raise PDFValidationError(
                    f"PDF file does not exist: {pdf_path}",
                    filename=pdf_path.name
                )
            
            # Check if it's a file (not directory)
            if not pdf_path.is_file():
                raise PDFValidationError(
                    f"Path is not a file: {pdf_path}",
                    filename=pdf_path.name
                )
            
            # Check file extension
            if pdf_path.suffix.lower() != '.pdf':
                raise PDFValidationError(
                    f"File is not a PDF: {pdf_path.suffix}",
                    filename=pdf_path.name,
                    details={'actual_extension': pdf_path.suffix}
                )
            
            # Check file size
            file_size = pdf_path.stat().st_size
            max_size_bytes = self.config.MAX_FILE_SIZE_MB * 1024 * 1024
            
            if file_size == 0:
                raise PDFEmptyError(
                    "PDF file is empty",
                    filename=pdf_path.name,
                    details={'file_size': file_size}
                )
            
            if file_size > max_size_bytes:
                raise PDFLargeError(
                    f"PDF file too large: {file_size / (1024*1024):.1f}MB > "
                    f"{self.config.MAX_FILE_SIZE_MB}MB",
                    filename=pdf_path.name,
                    details={'file_size_mb': file_size / (1024*1024)}
                )
            
            # Validate PDF structure and content
            self._validate_pdf_structure(pdf_path)
            
            self.logger.info(f"PDF validation passed: {pdf_path.name} "
                           f"({file_size / (1024*1024):.1f}MB)")
            
            return True
            
        except (PDFValidationError, ResourceLimitError) as e:
            self.logger.error(f"PDF validation failed for {pdf_path.name}: {e}")
            raise
        
        except Exception as e:
            error_msg = f"Unexpected validation error: {e}"
            self.logger.error(f"PDF validation failed for {pdf_path.name}: {error_msg}")
            raise PDFValidationError(error_msg, filename=pdf_path.name) from e
    
    def _validate_pdf_structure(self, pdf_path: Path) -> None:
        """
        Validate internal PDF structure using PyMuPDF.
        
        Args:
            pdf_path (Path): Path to PDF file
            
        Raises:
            PDFCorruptError: If PDF is corrupted
            PDFPasswordError: If PDF is password protected
            PDFValidationError: If PDF has other structural issues
        """
        doc = None
        try:
            # Try to open the PDF
            doc = fitz.open(str(pdf_path))
            
            # Check if password protected
            if doc.needs_pass:
                raise PDFPasswordError(
                    "PDF is password protected",
                    filename=pdf_path.name
                )
            
            # Check page count
            page_count = len(doc)
            if page_count == 0:
                raise PDFEmptyError(
                    "PDF has no pages",
                    filename=pdf_path.name
                )
            
            if page_count > self.config.MAX_PAGES:
                raise PDFValidationError(
                    f"PDF has too many pages: {page_count} > {self.config.MAX_PAGES}",
                    filename=pdf_path.name,
                    details={'page_count': page_count}
                )
            
            # Try to access first page to verify structure
            try:
                first_page = doc.load_page(0)
                # Try to extract some text to verify accessibility
                text = first_page.get_text()
                
                # Check if document has any extractable content
                total_chars = 0
                for page_num in range(min(3, page_count)):  # Check first 3 pages
                    page = doc.load_page(page_num)
                    page_text = page.get_text().strip()
                    total_chars += len(page_text)
                
                if total_chars == 0:
                    self.logger.warning(f"PDF appears to have no extractable text: {pdf_path.name}")
                
            except Exception as e:
                raise PDFCorruptError(
                    f"Cannot access PDF content: {e}",
                    filename=pdf_path.name
                ) from e
            
        except fitz.FileDataError as e:
            raise PDFCorruptError(
                f"PDF file is corrupted or invalid: {e}",
                filename=pdf_path.name
            ) from e
        
        except fitz.EmptyFileError as e:
            raise PDFEmptyError(
                "PDF file is empty or truncated",
                filename=pdf_path.name
            ) from e
        
        except (PDFValidationError, PDFCorruptError, PDFPasswordError, PDFEmptyError):
            # Re-raise our custom exceptions
            raise
        
        except Exception as e:
            raise PDFValidationError(
                f"Failed to validate PDF structure: {e}",
                filename=pdf_path.name
            ) from e
        
        finally:
            if doc:
                doc.close()
    
    def validate_output_directory(self, output_dir: Path) -> bool:
        """
        Validate output directory accessibility.
        
        Args:
            output_dir (Path): Output directory path
            
        Returns:
            bool: True if validation passes
            
        Raises:
            PDFValidationError: If directory validation fails
        """
        try:
            # Create directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if we can write to the directory
            test_file = output_dir / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()  # Delete test file
            except Exception as e:
                raise PDFValidationError(
                    f"Cannot write to output directory: {output_dir} - {e}"
                ) from e
            
            self.logger.info(f"Output directory validated: {output_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Output directory validation failed: {e}")
            raise PDFValidationError(f"Output directory validation failed: {e}") from e
    
    def validate_system_resources(self) -> bool:
        """
        Validate system resources availability.
        
        Returns:
            bool: True if resources are sufficient
            
        Raises:
            ResourceLimitError: If system resources are insufficient
        """
        try:
            import psutil
            
            # Check available memory
            memory = psutil.virtual_memory()
            available_mb = memory.available / (1024 * 1024)
            
            if available_mb < self.config.MEMORY_LIMIT_MB:
                raise ResourceLimitError(
                    f"Insufficient memory: {available_mb:.0f}MB available, "
                    f"{self.config.MEMORY_LIMIT_MB}MB required",
                    resource_type="memory",
                    limit=f"{self.config.MEMORY_LIMIT_MB}MB"
                )
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.config.CPU_USAGE_THRESHOLD:
                self.logger.warning(f"High CPU usage detected: {cpu_percent:.1f}%")
            
            self.logger.info(f"System resources validated - Memory: {available_mb:.0f}MB, CPU: {cpu_percent:.1f}%")
            return True
            
        except ImportError:
            # psutil not available, skip resource validation
            self.logger.warning("psutil not available, skipping resource validation")
            return True
        
        except Exception as e:
            self.logger.error(f"System resource validation failed: {e}")
            raise ResourceLimitError(f"System resource validation failed: {e}") from e
