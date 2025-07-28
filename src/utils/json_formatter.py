#!/usr/bin/env python3
"""
Utility functions for JSON formatting and validation
"""

import json
from typing import Dict, Any, List
from jsonschema import validate, ValidationError


def format_json_output(data: Dict[str, Any], indent: int = 2) -> str:
    """
    Format dictionary as pretty JSON string.
    
    Args:
        data: Dictionary to format
        indent: Indentation level
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


def validate_output_schema(data: Dict[str, Any]) -> bool:
    """
    Validate the output JSON against the expected schema.
    
    Args:
        data: Dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    schema = {
        "type": "object",
        "required": ["document_info", "structural_outline"],
        "properties": {
            "document_info": {
                "type": "object",
                "required": ["filename", "total_pages", "title"],
                "properties": {
                    "filename": {"type": "string"},
                    "total_pages": {"type": "integer", "minimum": 0},
                    "title": {"type": "string"},
                    "processing_timestamp": {"type": ["string", "null"]},
                    "error": {"type": "string"}
                }
            },
            "structural_outline": {
                "type": "object",
                "required": ["title", "headings"],
                "properties": {
                    "title": {"type": "string"},
                    "headings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["level", "text", "page"],
                            "properties": {
                                "level": {"type": "string", "enum": ["H1", "H2", "H3"]},
                                "text": {"type": "string"},
                                "page": {"type": "integer", "minimum": 1},
                                "position": {
                                    "type": "object",
                                    "properties": {
                                        "x": {"type": "number"},
                                        "y": {"type": "number"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError:
        return False


def create_empty_outline() -> Dict[str, Any]:
    """
    Create an empty structural outline template.
    
    Returns:
        Empty outline dictionary
    """
    return {
        "document_info": {
            "filename": "",
            "total_pages": 0,
            "title": "",
            "processing_timestamp": None
        },
        "structural_outline": {
            "title": "",
            "headings": []
        }
    }
