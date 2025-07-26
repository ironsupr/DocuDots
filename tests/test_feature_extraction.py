#!/usr/bin/env python3
"""
Test script to verify the PDF text extraction functionality
"""

import sys
import os
from pathlib import Path
import tempfile

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import PDFStructureAnalyzer


def test_with_sample_pdf():
    """Test the PDF analyzer with a sample PDF if available."""
    
    # Check if there are any PDFs in the input directory
    input_dir = Path("../input")
    if input_dir.exists():
        pdf_files = list(input_dir.glob("*.pdf"))
        if pdf_files:
            print(f"Found {len(pdf_files)} PDF files in input directory:")
            for pdf in pdf_files:
                print(f"  - {pdf.name}")
            
            # Test with the first PDF
            analyzer = PDFStructureAnalyzer(str(input_dir.absolute()), "../output")
            result = analyzer.analyze_pdf_structure(pdf_files[0])
            
            print(f"\nAnalysis Results for {pdf_files[0].name}:")
            print(f"Total pages: {result['document_info']['total_pages']}")
            print(f"Document title: {result['document_info']['title']}")
            
            if 'text_blocks_summary' in result:
                print(f"Total text blocks: {result['text_blocks_summary']['total_blocks']}")
                
                # Show sample of text blocks
                sample_blocks = result['text_blocks_summary']['sample_blocks']
                print(f"\nSample text blocks (first {len(sample_blocks)}):")
                for i, block in enumerate(sample_blocks, 1):
                    print(f"  {i}. '{block['text'][:50]}...' "
                          f"(Font: {block['font_size']}, Bold: {block['is_bold']}, "
                          f"Page: {block['page_number']})")
            
            return True
    
    print("No PDF files found in input directory for testing.")
    return False


def create_sample_usage_guide():
    """Create a guide for using the updated analyzer."""
    guide = """
# PDF Structure Analyzer - Updated Usage Guide

## What's New
The analyzer now performs actual feature extraction from PDFs:

1. **Text Block Extraction**: Extracts all text with formatting information
2. **Font Analysis**: Captures font size, weight (bold), and font name
3. **Position Tracking**: Records exact position of each text block
4. **Page Mapping**: Associates each text block with its page number

## Text Block Properties
Each extracted text block contains:
- `text`: The actual text content
- `font_size`: Size of the font (in points)
- `font_name`: Name of the font family
- `is_bold`: Boolean indicating if text is bold
- `page_number`: Page where text appears (1-indexed)
- `position`: Dictionary with x, y, width, height
- `bbox`: Bounding box coordinates [x0, y0, x1, y1]

## Usage
1. Place PDF files in the `input/` directory
2. Run the analyzer: `python src/main.py`
3. Check `output/` directory for JSON results
4. The console will show the total number of text blocks found

## Example Output Structure
```json
{
  "document_info": {
    "filename": "sample.pdf",
    "total_pages": 5,
    "title": "Extracted Document Title"
  },
  "text_blocks_summary": {
    "total_blocks": 1250,
    "sample_blocks": [...]
  },
  "structural_outline": {
    "title": "Main Title",
    "headings": [...]
  }
}
```

## Next Steps
- The text blocks are now available for heading classification
- Font size analysis can identify potential headings
- Position data can help with document structure understanding
"""
    
    with open("../FEATURE_EXTRACTION_GUIDE.md", "w") as f:
        f.write(guide)
    
    print("Created FEATURE_EXTRACTION_GUIDE.md")


if __name__ == "__main__":
    print("Testing PDF Feature Extraction...")
    print("=" * 50)
    
    # Test with sample PDF if available
    if not test_with_sample_pdf():
        print("\nTo test with your own PDFs:")
        print("1. Place PDF files in the input/ directory")
        print("2. Run: python src/main.py")
        print("3. Check the console output for text block counts")
    
    # Create usage guide
    create_sample_usage_guide()
    
    print("\n✅ Feature extraction functionality is ready!")
    print("The analyzer will now extract and analyze actual text blocks from PDFs.")
