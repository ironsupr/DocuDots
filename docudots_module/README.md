# DocuDots PDF Analysis Module

A robust Python module for extracting structured outlines from PDF documents.

## Quick Start

```python
from docudots_module import PDFAnalyzer

# Initialize analyzer
analyzer = PDFAnalyzer()

# Analyze PDF
result = analyzer.analyze_pdf("document.pdf")

# Access results
print(f"Title: {result['title']}")
for heading in result['outline']:
    print(f"{heading['level']}: {heading['text']} (Page {heading['page']})")
```

## Features

- Multi-factor heading detection (font size, weight, positioning)
- Multilingual support for international documents
- Robust error handling and validation
- Retry logic with timeout and circuit breaker patterns
- Clean JSON output format
- Batch processing capabilities

## Installation

```bash
pip install -e .
```

Or copy the module folder into your project and import directly.

## Requirements

- Python 3.8+
- PyMuPDF (fitz)
- psutil (optional, for resource monitoring)

## Output Format

```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Chapter 1", "page": 0 },
    { "level": "H2", "text": "Section 1.1", "page": 1 }
  ]
}
```

## Configuration

```python
from docudots_module import PDFAnalyzer, Config

config = Config()
config.MAX_HEADINGS_PER_DOCUMENT = 30
config.MAX_FILE_SIZE_MB = 50

analyzer = PDFAnalyzer(config)
```

---

**Adobe India Hackathon - Challenge 1A**
