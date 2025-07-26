#!/bin/bash

# Adobe India Hackathon - Challenge 1A
# Build and Run Script for DocuDots PDF Analyzer

set -e

echo "========================================"
echo "DocuDots - PDF Structure Analyzer"
echo "Adobe India Hackathon - Challenge 1A"
echo "========================================"

# Function to display usage
usage() {
    echo "Usage: $0 [build|run|dev|test|clean]"
    echo ""
    echo "Commands:"
    echo "  build  - Build the Docker image"
    echo "  run    - Run the PDF analyzer (requires input PDFs)"
    echo "  dev    - Run in development mode with volume mounts"
    echo "  test   - Run unit tests"
    echo "  clean  - Remove Docker images and containers"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 run"
    echo "  $0 dev"
    exit 1
}

# Build Docker image
build() {
    echo "Building Docker image..."
    docker build --platform linux/amd64 -t docudots:latest .
    echo "Build completed successfully!"
}

# Run the analyzer
run() {
    echo "Running PDF analyzer..."
    
    # Check if input directory has PDF files
    if [ ! -d "./input" ] || [ -z "$(ls -A ./input/*.pdf 2>/dev/null)" ]; then
        echo "Warning: No PDF files found in ./input directory"
        echo "Please place your PDF files in the ./input directory"
        echo "Creating input directory if it doesn't exist..."
        mkdir -p ./input
        exit 1
    fi
    
    # Ensure output directory exists
    mkdir -p ./output
    
    # Run the container
    docker run --rm \
        --platform linux/amd64 \
        -v "$(pwd)/input:/app/input:ro" \
        -v "$(pwd)/output:/app/output:rw" \
        docudots:latest
    
    echo "Processing completed! Check ./output directory for results."
}

# Run in development mode
dev() {
    echo "Running in development mode..."
    
    # Ensure directories exist
    mkdir -p ./input ./output
    
    # Run with source code mounted for development
    docker run --rm -it \
        --platform linux/amd64 \
        -v "$(pwd)/input:/app/input:ro" \
        -v "$(pwd)/output:/app/output:rw" \
        -v "$(pwd)/src:/app/src:rw" \
        --entrypoint /bin/bash \
        docudots:latest
}

# Run tests
test() {
    echo "Running unit tests..."
    
    # Run tests in container
    docker run --rm \
        --platform linux/amd64 \
        -v "$(pwd)/tests:/app/tests:ro" \
        -v "$(pwd)/src:/app/src:ro" \
        --entrypoint python \
        docudots:latest -m pytest tests/ -v
}

# Clean up Docker resources
clean() {
    echo "Cleaning up Docker resources..."
    
    # Remove containers
    docker ps -a --filter "ancestor=docudots" --format "{{.ID}}" | xargs -r docker rm -f
    
    # Remove images
    docker images "docudots" --format "{{.ID}}" | xargs -r docker rmi -f
    
    echo "Cleanup completed!"
}

# Main script logic
case "${1:-}" in
    build)
        build
        ;;
    run)
        build
        run
        ;;
    dev)
        build
        dev
        ;;
    test)
        build
        test
        ;;
    clean)
        clean
        ;;
    *)
        usage
        ;;
esac
