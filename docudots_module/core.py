"""
Core PDF Analysis Module
========================

Main PDFAnalyzer class that provides the public API for PDF structure extraction.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import fitz  # PyMuPDF

from exceptions import (
    PDFAnalysisError,
    PDFValidationError,
    PDFCorruptError,
    PDFEmptyError,
    PDFLargeError,
    PDFPasswordError,
    AnalysisTimeoutError
)
from config import Config
from validators import InputValidator
from retry import with_retry, with_timeout
from multilingual import MultilingualProcessor


class PDFAnalyzer:
    """
    Main PDF analysis class for extracting document structure.
    
    This class provides a clean API for analyzing PDF documents and extracting
    their structural outline (title and headings) in a standardized JSON format.
    
    Example:
        analyzer = PDFAnalyzer()
        result = analyzer.analyze_pdf("document.pdf")
        print(result["title"])
        for heading in result["outline"]:
            print(f"{heading['level']}: {heading['text']} (Page {heading['page']})")
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the PDF analyzer.
        
        Args:
            config (Optional[Config]): Configuration object. If None, uses default config.
        """
        self.config = config or Config()
        self.validator = InputValidator(self.config)
        self.multilingual = MultilingualProcessor()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, self.config.LOG_LEVEL))
    
    def analyze_pdf(self, 
                   pdf_path: Union[str, Path], 
                   output_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Analyze a PDF file and extract its structural outline.
        
        Args:
            pdf_path (Union[str, Path]): Path to the PDF file to analyze
            output_path (Optional[Union[str, Path]]): Optional path to save JSON output
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - title (str): Document title
                - outline (List[Dict]): List of headings with level, text, and page
                
        Raises:
            PDFValidationError: If PDF file is invalid or cannot be processed
            PDFAnalysisError: If analysis fails
            AnalysisTimeoutError: If analysis times out
        """
        pdf_path = Path(pdf_path)
        
        self.logger.info(f"Starting analysis of PDF: {pdf_path.name}")
        start_time = time.time()
        
        try:
            # Validate input
            self.validator.validate_pdf_file(pdf_path)
            
            # Perform analysis with timeout and retry
            result = self._analyze_pdf_with_retry(pdf_path)
            
            # Save output if requested
            if output_path:
                output_path = Path(output_path)
                self._save_json_output(result, output_path)
                self.logger.info(f"Saved output to: {output_path}")
            
            elapsed = time.time() - start_time
            self.logger.info(f"Analysis complete - Title: '{result['title'][:20]}...' (took {elapsed:.2f}s)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis failed for {pdf_path.name}: {str(e)}")
            raise
    
    def analyze_multiple_pdfs(self, 
                            pdf_paths: List[Union[str, Path]], 
                            output_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Analyze multiple PDF files.
        
        Args:
            pdf_paths (List[Union[str, Path]]): List of PDF file paths
            output_dir (Optional[Union[str, Path]]): Directory to save JSON outputs
            
        Returns:
            Dict[str, Any]: Summary of processing results
        """
        results = {
            "total_files": len(pdf_paths),
            "processed": 0,
            "errors": 0,
            "success_rate": 0.0,
            "results": {},
            "error_details": []
        }
        
        start_time = time.time()
        
        for pdf_path in pdf_paths:
            pdf_path = Path(pdf_path)
            try:
                # Analyze PDF
                result = self.analyze_pdf(pdf_path)
                
                # Save output if directory specified
                if output_dir:
                    output_path = Path(output_dir) / f"{pdf_path.stem}.json"
                    self._save_json_output(result, output_path)
                
                results["results"][pdf_path.name] = result
                results["processed"] += 1
                
            except Exception as e:
                results["errors"] += 1
                error_info = {
                    "file": pdf_path.name,
                    "error": str(e),
                    "type": type(e).__name__
                }
                results["error_details"].append(error_info)
                self.logger.error(f"Failed to process {pdf_path.name}: {str(e)}")
        
        # Calculate final stats
        results["success_rate"] = (results["processed"] / results["total_files"]) * 100
        results["processing_time"] = time.time() - start_time
        
        return results
    
    @with_timeout(300)  # 5 minute timeout
    @with_retry(max_attempts=3, delay=1.0, backoff=2.0)
    def _analyze_pdf_with_retry(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Internal method to analyze PDF with retry logic.
        
        Args:
            pdf_path (Path): Path to PDF file
            
        Returns:
            Dict[str, Any]: Analysis result
        """
        return self._analyze_pdf_structure(pdf_path)
    
    def _analyze_pdf_structure(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Core PDF analysis logic.
        
        Args:
            pdf_path (Path): Path to PDF file
            
        Returns:
            Dict[str, Any]: Dictionary with title and outline
        """
        try:
            # Open PDF
            doc = fitz.open(str(pdf_path))
            self.logger.info(f"Successfully opened PDF with {len(doc)} pages")
            
            # Extract text blocks
            self.logger.info("Extracting text blocks from PDF...")
            all_blocks = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                if span["text"].strip():
                                    all_blocks.append({
                                        "text": span["text"].strip(),
                                        "page": page_num,
                                        "font_size": span["size"],
                                        "font_flags": span["flags"],
                                        "bbox": span["bbox"]
                                    })
            
            doc.close()
            
            self.logger.info(f"Extracted {len(all_blocks)} text blocks from document")
            
            # Apply multilingual processing
            self.logger.info("Applying multi-lingual text processing...")
            all_blocks = self.multilingual.process_text_blocks(all_blocks)
            
            self.logger.info(f"Total text blocks extracted: {len(all_blocks)}")
            
            # Identify title and headings
            self.logger.info("Performing heading identification and classification...")
            title, headings = self._identify_headings(all_blocks)
            
            # Create final result
            result = {
                "title": title,
                "outline": headings
            }
            
            self.logger.info(f"Final headings count: {len(headings)}")
            
            return result
            
        except Exception as e:
            raise PDFAnalysisError(f"Failed to analyze PDF structure: {str(e)}") from e
    
    def _identify_headings(self, blocks: List[Dict]) -> tuple[str, List[Dict]]:
        """
        Identify document title and headings from text blocks.
        
        Args:
            blocks (List[Dict]): List of text blocks
            
        Returns:
            tuple: (title, headings_list)
        """
        if not blocks:
            return "Untitled Document", []
        
        self.logger.info("Starting comprehensive heading analysis...")
        
        # Analyze font characteristics
        font_sizes = [block["font_size"] for block in blocks]
        avg_font_size = sum(font_sizes) / len(font_sizes)
        
        # Identify body text size (most common size)
        size_counts = {}
        for size in font_sizes:
            size_counts[size] = size_counts.get(size, 0) + 1
        body_text_size = max(size_counts, key=size_counts.get)
        
        min_size = min(font_sizes)
        max_size = max(font_sizes)
        
        self.logger.info(f"Font analysis - Body text size: {body_text_size}, Average: {avg_font_size:.2f}, Range: {min_size}-{max_size}")
        
        # Find title (largest text on first page, usually)
        first_page_blocks = [b for b in blocks if b["page"] == 0]
        if first_page_blocks:
            title_block = max(first_page_blocks, key=lambda x: x["font_size"])
            title = title_block["text"]
        else:
            title = "Untitled Document"
        
        # Identify heading candidates
        heading_candidates = []
        for block in blocks:
            # Skip if it's the title
            if block["text"] == title:
                continue
                
            # Multi-factor heading detection
            is_heading = False
            heading_level = "H3"  # default
            
            # Factor 1: Font size relative to body text
            size_ratio = block["font_size"] / body_text_size
            
            # Factor 2: Font weight (bold)
            is_bold = bool(block["font_flags"] & 2**4)  # Bold flag
            
            # Factor 3: Text characteristics
            text = block["text"].strip()
            is_short = len(text.split()) <= 8
            is_capitalized = text.isupper() or text.istitle()
            
            # Heading classification logic
            if size_ratio >= 1.5 or (size_ratio >= 1.2 and is_bold):
                is_heading = True
                heading_level = "H1"
            elif size_ratio >= 1.15 or (size_ratio >= 1.05 and is_bold) or (is_capitalized and is_short):
                is_heading = True
                heading_level = "H2"
            elif is_bold and is_short and size_ratio >= 0.95:
                is_heading = True
                heading_level = "H3"
            
            if is_heading:
                heading_candidates.append({
                    "level": heading_level,
                    "text": text,
                    "page": block["page"],
                    "font_size": block["font_size"],
                    "size_ratio": size_ratio,
                    "is_bold": is_bold
                })
        
        self.logger.info(f"Identified {len(heading_candidates)} heading candidates")
        
        # Sort by page and position
        heading_candidates.sort(key=lambda x: (x["page"], -x["font_size"]))
        
        # Limit headings and create final list
        max_headings = self.config.MAX_HEADINGS_PER_DOCUMENT
        final_headings = heading_candidates[:max_headings]
        
        # Count by level for logging
        level_counts = {}
        for h in final_headings:
            level_counts[h["level"]] = level_counts.get(h["level"], 0) + 1
        
        self.logger.info(f"Heading classification: {level_counts}")
        
        # Create clean output format
        clean_headings = []
        for heading in final_headings:
            clean_headings.append({
                "level": heading["level"],
                "text": heading["text"],
                "page": heading["page"]
            })
        
        self.logger.info(f"Final results - Title: '{title[:20]}...', Headings: {len(clean_headings)}")
        
        return title, clean_headings
    
    def _save_json_output(self, result: Dict[str, Any], output_path: Path) -> None:
        """
        Save analysis result to JSON file.
        
        Args:
            result (Dict[str, Any]): Analysis result
            output_path (Path): Output file path
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise PDFAnalysisError(f"Failed to save JSON output: {str(e)}") from e
