#!/usr/bin/env python3
"""
Unit tests for the PDF Structure Analysis Tool
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import PDFStructureAnalyzer


class TestPDFStructureAnalyzer(unittest.TestCase):
    """Test cases for PDFStructureAnalyzer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        
        self.input_dir.mkdir(parents=True)
        self.output_dir.mkdir(parents=True)
        
        self.analyzer = PDFStructureAnalyzer(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir)
        )
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertTrue(self.input_dir.exists())
        self.assertTrue(self.output_dir.exists())
        self.assertEqual(self.analyzer.input_dir, self.input_dir)
        self.assertEqual(self.analyzer.output_dir, self.output_dir)
    
    def test_get_pdf_files_empty_directory(self):
        """Test getting PDF files from empty directory."""
        pdf_files = self.analyzer.get_pdf_files()
        self.assertEqual(len(pdf_files), 0)
    
    def test_get_pdf_files_with_pdfs(self):
        """Test getting PDF files when PDFs exist."""
        # Create dummy PDF files
        (self.input_dir / "test1.pdf").touch()
        (self.input_dir / "test2.pdf").touch()
        (self.input_dir / "not_pdf.txt").touch()
        
        pdf_files = self.analyzer.get_pdf_files()
        self.assertEqual(len(pdf_files), 2)
        
        pdf_names = [f.name for f in pdf_files]
        self.assertIn("test1.pdf", pdf_names)
        self.assertIn("test2.pdf", pdf_names)
        self.assertNotIn("not_pdf.txt", pdf_names)
    
    def test_create_error_result(self):
        """Test error result creation."""
        error_result = self.analyzer._create_error_result("test.pdf", "Test error")
        
        self.assertEqual(error_result["document_info"]["filename"], "test.pdf")
        self.assertEqual(error_result["document_info"]["error"], "Test error")
        self.assertEqual(error_result["document_info"]["total_pages"], 0)
        self.assertEqual(len(error_result["structural_outline"]["headings"]), 0)
    
    def test_save_result(self):
        """Test saving analysis result."""
        test_result = {
            "document_info": {
                "filename": "test.pdf",
                "total_pages": 5,
                "title": "Test Document"
            },
            "structural_outline": {
                "title": "Test Title",
                "headings": []
            }
        }
        
        success = self.analyzer.save_result(test_result, "test.pdf")
        self.assertTrue(success)
        
        # Check if file was created
        output_file = self.output_dir / "test.json"
        self.assertTrue(output_file.exists())
        
        # Check file contents
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data["document_info"]["filename"], "test.pdf")
        self.assertIn("processing_timestamp", saved_data["document_info"])


if __name__ == '__main__':
    unittest.main()
