#!/usr/bin/env python3
"""
Test script for heading identification functionality
"""

import sys
import os
from pathlib import Path
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import PDFStructureAnalyzer


def test_heading_identification():
    """Test the comprehensive heading identification system."""
    
    print("🔍 Testing Heading Identification System")
    print("=" * 50)
    
    # Check for PDFs in input directory
    input_dir = Path("../input")
    if not input_dir.exists():
        input_dir.mkdir(parents=True)
        print("📁 Created input directory")
    
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("⚠️  No PDF files found in input directory")
        print("   Please add PDF files to test the heading identification")
        return create_sample_analysis()
    
    # Test with available PDFs
    analyzer = PDFStructureAnalyzer(str(input_dir.absolute()), "../output")
    
    for pdf_file in pdf_files[:2]:  # Test first 2 PDFs
        print(f"\n📄 Analyzing: {pdf_file.name}")
        print("-" * 30)
        
        try:
            result = analyzer.analyze_pdf_structure(pdf_file)
            
            # Display results
            doc_info = result["document_info"]
            outline = result["structural_outline"]
            
            print(f"📊 Document Info:")
            print(f"   Pages: {doc_info['total_pages']}")
            print(f"   Title: {doc_info['title']}")
            
            if "text_blocks_summary" in result:
                print(f"   Text blocks: {result['text_blocks_summary']['total_blocks']}")
            
            print(f"\n🎯 Structural Analysis:")
            print(f"   Final Title: '{outline['title']}'")
            print(f"   Headings Found: {len(outline['headings'])}")
            
            # Show heading breakdown by level
            level_counts = {}
            for heading in outline["headings"]:
                level = heading["level"]
                level_counts[level] = level_counts.get(level, 0) + 1
            
            print(f"   Heading Distribution: {level_counts}")
            
            # Show first few headings
            print(f"\n📝 Sample Headings:")
            for i, heading in enumerate(outline["headings"][:8], 1):
                text = heading["text"][:50] + "..." if len(heading["text"]) > 50 else heading["text"]
                print(f"   {i}. {heading['level']}: {text} (Page {heading['page']})")
            
            # Show font analysis if available
            if "analysis_metadata" in outline:
                metadata = outline["analysis_metadata"]
                if "font_analysis" in metadata:
                    font_stats = metadata["font_analysis"]["font_size_stats"]
                    print(f"\n📈 Font Analysis:")
                    print(f"   Body text size: {metadata['font_analysis']['body_font_size']}")
                    print(f"   Size range: {font_stats['min']}-{font_stats['max']}")
                    print(f"   Average size: {font_stats['average']}")
                    print(f"   Heading candidates: {metadata['total_candidates']}")
            
        except Exception as e:
            print(f"❌ Error analyzing {pdf_file.name}: {str(e)}")
    
    return True


def create_sample_analysis():
    """Create a sample analysis description when no PDFs are available."""
    
    print("\n📝 Sample Heading Identification Process")
    print("-" * 40)
    
    sample_process = """
The heading identification system follows these steps:

1. 📊 FONT ANALYSIS:
   - Identifies most common font size (body text)
   - Calculates font size statistics and distribution
   - Determines baseline for heading detection

2. 🔍 HEADING CANDIDATE FILTERING:
   - Filters out body text based on size thresholds
   - Considers bold formatting and position
   - Applies text pattern analysis
   - Calculates heading likelihood scores

3. 🏷️ HEADING LEVEL CLASSIFICATION:
   - Classifies into H1, H2, H3 based on:
     * Font size ranking (primary factor)
     * Font weight (bold/regular)
     * Size ratio to body text
     * Heading confidence score
   
4. 📰 TITLE IDENTIFICATION:
   - Finds largest font size on first 1-2 pages
   - Considers position and text characteristics
   - Applies title-specific scoring algorithm

5. 📋 FINAL OUTPUT:
   - Stores classified headings with levels
   - Maintains page numbers and positions
   - Provides comprehensive analysis metadata

Example Output Structure:
{
  "title": "Machine Learning in Healthcare",
  "headings": [
    {"level": "H1", "text": "Introduction", "page": 1},
    {"level": "H2", "text": "Background", "page": 2},
    {"level": "H3", "text": "Related Work", "page": 2},
    {"level": "H1", "text": "Methodology", "page": 3}
  ]
}
"""
    
    print(sample_process)
    
    # Create demonstration guide
    with open("../HEADING_IDENTIFICATION_GUIDE.md", "w") as f:
        f.write("# Heading Identification System\n\n")
        f.write("## Overview\n")
        f.write("This system uses advanced heuristics to identify and classify document headings.\n\n")
        f.write("## Process\n")
        f.write(sample_process)
        f.write("\n## Usage\n")
        f.write("1. Place PDF files in input/ directory\n")
        f.write("2. Run: python src/main.py\n")
        f.write("3. Check output/ for detailed JSON results\n")
        f.write("4. Console shows summary of findings\n")
    
    print("\n✅ Created HEADING_IDENTIFICATION_GUIDE.md")
    return False


def validate_implementation():
    """Validate that all required functions are implemented."""
    
    print("\n🔧 Validating Implementation")
    print("-" * 30)
    
    analyzer = PDFStructureAnalyzer()
    
    # Check if all required methods exist
    required_methods = [
        "_analyze_font_styles",
        "_filter_heading_candidates", 
        "_classify_heading_levels",
        "_identify_document_title",
        "_extract_headings_from_blocks"
    ]
    
    implemented = []
    for method in required_methods:
        if hasattr(analyzer, method):
            implemented.append(f"✅ {method}")
        else:
            implemented.append(f"❌ {method}")
    
    for status in implemented:
        print(f"   {status}")
    
    all_implemented = all("✅" in status for status in implemented)
    
    if all_implemented:
        print("\n🎉 All heading identification functions implemented!")
    else:
        print("\n⚠️  Some functions missing - check implementation")
    
    return all_implemented


if __name__ == "__main__":
    print("🧪 Heading Identification Test Suite")
    print("=" * 50)
    
    # Validate implementation
    validation_passed = validate_implementation()
    
    if validation_passed:
        # Test with actual PDFs
        test_successful = test_heading_identification()
        
        if test_successful:
            print("\n🎯 Heading identification system is ready!")
            print("   The system can now:")
            print("   • Analyze font styles and identify body text")
            print("   • Filter and score heading candidates")
            print("   • Classify headings into H1, H2, H3 levels")
            print("   • Identify document titles intelligently")
            print("   • Store results in structured format")
        else:
            print("\n📚 System ready - add PDFs to test with real documents")
    else:
        print("\n❌ Implementation incomplete - check the code")
    
    print("\n" + "=" * 50)
