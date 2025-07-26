#!/usr/bin/env python3
"""
Adobe India Hackathon - Challenge 1A
PDF Structure Analysis Tool

This script analyzes PDF files and extracts their structural outline
(Title, H1, H2, H3 headings) into a specific JSON format.

Author: Created for Adobe India Hackathon
Date: July 2025
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter
import fitz  # PyMuPDF

# Configure logging for better debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PDFStructureAnalyzer:
    """
    Analyzes PDF files and extracts structural outline information.
    """
    
    def __init__(self, input_dir: str = "/app/input", output_dir: str = "/app/output"):
        """
        Initialize the PDF analyzer.
        
        Args:
            input_dir: Directory containing input PDF files
            output_dir: Directory for output JSON files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # Ensure directories exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized PDF analyzer - Input: {self.input_dir}, Output: {self.output_dir}")
    
    def get_pdf_files(self) -> List[Path]:
        """
        Get all PDF files from the input directory.
        
        Returns:
            List of Path objects for PDF files
        """
        pdf_files = list(self.input_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {self.input_dir}")
        return pdf_files
    
    def analyze_pdf_structure(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Analyze a single PDF file and extract its structural outline.
        This is the main method that orchestrates the complete analysis workflow.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing the complete analysis results
        """
        logger.info(f"Starting analysis of PDF: {pdf_path.name}")
        
        try:
            # Step 1: Open the PDF document
            doc = fitz.open(pdf_path)
            logger.info(f"Successfully opened PDF with {len(doc)} pages")
            
            # Step 2: Initialize the result structure
            result = {
                "document_info": {
                    "filename": pdf_path.name,
                    "total_pages": len(doc),
                    "title": "",  # Will be populated later
                    "processing_timestamp": None
                },
                "structural_outline": {
                    "title": "",
                    "headings": []
                }
            }
            
            # Step 3: Extract all text blocks with their properties
            logger.info("Extracting text blocks from PDF...")
            text_blocks = self._extract_text_blocks(doc)
            
            # Print total number of text blocks found (confirmation output)
            print(f"✅ Found {len(text_blocks)} text blocks in {pdf_path.name}")
            logger.info(f"Total text blocks extracted: {len(text_blocks)}")
            
            # Step 4: Perform comprehensive heading identification and classification
            logger.info("Performing heading identification and classification...")
            structural_outline = self._extract_headings_from_blocks(text_blocks)
            result["structural_outline"] = structural_outline
            
            # Step 5: Extract the final title and classified headings (as requested)
            final_title = structural_outline["title"]
            final_headings = structural_outline["headings"]
            
            # Update document info with extracted title
            result["document_info"]["title"] = final_title
            
            # Step 6: Log and display final results
            logger.info(f"Analysis complete - Title: '{final_title}'")
            logger.info(f"Final headings count: {len(final_headings)}")
            
            # Print comprehensive summary to console
            print(f"📋 Title: {final_title}")
            print(f"📑 Found {len(final_headings)} classified headings:")
            
            # Display heading breakdown by level
            level_counts = {"H1": 0, "H2": 0, "H3": 0}
            for heading in final_headings:
                level_counts[heading["level"]] += 1
            
            print(f"   Level distribution: H1({level_counts['H1']}) H2({level_counts['H2']}) H3({level_counts['H3']})")
            
            # Show sample of headings
            for i, heading in enumerate(final_headings[:8], 1):  # Show first 8
                text_preview = heading['text'][:60] + "..." if len(heading['text']) > 60 else heading['text']
                print(f"   {i}. {heading['level']}: {text_preview} (Page {heading['page']})")
            
            if len(final_headings) > 8:
                print(f"   ... and {len(final_headings) - 8} more headings")
            
            # Step 7: Store text blocks summary for debugging
            result["text_blocks_summary"] = {
                "total_blocks": len(text_blocks),
                "sample_blocks": text_blocks[:5]  # Store first 5 blocks as sample
            }
            
            # Step 8: Close the document
            doc.close()
            
            logger.info(f"Successfully completed analysis of {pdf_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {pdf_path.name}: {str(e)}")
            # Return error result but still attempt to close document if it was opened
            try:
                if 'doc' in locals():
                    doc.close()
            except:
                pass
            return self._create_error_result(pdf_path.name, str(e))
    
    def _extract_document_title(self, doc: fitz.Document) -> str:
        """
        Extract the document title from PDF metadata or first page.
        
        Args:
            doc: PyMuPDF document object
            
        Returns:
            Document title or filename if not found
        """
        # Try to get title from metadata first
        metadata = doc.metadata
        if metadata and metadata.get('title') and metadata['title'].strip():
            return metadata['title'].strip()
        
        # If no metadata title, try to extract from first page content
        try:
            if len(doc) > 0:
                first_page = doc[0]
                # Get text with formatting to find the largest text (likely title)
                text_dict = first_page.get_text("dict")
                
                largest_text = ""
                largest_size = 0
                
                for block in text_dict["blocks"]:
                    if "lines" not in block:
                        continue
                    
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            size = span.get("size", 0)
                            
                            # Look for the largest text on first page that's not too long
                            if size > largest_size and 5 < len(text) < 100:
                                largest_text = text
                                largest_size = size
                
                if largest_text:
                    return largest_text
                    
        except Exception as e:
            logger.warning(f"Could not extract title from first page: {str(e)}")
        
        return "Untitled Document"
    
    def _extract_text_blocks(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """
        Extract all text blocks from the PDF with their properties.
        
        Args:
            doc: PyMuPDF document object
            
        Returns:
            List of dictionaries containing text block properties
        """
        text_blocks = []
        
        try:
            # Iterate through each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get text blocks with detailed formatting information
                # Using get_text("dict") to get detailed formatting data
                text_dict = page.get_text("dict")
                
                # Process each block in the page
                for block in text_dict["blocks"]:
                    # Skip image blocks, only process text blocks
                    if "lines" not in block:
                        continue
                    
                    # Process each line in the block
                    for line in block["lines"]:
                        # Process each span (text with consistent formatting) in the line
                        for span in line["spans"]:
                            # Extract text content
                            text_content = span["text"].strip()
                            
                            # Skip empty text spans
                            if not text_content:
                                continue
                            
                            # Extract font properties
                            font_name = span.get("font", "")
                            font_size = span.get("size", 0)
                            font_flags = span.get("flags", 0)
                            
                            # Determine if text is bold
                            # Font flags bit 4 (16) indicates bold
                            is_bold = bool(font_flags & 16)
                            
                            # Get text position (bbox: [x0, y0, x1, y1])
                            bbox = span.get("bbox", [0, 0, 0, 0])
                            
                            # Create text block dictionary
                            text_block = {
                                "text": text_content,
                                "font_size": round(font_size, 2),
                                "font_name": font_name,
                                "is_bold": is_bold,
                                "page_number": page_num + 1,  # 1-indexed page numbers
                                "position": {
                                    "x": round(bbox[0], 2),
                                    "y": round(bbox[1], 2),
                                    "width": round(bbox[2] - bbox[0], 2),
                                    "height": round(bbox[3] - bbox[1], 2)
                                },
                                "bbox": [round(coord, 2) for coord in bbox]
                            }
                            
                            text_blocks.append(text_block)
            
            logger.info(f"Extracted {len(text_blocks)} text blocks from document")
            return text_blocks
            
        except Exception as e:
            logger.error(f"Error extracting text blocks: {str(e)}")
            return []

    def _analyze_font_styles(self, text_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze font styles to determine body text characteristics.
        
        Args:
            text_blocks: List of text block dictionaries
            
        Returns:
            Dictionary containing font analysis results
        """
        if not text_blocks:
            return {
                "body_font_size": 12.0,
                "body_font_name": "default",
                "common_font_sizes": [],
                "font_size_stats": {}
            }
        
        # Collect font statistics
        font_sizes = [block["font_size"] for block in text_blocks]
        font_names = [block["font_name"] for block in text_blocks]
        
        # Calculate font size frequency
        from collections import Counter
        font_size_counts = Counter(font_sizes)
        font_name_counts = Counter(font_names)
        
        # Find most common font size (likely body text)
        most_common_size = font_size_counts.most_common(1)[0][0] if font_size_counts else 12.0
        most_common_font = font_name_counts.most_common(1)[0][0] if font_name_counts else "default"
        
        # Calculate statistics
        avg_font_size = sum(font_sizes) / len(font_sizes)
        median_font_size = sorted(font_sizes)[len(font_sizes) // 2]
        
        # Get common font sizes (top 5)
        common_sizes = [size for size, count in font_size_counts.most_common(5)]
        
        font_analysis = {
            "body_font_size": most_common_size,
            "body_font_name": most_common_font,
            "common_font_sizes": common_sizes,
            "font_size_stats": {
                "average": round(avg_font_size, 2),
                "median": round(median_font_size, 2),
                "min": min(font_sizes),
                "max": max(font_sizes),
                "most_common": most_common_size
            },
            "total_unique_sizes": len(font_size_counts),
            "size_distribution": dict(font_size_counts.most_common(10))
        }
        
        logger.info(f"Font analysis - Body text size: {most_common_size}, "
                   f"Average: {avg_font_size:.2f}, Range: {min(font_sizes)}-{max(font_sizes)}")
        
        return font_analysis

    def _filter_heading_candidates(self, text_blocks: List[Dict[str, Any]], 
                                 font_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter text blocks to identify potential headings.
        
        Args:
            text_blocks: List of all text blocks
            font_analysis: Results from font analysis
            
        Returns:
            List of heading candidate blocks
        """
        body_font_size = font_analysis["body_font_size"]
        avg_font_size = font_analysis["font_size_stats"]["average"]
        
        heading_candidates = []
        
        for block in text_blocks:
            text = block["text"].strip()
            font_size = block["font_size"]
            is_bold = block["is_bold"]
            
            # Skip very short or very long text
            if len(text) < 3 or len(text) > 200:
                continue
            
            # Skip text that looks like body content (common patterns)
            if any(pattern in text.lower() for pattern in [
                "figure", "table", "page", "www.", "http", "@", 
                "copyright", "©", "et al.", "ibid"
            ]):
                continue
            
            # Multiple criteria for heading identification
            size_threshold = max(body_font_size * 1.1, avg_font_size * 1.05)
            
            is_potential_heading = (
                # Larger than body text
                font_size > size_threshold or
                # Bold text with reasonable size
                (is_bold and font_size >= body_font_size * 0.9) or
                # Significantly larger than average
                font_size > avg_font_size * 1.3
            )
            
            # Additional filters for better heading detection
            if is_potential_heading:
                # Check text characteristics
                word_count = len(text.split())
                has_sentence_ending = text.endswith(('.', '!', '?'))
                is_all_caps = text.isupper() and len(text) > 3
                starts_with_number = text.split('.')[0].replace(' ', '').isdigit()
                
                # Heading likelihood score
                heading_score = 0
                
                # Font size factor (0-40 points)
                size_ratio = font_size / body_font_size
                heading_score += min(40, (size_ratio - 1) * 20)
                
                # Bold factor (0-20 points)
                if is_bold:
                    heading_score += 20
                
                # Length factor (prefer shorter text, 0-20 points)
                if word_count <= 8:
                    heading_score += 20 - (word_count * 2)
                
                # Position factor (early in page gets bonus, 0-10 points)
                if block["position"]["y"] < 200:  # Top portion of page
                    heading_score += 10
                
                # Text pattern bonuses/penalties
                if not has_sentence_ending:
                    heading_score += 5  # Headings rarely end with periods
                
                if is_all_caps and len(text) < 50:
                    heading_score += 10  # ALL CAPS headings
                
                if starts_with_number:
                    heading_score += 8  # Numbered headings like "1. Introduction"
                
                # Only include if score is high enough
                if heading_score >= 25:
                    block_copy = block.copy()
                    block_copy["heading_score"] = round(heading_score, 2)
                    heading_candidates.append(block_copy)
        
        # Sort by document order (page number, then Y position)
        heading_candidates.sort(key=lambda x: (x["page_number"], x["position"]["y"]))
        
        logger.info(f"Identified {len(heading_candidates)} heading candidates")
        return heading_candidates

    def _classify_heading_levels(self, heading_candidates: List[Dict[str, Any]], 
                               font_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Classify heading candidates into H1, H2, H3 levels using multiple factors.
        
        This method uses a sophisticated scoring system that considers:
        - Text patterns and content analysis
        - Document structure and position
        - Font characteristics (size, bold, formatting)
        - Context and semantic meaning
        - Hierarchy indicators (numbering, bullets, etc.)
        
        Args:
            heading_candidates: List of heading candidate blocks
            font_analysis: Results from font analysis
            
        Returns:
            List of classified headings with levels assigned
        """
        if not heading_candidates:
            return []
        
        classified_headings = []
        body_font_size = font_analysis["body_font_size"]
        
        for block in heading_candidates:
            text = block["text"].strip()
            font_size = block["font_size"]
            is_bold = block["is_bold"]
            position_y = block["position"]["y"]
            heading_score = block["heading_score"]
            
            # Initialize level scoring system
            h1_score = 0
            h2_score = 0
            h3_score = 0
            
            # === TEXT PATTERN ANALYSIS ===
            text_lower = text.lower()
            text_length = len(text)
            word_count = len(text.split())
            
            # H1 indicators - Major document sections
            h1_patterns = [
                'abstract', 'introduction', 'conclusion', 'summary', 'overview',
                'background', 'methodology', 'results', 'discussion', 'references',
                'about', 'experience', 'education', 'skills', 'projects', 'contact',
                'objective', 'profile', 'qualifications', 'achievements', 'awards'
            ]
            
            # H2 indicators - Subsections and categories
            h2_patterns = [
                'work experience', 'employment history', 'professional experience',
                'technical skills', 'core competencies', 'key skills', 'expertise',
                'certifications', 'publications', 'research', 'languages',
                'extracurricular', 'activities', 'volunteering', 'interests',
                'tools', 'technologies', 'software', 'platforms'
            ]
            
            # H3 indicators - Specific items and details
            h3_patterns = [
                'programming languages', 'frameworks', 'databases', 'operating systems',
                'web technologies', 'mobile development', 'cloud platforms',
                'project management', 'soft skills', 'leadership', 'communication'
            ]
            
            # Pattern matching scores
            for pattern in h1_patterns:
                if pattern in text_lower:
                    h1_score += 25
            
            for pattern in h2_patterns:
                if pattern in text_lower:
                    h2_score += 20
                    
            for pattern in h3_patterns:
                if pattern in text_lower:
                    h3_score += 15
            
            # === STRUCTURAL ANALYSIS ===
            
            # Position-based scoring (earlier in document = higher level)
            if position_y < 150:  # Very top of page
                h1_score += 20
            elif position_y < 300:  # Upper portion
                h1_score += 10
                h2_score += 15
            elif position_y < 500:  # Middle portion
                h2_score += 10
                h3_score += 5
            else:  # Lower portion
                h3_score += 10
            
            # Text length analysis
            if word_count == 1:  # Single word headings
                h1_score += 15
                h2_score += 10
            elif word_count <= 3:  # Short phrases
                h1_score += 10
                h2_score += 15
                h3_score += 5
            elif word_count <= 6:  # Medium phrases
                h2_score += 10
                h3_score += 10
            else:  # Long phrases (less likely to be major headings)
                h3_score += 5
            
            # === TYPOGRAPHY ANALYSIS ===
            
            # Font size analysis (still considered but not primary)
            size_ratio = font_size / body_font_size
            
            if size_ratio >= 2.0:
                h1_score += 20
            elif size_ratio >= 1.6:
                h1_score += 15
                h2_score += 10
            elif size_ratio >= 1.3:
                h1_score += 5
                h2_score += 15
                h3_score += 5
            elif size_ratio >= 1.1:
                h2_score += 10
                h3_score += 10
            else:
                h3_score += 15
            
            # Bold formatting
            if is_bold:
                h1_score += 15
                h2_score += 15
                h3_score += 10
            
            # === CONTENT ANALYSIS ===
            
            # All caps text (often major headings)
            if text.isupper() and text_length > 2:
                h1_score += 20
                h2_score += 10
            
            # Numbered/lettered headings
            import re
            if re.match(r'^[0-9]+\.?\s+', text):  # "1. Introduction" or "1 Background"
                h1_score += 15
                h2_score += 20
            elif re.match(r'^[0-9]+\.[0-9]+\.?\s+', text):  # "1.1 Overview"
                h2_score += 25
                h3_score += 10
            elif re.match(r'^[a-zA-Z][\)\.]\s+', text):  # "a) Details" or "A. Section"
                h2_score += 15
                h3_score += 20
            elif re.match(r'^[ivxlc]+\.?\s+', text, re.I):  # Roman numerals "i. item"
                h2_score += 10
                h3_score += 15
            
            # Special characters and formatting
            if ':' in text and not text.endswith(':'):  # "Skills: Programming"
                h2_score += 10
                h3_score += 15
            elif text.endswith(':'):  # "Skills:"
                h1_score += 10
                h2_score += 20
            
            # Professional titles and institutions
            title_indicators = ['university', 'college', 'institute', 'company', 'corporation', 
                              'ltd', 'inc', 'llc', 'technologies', 'systems', 'solutions']
            if any(indicator in text_lower for indicator in title_indicators):
                h2_score += 15
                h3_score += 10
            
            # === FINAL CLASSIFICATION ===
            
            # Determine the level based on highest score
            max_score = max(h1_score, h2_score, h3_score)
            
            if max_score == h1_score and h1_score >= 25:
                level = "H1"
            elif max_score == h2_score and h2_score >= 20:
                level = "H2"
            elif max_score == h3_score and h3_score >= 15:
                level = "H3"
            else:
                # Fallback logic if scores are too low or tied
                if size_ratio >= 1.5 or (is_bold and word_count <= 2):
                    level = "H1"
                elif size_ratio >= 1.2 or (is_bold and word_count <= 4):
                    level = "H2"
                else:
                    level = "H3"
            
            # Create classified heading with detailed scoring info
            classified_heading = {
                "level": level,
                "text": text,
                "page": block["page_number"],
                "position": block["position"],
                "font_size": font_size,
                "is_bold": is_bold,
                "heading_score": heading_score,
                "size_ratio": round(size_ratio, 2),
                "classification_scores": {
                    "h1": h1_score,
                    "h2": h2_score,
                    "h3": h3_score,
                    "final": max_score
                }
            }
            
            classified_headings.append(classified_heading)
        
        # Sort by page number, then by position on page
        classified_headings.sort(key=lambda x: (x["page"], x["position"]["y"]))
        
        # Post-processing: Ensure logical hierarchy
        classified_headings = self._refine_heading_hierarchy(classified_headings)
        
        # Log level distribution
        level_counts = {}
        for heading in classified_headings:
            level = heading["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
        
        logger.info(f"Heading classification: {level_counts}")
        
        return classified_headings
    
    def _refine_heading_hierarchy(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Refine heading hierarchy to ensure logical structure.
        
        Args:
            headings: List of classified headings
            
        Returns:
            List of headings with refined hierarchy
        """
        if len(headings) <= 1:
            return headings
        
        refined_headings = []
        
        for i, heading in enumerate(headings):
            current_level = heading["level"]
            
            # Look at context around this heading
            prev_heading = headings[i-1] if i > 0 else None
            next_heading = headings[i+1] if i < len(headings)-1 else None
            
            # Adjust level based on context
            if prev_heading and next_heading:
                prev_level = prev_heading["level"]
                next_level = next_heading["level"]
                
                # If surrounded by H3s and classified as H1, likely should be H2
                if current_level == "H1" and prev_level == "H3" and next_level == "H3":
                    if heading["classification_scores"]["h2"] >= 15:
                        heading["level"] = "H2"
                
                # If surrounded by H2s and classified as H3, might be H2
                elif current_level == "H3" and prev_level == "H2" and next_level == "H2":
                    if heading["classification_scores"]["h2"] >= heading["classification_scores"]["h3"]:
                        heading["level"] = "H2"
            
            refined_headings.append(heading)
        
        return refined_headings

    def _identify_document_title(self, text_blocks: List[Dict[str, Any]]) -> str:
        """
        Identify the main document title from text blocks.
        
        Args:
            text_blocks: List of all text blocks
            
        Returns:
            Document title string
        """
        if not text_blocks:
            return "Untitled Document"
        
        # Filter blocks from first two pages only
        title_candidates = [
            block for block in text_blocks 
            if block["page_number"] <= 2
        ]
        
        if not title_candidates:
            return "Untitled Document"
        
        # Find candidates with largest font size
        max_font_size = max(block["font_size"] for block in title_candidates)
        largest_text_blocks = [
            block for block in title_candidates 
            if block["font_size"] >= max_font_size * 0.95  # Within 95% of max size
        ]
        
        # Score title candidates
        best_title = ""
        best_score = 0
        
        for block in largest_text_blocks:
            text = block["text"].strip()
            font_size = block["font_size"]
            is_bold = block["is_bold"]
            page_num = block["page_number"]
            y_position = block["position"]["y"]
            
            # Skip very short or very long text
            if len(text) < 5 or len(text) > 150:
                continue
            
            # Skip obvious non-titles
            if any(pattern in text.lower() for pattern in [
                "page", "figure", "table", "abstract", "introduction",
                "www.", "http", "@", "copyright", "©"
            ]):
                continue
            
            # Calculate title score
            title_score = 0
            
            # Font size (0-40 points)
            title_score += min(40, font_size * 2)
            
            # Bold text bonus (0-20 points)
            if is_bold:
                title_score += 20
            
            # Page position bonus (0-20 points)
            if page_num == 1:
                title_score += 20
            elif page_num == 2:
                title_score += 10
            
            # Y-position bonus (higher on page = better, 0-15 points)
            if y_position < 200:  # Top of page
                title_score += 15
            elif y_position < 400:  # Upper portion
                title_score += 10
            
            # Text characteristics (0-15 points)
            word_count = len(text.split())
            if 2 <= word_count <= 12:  # Reasonable title length
                title_score += 15 - abs(word_count - 6)
            
            # Check if it's a reasonable title
            if not text.endswith('.') and not text.startswith(('Fig', 'Table')):
                title_score += 10
            
            if title_score > best_score:
                best_score = title_score
                best_title = text
        
        # Fallback to first large text if no good title found
        if not best_title and largest_text_blocks:
            best_title = largest_text_blocks[0]["text"].strip()
        
        return best_title if best_title else "Untitled Document"

    def _extract_headings_from_blocks(self, text_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze text blocks to identify and classify headings and title.
        
        Args:
            text_blocks: List of text block dictionaries
            
        Returns:
            Dictionary containing structural outline with classified headings
        """
        if not text_blocks:
            return {
                "title": "",
                "headings": []
            }
        
        logger.info("Starting comprehensive heading analysis...")
        
        # Step 1: Analyze font styles to understand document structure
        font_analysis = self._analyze_font_styles(text_blocks)
        
        # Step 2: Filter for heading candidates
        heading_candidates = self._filter_heading_candidates(text_blocks, font_analysis)
        
        # Step 3: Classify heading levels
        classified_headings = self._classify_heading_levels(heading_candidates, font_analysis)
        
        # Step 4: Identify document title
        document_title = self._identify_document_title(text_blocks)
        
        # Limit headings to reasonable number and clean up
        final_headings = []
        for heading in classified_headings[:20]:  # Limit to top 20 headings
            final_headings.append({
                "level": heading["level"],
                "text": heading["text"],
                "page": heading["page"],
                "position": {
                    "x": heading["position"]["x"],
                    "y": heading["position"]["y"]
                }
            })
        
        logger.info(f"Final results - Title: '{document_title[:50]}...', "
                   f"Headings: {len(final_headings)}")
        
        return {
            "title": document_title,
            "headings": final_headings,
            "analysis_metadata": {
                "font_analysis": font_analysis,
                "total_candidates": len(heading_candidates),
                "final_heading_count": len(final_headings)
            }
        }
    
    def _create_error_result(self, filename: str, error_message: str) -> Dict[str, Any]:
        """
        Create an error result structure for failed PDF processing.
        
        Args:
            filename: Name of the PDF file that failed
            error_message: Error description
            
        Returns:
            Error result dictionary with proper structure
        """
        return {
            "document_info": {
                "filename": filename,
                "total_pages": 0,
                "title": "Error - Could not process document",
                "processing_timestamp": None,
                "error": error_message
            },
            "structural_outline": {
                "title": "Error - Could not process document",
                "headings": [],
                "error": error_message
            },
            "text_blocks_summary": {
                "total_blocks": 0,
                "sample_blocks": []
            }
        }
    
    def _create_final_json_output(self, title: str, headings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create the final JSON output in the exact required format.
        
        Args:
            title: Document title string
            headings: List of classified heading dictionaries
            
        Returns:
            Dictionary in the required JSON format with 'title' and 'outline' keys
        """
        # Create the exact JSON structure as required
        final_json = {
            "title": title,
            "outline": []
        }
        
        # Process each heading to match required format
        for heading in headings:
            heading_object = {
                "level": heading["level"],      # H1, H2, or H3
                "text": heading["text"],        # Heading text content
                "page": heading["page"]         # Page number (1-indexed)
            }
            final_json["outline"].append(heading_object)
        
        logger.info(f"Created final JSON with {len(final_json['outline'])} headings")
        return final_json

    def save_result(self, result: Dict[str, Any], pdf_filename: str) -> bool:
        """
        Save the analysis result to a JSON file in the required format.
        
        Args:
            result: Analysis result dictionary
            pdf_filename: Original PDF filename
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create output filename by replacing .pdf with .json
            output_filename = pdf_filename.replace('.pdf', '.json')
            output_path = self.output_dir / output_filename
            
            # Extract title and headings from the analysis result
            structural_outline = result.get("structural_outline", {})
            title = structural_outline.get("title", "Untitled Document")
            headings = structural_outline.get("headings", [])
            
            # Create the final JSON output in the required format
            final_json_output = self._create_final_json_output(title, headings)
            
            # Write JSON file with clean formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_json_output, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved final JSON output to {output_path}")
            logger.info(f"Output contains: Title + {len(final_json_output['outline'])} headings")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving result for {pdf_filename}: {str(e)}")
            return False
    
    def process_all_pdfs(self) -> Dict[str, Any]:
        """
        Process all PDF files in the input directory with complete workflow.
        
        Returns:
            Summary of processing results
        """
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            logger.warning("No PDF files found in input directory")
            print("⚠️  No PDF files found in input directory")
            print(f"   Please add PDF files to: {self.input_dir}")
            return {"total_files": 0, "processed": 0, "errors": 0}
        
        print(f"\n🚀 Starting PDF Structure Analysis")
        print(f"📁 Input directory: {self.input_dir}")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📄 Found {len(pdf_files)} PDF file(s) to process")
        print("-" * 60)
        
        processed_count = 0
        error_count = 0
        
        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
                print("=" * 50)
                
                # Perform complete analysis workflow
                result = self.analyze_pdf_structure(pdf_file)
                
                # Save the final JSON output in required format
                if self.save_result(result, pdf_file.name):
                    processed_count += 1
                    print(f"✅ Successfully processed {pdf_file.name}")
                    
                    # Show final output file info
                    output_filename = pdf_file.name.replace('.pdf', '.json')
                    print(f"📄 Output saved as: {output_filename}")
                else:
                    error_count += 1
                    print(f"❌ Failed to save results for {pdf_file.name}")
                    
            except Exception as e:
                logger.error(f"Unexpected error processing {pdf_file.name}: {str(e)}")
                print(f"❌ Unexpected error processing {pdf_file.name}: {str(e)}")
                error_count += 1
        
        # Final summary
        print("\n" + "=" * 60)
        print("📊 PROCESSING SUMMARY")
        print("-" * 30)
        
        summary = {
            "total_files": len(pdf_files),
            "processed": processed_count,
            "errors": error_count,
            "success_rate": round((processed_count / len(pdf_files)) * 100, 1) if pdf_files else 0
        }
        
        print(f"Total files: {summary['total_files']}")
        print(f"Successfully processed: {summary['processed']}")
        print(f"Errors: {summary['errors']}")
        print(f"Success rate: {summary['success_rate']}%")
        
        if processed_count > 0:
            print(f"\n✅ Results available in: {self.output_dir}")
        
        logger.info(f"Processing complete: {summary}")
        return summary


def main():
    """
    Main execution function - Complete PDF Structure Analysis Workflow.
    
    This function orchestrates the entire process:
    1. Initializes the PDF analyzer
    2. Discovers PDF files in the input directory
    3. For each PDF:
       - Extracts text blocks with properties
       - Analyzes font styles to identify body text
       - Filters and scores heading candidates
       - Classifies headings into H1, H2, H3 levels
       - Identifies document title
       - Creates final JSON output in required format
    4. Saves results and provides summary
    """
    print("🔍 PDF Structure Analysis Tool")
    print("Adobe India Hackathon - Challenge 1A")
    print("=" * 50)
    
    logger.info("Starting PDF Structure Analysis Tool")
    logger.info("Adobe India Hackathon - Challenge 1A")
    
    try:
        # Initialize the analyzer with default paths
        analyzer = PDFStructureAnalyzer()
        
        print(f"📂 Monitoring directories:")
        print(f"   Input:  {analyzer.input_dir}")
        print(f"   Output: {analyzer.output_dir}")
        
        # Process all PDFs with complete workflow
        summary = analyzer.process_all_pdfs()
        
        # Final status and exit
        if summary["errors"] > 0:
            logger.warning(f"Completed with {summary['errors']} errors")
            print(f"\n⚠️  Processing completed with {summary['errors']} errors")
            print("Check the logs for details on failed files")
            sys.exit(1)
        else:
            logger.info("All files processed successfully")
            print(f"\n🎉 All {summary['processed']} files processed successfully!")
            print("\nFinal JSON Output Format:")
            print('   {')
            print('     "title": "Document Title",')
            print('     "outline": [')
            print('       {"level": "H1", "text": "Heading Text", "page": 1},')
            print('       {"level": "H2", "text": "Sub Heading", "page": 2}')
            print('     ]')
            print('   }')
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Fatal error in main execution: {str(e)}")
        print(f"\n❌ Fatal error: {str(e)}")
        print("Please check the logs and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()
