#!/usr/bin/env python3
"""
Example and validation script for the final JSON output format
"""

import json
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def show_example_output():
    """Display the exact required JSON output format."""
    
    print("📋 Required JSON Output Format")
    print("=" * 40)
    
    # Example of the exact required format
    example_output = {
        "title": "Machine Learning Applications in Healthcare",
        "outline": [
            {
                "level": "H1",
                "text": "Introduction",
                "page": 1
            },
            {
                "level": "H2", 
                "text": "Background and Motivation",
                "page": 2
            },
            {
                "level": "H3",
                "text": "Related Work in Medical AI",
                "page": 2
            },
            {
                "level": "H1",
                "text": "Methodology",
                "page": 3
            },
            {
                "level": "H2",
                "text": "Data Collection Process",
                "page": 4
            },
            {
                "level": "H2",
                "text": "Machine Learning Models",
                "page": 5
            },
            {
                "level": "H3",
                "text": "Neural Network Architecture",
                "page": 5
            },
            {
                "level": "H1",
                "text": "Results and Analysis",
                "page": 7
            }
        ]
    }
    
    # Display formatted JSON
    formatted_json = json.dumps(example_output, indent=2, ensure_ascii=False)
    print(formatted_json)
    
    print(f"\n📊 Structure Summary:")
    print(f"• Title: 1 document title")
    print(f"• Outline: {len(example_output['outline'])} headings")
    
    # Count by level
    level_counts = {}
    for heading in example_output["outline"]:
        level = heading["level"]
        level_counts[level] = level_counts.get(level, 0) + 1
    
    print(f"• Level distribution: {level_counts}")
    
    return example_output


def validate_json_format(json_data):
    """Validate that JSON data matches the required format."""
    
    print("\n🔍 Validating JSON Format")
    print("-" * 30)
    
    errors = []
    
    # Check top-level structure
    if not isinstance(json_data, dict):
        errors.append("Root must be a dictionary/object")
        return errors
    
    # Check required keys
    if "title" not in json_data:
        errors.append("Missing required 'title' key")
    elif not isinstance(json_data["title"], str):
        errors.append("'title' must be a string")
    
    if "outline" not in json_data:
        errors.append("Missing required 'outline' key")
    elif not isinstance(json_data["outline"], list):
        errors.append("'outline' must be a list/array")
    else:
        # Validate each heading in outline
        for i, heading in enumerate(json_data["outline"]):
            if not isinstance(heading, dict):
                errors.append(f"Outline item {i} must be an object")
                continue
            
            # Check required heading keys
            required_keys = ["level", "text", "page"]
            for key in required_keys:
                if key not in heading:
                    errors.append(f"Outline item {i} missing required '{key}' key")
            
            # Validate data types and values
            if "level" in heading:
                if heading["level"] not in ["H1", "H2", "H3"]:
                    errors.append(f"Outline item {i} 'level' must be H1, H2, or H3")
            
            if "text" in heading and not isinstance(heading["text"], str):
                errors.append(f"Outline item {i} 'text' must be a string")
            
            if "page" in heading:
                if not isinstance(heading["page"], int) or heading["page"] < 1:
                    errors.append(f"Outline item {i} 'page' must be a positive integer")
    
    # Check for unexpected keys
    allowed_keys = {"title", "outline"}
    extra_keys = set(json_data.keys()) - allowed_keys
    if extra_keys:
        errors.append(f"Unexpected keys found: {extra_keys}")
    
    if errors:
        print("❌ Validation Failed:")
        for error in errors:
            print(f"   • {error}")
    else:
        print("✅ JSON format is valid!")
        print(f"   • Title: '{json_data['title']}'")
        print(f"   • Headings: {len(json_data['outline'])}")
    
    return errors


def test_output_files():
    """Test any existing output files to ensure they match the format."""
    
    output_dir = Path("../output")
    if not output_dir.exists():
        print("📁 No output directory found")
        return
    
    json_files = list(output_dir.glob("*.json"))
    json_files = [f for f in json_files if not f.name.endswith('_debug.json')]
    
    if not json_files:
        print("📄 No output JSON files found to test")
        return
    
    print(f"\n🧪 Testing {len(json_files)} output file(s)")
    print("=" * 40)
    
    for json_file in json_files:
        print(f"\n📄 Testing: {json_file.name}")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            errors = validate_json_format(data)
            if not errors:
                print(f"✅ {json_file.name} format is correct")
            
        except Exception as e:
            print(f"❌ Error reading {json_file.name}: {str(e)}")


if __name__ == "__main__":
    print("🔬 JSON Output Format Validator")
    print("Adobe India Hackathon - Challenge 1A")
    print("=" * 50)
    
    # Show the required format
    example = show_example_output()
    
    # Validate the example
    validate_json_format(example)
    
    # Test any existing output files
    test_output_files()
    
    print(f"\n📝 Key Requirements:")
    print(f"• Root object with 'title' and 'outline' keys only")
    print(f"• Title: string containing document title")
    print(f"• Outline: array of heading objects")
    print(f"• Each heading: level (H1/H2/H3), text (string), page (positive integer)")
    print(f"• No additional keys or metadata in the final output")
    
    print(f"\n🎯 Usage:")
    print(f"1. Place PDF files in input/ directory")
    print(f"2. Run: python src/main.py")
    print(f"3. Check output/ for [filename].json files")
    print(f"4. Each JSON file will have the exact required format")
