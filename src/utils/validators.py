#!/usr/bin/env python3
"""
Input validation utilities for DocuDots PDF Structure Analysis Tool
Adobe India Hackathon - Challenge 1A
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import logging
import fitz  # PyMuPDF

from .exceptions import PDFValidationError, ResourceLimitError
from .config import config

logger = logging.getLogger(__name__)


class PDFValidator:
    """Comprehensive PDF file validator."""
    
    def __init__(self):
        self.config = config
    
    def validate_pdf_file(self, pdf_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive PDF file validation.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Raises:
            PDFValidationError: If validation fails with details
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
            max_size_bytes = self.config.processing_limits.max_file_size_mb * 1024 * 1024
            
            if file_size == 0:
                raise PDFValidationError(
                    "PDF file is empty",
                    filename=pdf_path.name,
                    details={'file_size': file_size}
                )
            
            if file_size > max_size_bytes:
                raise ResourceLimitError(
                    f"PDF file too large: {file_size / (1024*1024):.1f}MB > "
                    f"{self.config.processing_limits.max_file_size_mb}MB",
                    resource_type="file_size",
                    limit=f"{self.config.processing_limits.max_file_size_mb}MB"
                )
            
            # Validate PDF structure and content
            self._validate_pdf_structure(pdf_path)
            
            logger.info(f"PDF validation passed: {pdf_path.name} "
                       f"({file_size / (1024*1024):.1f}MB)")
            
            return True, None
            
        except (PDFValidationError, ResourceLimitError) as e:
            logger.error(f"PDF validation failed for {pdf_path.name}: {e}")
            return False, str(e)
        
        except Exception as e:
            error_msg = f"Unexpected validation error: {e}"
            logger.error(f"PDF validation failed for {pdf_path.name}: {error_msg}")
            return False, error_msg
    
    def _validate_pdf_structure(self, pdf_path: Path) -> None:
        """
        Validate internal PDF structure using PyMuPDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Raises:
            PDFValidationError: If PDF structure is invalid
        """
        doc = None
        try:
            # Try to open the PDF
            doc = fitz.open(pdf_path)
            
            # Check if PDF is encrypted (we can't process password-protected PDFs)
            if doc.needs_pass:
                raise PDFValidationError(
                    "PDF is password protected",
                    filename=pdf_path.name,
                    details={'encrypted': True}
                )
            
            # Check page count
            page_count = len(doc)
            if page_count == 0:
                raise PDFValidationError(
                    "PDF has no pages",
                    filename=pdf_path.name,
                    details={'page_count': page_count}
                )
            
            if page_count > self.config.processing_limits.max_pages:
                raise ResourceLimitError(
                    f"PDF has too many pages: {page_count} > "
                    f"{self.config.processing_limits.max_pages}",
                    resource_type="page_count",
                    limit=str(self.config.processing_limits.max_pages)
                )
            
            # Try to extract text from first page to ensure it's readable
            first_page = doc[0]
            text_dict = first_page.get_text("dict")
            
            # Check if we can extract any text blocks
            text_blocks_found = 0
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span.get("text", "").strip():
                                text_blocks_found += 1
                                break
                        if text_blocks_found > 0:
                            break
                if text_blocks_found > 0:
                    break
            
            if text_blocks_found == 0:
                logger.warning(f"No text found in first page of {pdf_path.name} "
                             "(might be image-only PDF)")
            
            # Check document metadata
            metadata = doc.metadata
            if metadata:
                logger.debug(f"PDF metadata for {pdf_path.name}: "
                           f"Title='{metadata.get('title', 'N/A')}', "
                           f"Author='{metadata.get('author', 'N/A')}'")
            
        except fitz.FileDataError as e:
            raise PDFValidationError(
                f"PDF file is corrupted or invalid: {e}",
                filename=pdf_path.name,
                details={'fitz_error': str(e)}
            )
        
        except fitz.FileNotFoundError as e:
            raise PDFValidationError(
                f"PDF file not found by PyMuPDF: {e}",
                filename=pdf_path.name,
                details={'fitz_error': str(e)}
            )
        
        finally:
            if doc:
                doc.close()
    
    def validate_input_directory(self, input_dir: Path) -> Dict[str, Any]:
        """
        Validate input directory and return summary.
        
        Args:
            input_dir: Path to input directory
            
        Returns:
            Dictionary with validation summary
        """
        if not input_dir.exists():
            raise PDFValidationError(f"Input directory does not exist: {input_dir}")
        
        if not input_dir.is_dir():
            raise PDFValidationError(f"Input path is not a directory: {input_dir}")
        
        # Find all PDF files
        pdf_files = list(input_dir.glob("*.pdf"))
        valid_files = []
        invalid_files = []
        
        for pdf_file in pdf_files:
            is_valid, error_msg = self.validate_pdf_file(pdf_file)
            if is_valid:
                valid_files.append(pdf_file)
            else:
                invalid_files.append({
                    'file': pdf_file,
                    'error': error_msg
                })
        
        summary = {
            'total_files': len(pdf_files),
            'valid_files': len(valid_files),
            'invalid_files': len(invalid_files),
            'valid_file_paths': valid_files,
            'invalid_file_details': invalid_files
        }
        
        logger.info(f"Input validation summary: {summary['valid_files']}/{summary['total_files']} files valid")
        
        return summary
    
    def validate_output_directory(self, output_dir: Path) -> bool:
        """
        Validate and prepare output directory.
        
        Args:
            output_dir: Path to output directory
            
        Returns:
            True if directory is ready for output
        """
        try:
            # Create directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if we can write to the directory
            test_file = output_dir / '.docudots_write_test'
            try:
                test_file.write_text('test')
                test_file.unlink()  # Delete test file
            except PermissionError:
                raise PDFValidationError(
                    f"No write permission for output directory: {output_dir}"
                )
            
            logger.info(f"Output directory validated: {output_dir}")
            return True
            
        except Exception as e:
            raise PDFValidationError(f"Output directory validation failed: {e}")


class InputValidator:
    """High-level input validation coordinator."""
    
    def __init__(self):
        self.pdf_validator = PDFValidator()
    
    def validate_processing_environment(self, input_dir: Path, output_dir: Path) -> Dict[str, Any]:
        """
        Validate the complete processing environment.
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            
        Returns:
            Validation summary dictionary
        """
        logger.info("Starting environment validation...")
        
        # Validate configuration
        config.validate()
        
        # Validate directories
        input_summary = self.pdf_validator.validate_input_directory(input_dir)
        self.pdf_validator.validate_output_directory(output_dir)
        
        # Check system resources
        resource_summary = self._check_system_resources()
        
        environment_summary = {
            'config_valid': True,
            'input_summary': input_summary,
            'output_directory_ready': True,
            'system_resources': resource_summary,
            'ready_for_processing': input_summary['valid_files'] > 0
        }
        
        logger.info(f"Environment validation complete. Ready: {environment_summary['ready_for_processing']}")
        
        return environment_summary
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check available system resources."""
        try:
            import psutil
            
            # Check available memory
            memory = psutil.virtual_memory()
            available_mb = memory.available / (1024 * 1024)
            
            # Check available disk space
            disk = psutil.disk_usage('/')
            available_gb = disk.free / (1024 * 1024 * 1024)
            
            return {
                'memory_available_mb': round(available_mb),
                'disk_available_gb': round(available_gb, 1),
                'memory_sufficient': available_mb > 500,  # Minimum 500MB
                'disk_sufficient': available_gb > 1.0     # Minimum 1GB
            }
            
        except ImportError:
            logger.warning("psutil not available for resource checking")
            return {
                'memory_available_mb': 'unknown',
                'disk_available_gb': 'unknown',
                'memory_sufficient': True,  # Assume sufficient
                'disk_sufficient': True
            }
        
        except Exception as e:
            logger.warning(f"Could not check system resources: {e}")
            return {
                'memory_available_mb': 'error',
                'disk_available_gb': 'error',
                'memory_sufficient': True,
                'disk_sufficient': True
            }
