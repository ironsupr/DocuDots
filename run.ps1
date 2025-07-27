# Adobe India Hackathon - Challenge 1A
# Build and Run Script for DocuDots PDF Analyzer (PowerShell)

param(
    [Parameter(Position = 0)]
    [ValidateSet("build", "run", "dev", "test", "clean", "")]
    [string]$Command = ""
)

function Show-Usage {
    Write-Host "========================================"
    Write-Host "DocuDots - PDF Structure Analyzer"
    Write-Host "Adobe India Hackathon - Challenge 1A"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "Usage: .\run.ps1 [build|run|dev|test|clean]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  build  - Build the Docker image"
    Write-Host "  run    - Run the PDF analyzer (requires input PDFs)"
    Write-Host "  dev    - Run in development mode with volume mounts"
    Write-Host "  test   - Run unit tests"
    Write-Host "  clean  - Remove Docker images and containers"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run.ps1 build"
    Write-Host "  .\run.ps1 run"
    Write-Host "  .\run.ps1 dev"
    exit 1
}

function Build-Image {
    Write-Host "Building Docker image..."
    docker build --platform linux/amd64 -t docudots:latest .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Build completed successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "Build failed!" -ForegroundColor Red
        exit 1
    }
}

function Run-Analyzer {
    Write-Host "Running PDF analyzer..."
    
    # Check if input directory has PDF files
    if (!(Test-Path "./input") -or !(Get-ChildItem "./input" -Filter "*.pdf" -ErrorAction SilentlyContinue)) {
        Write-Host "Warning: No PDF files found in .\input directory" -ForegroundColor Yellow
        Write-Host "Please place your PDF files in the .\input directory"
        Write-Host "Creating input directory if it doesn't exist..."
        New-Item -ItemType Directory -Force -Path "./input" | Out-Null
        exit 1
    }
    
    # Ensure output directory exists
    New-Item -ItemType Directory -Force -Path "./output" | Out-Null
    
    # Get absolute paths for volume mounting
    $inputPath = (Resolve-Path "./input").Path
    $outputPath = (Resolve-Path "./output").Path
    
    # Run the container
    docker run --rm `
        --platform linux/amd64 `
        -v "${inputPath}:/app/input:ro" `
        -v "${outputPath}:/app/output:rw" `
        docudots:latest
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Processing completed! Check .\output directory for results." -ForegroundColor Green
    }
    else {
        Write-Host "Processing failed!" -ForegroundColor Red
    }
}

function Run-Dev {
    Write-Host "Running in development mode..."
    
    # Ensure directories exist
    New-Item -ItemType Directory -Force -Path "./input" | Out-Null
    New-Item -ItemType Directory -Force -Path "./output" | Out-Null
    
    # Get absolute paths for volume mounting
    $inputPath = (Resolve-Path "./input").Path
    $outputPath = (Resolve-Path "./output").Path
    $srcPath = (Resolve-Path "./src").Path
    
    # Run with source code mounted for development
    docker run --rm -it `
        --platform linux/amd64 `
        -v "${inputPath}:/app/input:ro" `
        -v "${outputPath}:/app/output:rw" `
        -v "${srcPath}:/app/src:rw" `
        --entrypoint /bin/bash `
        docudots:latest
}

function Run-Tests {
    Write-Host "Running unit tests..."
    
    # Get absolute paths for volume mounting
    $testsPath = (Resolve-Path "./tests").Path
    $srcPath = (Resolve-Path "./src").Path
    
    # Run tests in container
    docker run --rm `
        --platform linux/amd64 `
        -v "${testsPath}:/app/tests:ro" `
        -v "${srcPath}:/app/src:ro" `
        --entrypoint python `
        docudots:latest -m pytest tests/ -v
}

function Clean-Resources {
    Write-Host "Cleaning up Docker resources..."
    
    # Remove containers
    $containers = docker ps -a --filter "ancestor=docudots" --format "{{.ID}}"
    if ($containers) {
        docker rm -f $containers
    }
    
    # Remove images
    $images = docker images "docudots" --format "{{.ID}}"
    if ($images) {
        docker rmi -f $images
    }
    
    Write-Host "Cleanup completed!" -ForegroundColor Green
}

# Main script logic
switch ($Command) {
    "build" {
        Build-Image
    }
    "run" {
        Build-Image
        Run-Analyzer
    }
    "dev" {
        Build-Image
        Run-Dev
    }
    "test" {
        Build-Image
        Run-Tests
    }
    "clean" {
        Clean-Resources
    }
    default {
        Show-Usage
    }
}
