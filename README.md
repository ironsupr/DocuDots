# DocuDots - PDF Structure Analysis Tool

<div align="center">

![DocuDots Logo](https://img.shields.io/badge/DocuDots-PDF%20Analyzer-blue?style=for-the-badge&logo=adobe)

**Adobe India Hackathon - Challenge 1A**

_Intelligent PDF structure extraction for document analysis and accessibility_

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-Latest-FF6B6B?style=flat-square)](https://pymupdf.readthedocs.io/)

</div>

## 🎯 Overview

DocuDots is an advanced PDF structure analysis tool that extracts hierarchical document outlines (Title, H1, H2, H3 headings) from PDF files and converts them into structured JSON format. Built specifically for the Adobe India Hackathon Challenge 1A, this tool uses sophisticated multi-factor heading detection algorithms that go beyond simple font-size analysis.

### 🌟 Key Features

- **🧠 Intelligent Heading Detection**: Multi-factor analysis using font properties, text patterns, document structure, and semantic context
- **📊 Hierarchical Classification**: Accurate H1, H2, H3 level determination based on content analysis
- **🎨 Context-Aware Processing**: Considers document layout, positioning, and typographic conventions
- **🔄 Batch Processing**: Analyze multiple PDF files in a single operation
- **📋 Clean JSON Output**: Generates only the required output files without debug clutter
- **🐳 Docker Ready**: Fully containerized for consistent execution across platforms
- **📖 Document Order Preservation**: Maintains heading order exactly as they appear in the PDF

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Docker Commands](#-docker-commands)
- [Output Format](#-output-format)
- [Technical Architecture](#-technical-architecture)
- [Algorithm Details](#-algorithm-details)
- [Project Structure](#-project-structure)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## 🚀 Quick Start

### Prerequisites

- **Docker**: Version 20.10 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 2GB RAM available for Docker

### 1. Clone the Repository

```bash
git clone https://github.com/ironsupr/DocuDots.git
cd DocuDots
```

### 2. Add Your PDF Files

Place your PDF files in the `input` directory:

```bash
# Create input directory if it doesn't exist
mkdir -p input

# Copy your PDF files
cp /path/to/your/document.pdf input/
```

### 3. Run DocuDots

**Windows (PowerShell):**

```powershell
.\run.ps1 run
```

**Linux/macOS (Bash):**

```bash
chmod +x run.sh
./run.sh run
```

### 4. Get Results

Your analyzed JSON files will be available in the `output` directory:

```bash
ls output/
# document.json
# another_document.json
```

## 🛠 Installation

### Option 1: Docker (Recommended)

```bash
# Build the DocuDots container
docker build --platform linux/amd64 -t docudots:latest .

# Verify the build
docker images docudots
```

### Option 2: Local Python Environment

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run directly
python src/main.py
```

## 💻 Usage

### Basic Usage

```bash
# Place PDF files in input directory
cp document.pdf input/

# Run analysis
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  docudots:latest
```

### Advanced Usage

```bash
# Run with custom input/output directories
docker run --rm \
  -v "/custom/input/path:/app/input" \
  -v "/custom/output/path:/app/output" \
  docudots:latest

# Run in development mode (interactive)
docker run -it --rm \
  -v "$(pwd):/app" \
  --entrypoint /bin/bash \
  docudots:latest
```

## 🐳 Docker Commands

### Build Commands

```bash
# Build the container
docker build --platform linux/amd64 -t docudots:latest .

# Build with no cache (force rebuild)
docker build --no-cache --platform linux/amd64 -t docudots:latest .

# Build with custom tag
docker build --platform linux/amd64 -t docudots:v1.0 .
```

### Run Commands

```bash
# Standard run
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  docudots:latest

# Background processing
docker run -d --name docudots-process \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  docudots:latest

# Interactive mode for debugging
docker run -it --rm \
  -v "$(pwd):/app" \
  --entrypoint /bin/bash \
  docudots:latest
```

### Management Commands

```bash
# List DocuDots images
docker images docudots

# Remove DocuDots container
docker rmi docudots:latest

# Clean up all containers and images
docker system prune -a

# View running containers
docker ps

# View container logs
docker logs docudots-process
```

### Using the Convenience Scripts

**Windows PowerShell (`run.ps1`):**

```powershell
# Build the container
.\run.ps1 build

# Run analysis
.\run.ps1 run

# Development mode
.\run.ps1 dev

# Run tests
.\run.ps1 test

# Clean up
.\run.ps1 clean

# View help
.\run.ps1 help
```

**Linux/macOS Bash (`run.sh`):**

```bash
# Make executable (first time only)
chmod +x run.sh

# Build the container
./run.sh build

# Run analysis
./run.sh run

# Development mode
./run.sh dev

# Run tests
./run.sh test

# Clean up
./run.sh clean

# View help
./run.sh help
```

## 📄 Output Format

DocuDots generates clean JSON files with the following structure:

```json
{
  "title": "Document Title Extracted from PDF",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Background Information",
      "page": 1
    },
    {
      "level": "H3",
      "text": "Previous Research",
      "page": 2
    },
    {
      "level": "H1",
      "text": "Methodology",
      "page": 3
    }
  ]
}
```

### Output Specifications

- **`title`**: Main document title extracted from the largest text or metadata
- **`outline`**: Array of heading objects in document order
- **`level`**: Heading hierarchy (H1, H2, H3)
- **`text`**: Complete heading text content
- **`page`**: Page number where the heading appears (1-indexed)

### File Naming Convention

- Input: `document.pdf` → Output: `document.json`
- Input: `resume.pdf` → Output: `resume.json`
- Input: `report_2025.pdf` → Output: `report_2025.json`

## 🔧 Technical Architecture

### Core Components

```
DocuDots Architecture
├── PDFStructureAnalyzer (Main Class)
│   ├── Text Block Extraction
│   ├── Font Style Analysis
│   ├── Heading Candidate Filtering
│   ├── Multi-Factor Classification
│   └── JSON Output Generation
├── Dockerfile (Container Definition)
├── Requirements Management
└── Cross-Platform Scripts
```

### Processing Pipeline

1. **PDF Loading**: Opens PDF using PyMuPDF (fitz)
2. **Text Extraction**: Extracts all text blocks with formatting properties
3. **Font Analysis**: Analyzes document typography to identify body text patterns
4. **Candidate Filtering**: Identifies potential headings using multiple criteria
5. **Level Classification**: Assigns H1/H2/H3 levels using scoring algorithm
6. **Title Extraction**: Identifies main document title
7. **JSON Generation**: Creates structured output in required format

### Algorithm Highlights

- **Multi-Factor Scoring**: Combines font size, position, text patterns, and semantic analysis
- **Context Awareness**: Considers surrounding text and document structure
- **Pattern Recognition**: Identifies numbered sections, bullet points, and formatting cues
- **Hierarchy Refinement**: Post-processes results to ensure logical heading structure

## 🧮 Algorithm Details

### Heading Detection Factors

| Factor            | Weight | Description                         |
| ----------------- | ------ | ----------------------------------- |
| **Font Size**     | 25%    | Relative to body text size          |
| **Typography**    | 25%    | Bold, italic, font family           |
| **Position**      | 20%    | Page location and vertical position |
| **Text Patterns** | 15%    | Keywords, numbering, structure      |
| **Context**       | 10%    | Surrounding content analysis        |
| **Length**        | 5%     | Word count and character length     |

### Classification Logic

```python
# Simplified classification algorithm
def classify_heading(text_block):
    score = {
        'H1': calculate_h1_score(text_block),
        'H2': calculate_h2_score(text_block),
        'H3': calculate_h3_score(text_block)
    }
    return max(score, key=score.get)
```

### Supported Document Types

- **Academic Papers**: Research papers, theses, dissertations
- **Technical Documents**: Manuals, specifications, guides
- **Business Reports**: Annual reports, proposals, presentations
- **Educational Materials**: Textbooks, course materials, handouts
- **Personal Documents**: Resumes, CVs, portfolios

## 📁 Project Structure

```
DocuDots/
├── src/
│   └── main.py              # Core analysis engine
├── input/                   # Place PDF files here
├── output/                  # Generated JSON files
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
├── run.ps1                # Windows PowerShell script
├── run.sh                 # Linux/macOS bash script
├── README.md              # This documentation
└── .dockerignore          # Docker ignore rules
```

### Key Files Description

- **`src/main.py`**: Main Python script containing the PDFStructureAnalyzer class
- **`Dockerfile`**: Multi-stage Docker build configuration
- **`requirements.txt`**: Python package dependencies (PyMuPDF, etc.)
- **`run.ps1`** / **`run.sh`**: Cross-platform convenience scripts
- **`input/`**: Directory for source PDF files
- **`output/`**: Directory for generated JSON results

## 📊 Examples

### Example 1: Academic Paper

**Input PDF**: Research paper on machine learning
**Output JSON**:

```json
{
  "title": "Deep Learning Approaches for Natural Language Processing",
  "outline": [
    { "level": "H1", "text": "Abstract", "page": 1 },
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "Problem Statement", "page": 2 },
    { "level": "H2", "text": "Related Work", "page": 3 },
    { "level": "H1", "text": "Methodology", "page": 4 },
    { "level": "H2", "text": "Data Collection", "page": 4 },
    { "level": "H3", "text": "Dataset Preparation", "page": 5 }
  ]
}
```

### Example 2: Resume/CV

**Input PDF**: Professional resume
**Output JSON**:

```json
{
  "title": "John Doe - Software Engineer",
  "outline": [
    { "level": "H1", "text": "John Doe", "page": 1 },
    { "level": "H1", "text": "Experience", "page": 1 },
    { "level": "H2", "text": "Senior Software Engineer", "page": 1 },
    { "level": "H2", "text": "Software Developer", "page": 1 },
    { "level": "H1", "text": "Education", "page": 1 },
    { "level": "H1", "text": "Skills", "page": 1 },
    { "level": "H2", "text": "Programming Languages", "page": 1 }
  ]
}
```

### Example 3: Technical Manual

**Input PDF**: User manual for software
**Output JSON**:

```json
{
  "title": "User Guide - DocuDots PDF Analyzer",
  "outline": [
    { "level": "H1", "text": "Getting Started", "page": 1 },
    { "level": "H2", "text": "Installation", "page": 2 },
    { "level": "H3", "text": "System Requirements", "page": 2 },
    { "level": "H3", "text": "Docker Setup", "page": 3 },
    { "level": "H1", "text": "Usage Instructions", "page": 4 },
    { "level": "H2", "text": "Basic Operations", "page": 4 }
  ]
}
```

## 🔍 Troubleshooting

### Common Issues

#### 1. No PDF Files Found

```
⚠️ No PDF files found in input directory
```

**Solution**: Ensure PDF files are placed in the `input/` directory.

#### 2. Docker Build Fails

```
Error: failed to solve: failed to read dockerfile
```

**Solution**: Ensure you're running the command from the DocuDots project root directory.

#### 3. Permission Denied (Linux/macOS)

```
Permission denied: ./run.sh
```

**Solution**: Make the script executable:

```bash
chmod +x run.sh
```

#### 4. Empty Output Files

```
JSON files are generated but contain no headings
```

**Solution**: The PDF might have unusual formatting. Check the logs for details about text block extraction.

### Debug Mode

Run in development mode to see detailed processing information:

```bash
# Windows
.\run.ps1 dev

# Linux/macOS
./run.sh dev
```

### Log Analysis

DocuDots provides detailed logging:

```
2025-07-27 10:30:45,123 - INFO - Starting PDF Structure Analysis Tool
2025-07-27 10:30:45,124 - INFO - Adobe India Hackathon - Challenge 1A
2025-07-27 10:30:45,126 - INFO - Initialized PDF analyzer
2025-07-27 10:30:45,193 - INFO - Found 5 PDF files in /app/input
2025-07-27 10:30:45,194 - INFO - Starting analysis of PDF: document.pdf
```

### Performance Optimization

For large PDFs or batch processing:

1. **Increase Docker Memory**: Allocate more RAM to Docker
2. **Use SSD Storage**: Place input/output directories on fast storage
3. **Batch Size**: Process files in smaller batches for very large datasets

## 🤝 Contributing

### Development Setup

1. **Fork the Repository**
2. **Clone Your Fork**

```bash
git clone https://github.com/yourusername/DocuDots.git
cd DocuDots
```

3. **Create Development Environment**

```bash
# Using Docker
./run.sh dev

# Or local Python
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

4. **Make Changes**
5. **Test Your Changes**

```bash
./run.sh test
```

6. **Submit Pull Request**

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and returns
- Include comprehensive docstrings
- Add logging for important operations

### Testing

```bash
# Run all tests
./run.sh test

# Run specific test
python -m pytest tests/test_pdf_analyzer.py

# Run with coverage
python -m pytest --cov=src tests/
```

## 📜 License

This project is created for the Adobe India Hackathon - Challenge 1A. Please refer to the hackathon terms and conditions for usage rights and restrictions.

## 🙏 Acknowledgments

- **Adobe India Hackathon** for providing the challenge and motivation
- **PyMuPDF Community** for the excellent PDF processing library
- **Docker Team** for containerization technology
- **Python Community** for the robust ecosystem

## 📞 Support

For issues, questions, or contributions:

1. **GitHub Issues**: [Create an issue](https://github.com/ironsupr/DocuDots/issues)
2. **Documentation**: Refer to this README and inline code documentation
3. **Hackathon Support**: Follow Adobe India Hackathon communication channels

---

<div align="center">

**Built with ❤️ for Adobe India Hackathon 2025**

_DocuDots - Making PDF structure analysis intelligent and accessible_

</div>
