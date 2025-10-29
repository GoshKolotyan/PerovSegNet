#!/bin/bash
# Build script for PerovSegNet Desktop Application
# This ensures the virtual environment is used

set -e  # Exit on error

echo "=================================="
echo "Building PerovSegNet Desktop App"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please create it first: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install project dependencies
echo "Installing/updating project dependencies..."
pip install -e . > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "⚠ Warning: Could not install dependencies"
fi

# Verify PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/

# Build the executable
echo ""
echo "Building executable..."
echo "(This may take 1-2 minutes)"
echo ""
pyinstaller PerovSegNet.spec

# Check if build succeeded
if [ -f "dist/PerovSegNet" ]; then
    echo ""
    echo "=================================="
    echo "✅ Build completed successfully!"
    echo "=================================="
    echo ""
    echo "Executable location: dist/PerovSegNet"
    echo "Size: $(du -h dist/PerovSegNet | cut -f1)"
    echo ""
    echo "To test it, run:"
    echo "  ./dist/PerovSegNet"
    echo ""
else
    echo ""
    echo "❌ Build failed!"
    echo "Check the output above for errors."
    exit 1
fi
