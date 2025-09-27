#!/bin/bash

# Excel to Windows Converter Script
# This script converts Excel files to Windows-compatible format

echo "🚀 Starting Excel to Windows conversion..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 to continue."
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import openpyxl, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required packages..."
    pip3 install openpyxl pandas
fi

# Run the conversion script
echo "🔄 Running conversion..."
python3 scripts/convert_excel_windows.py

# Check results
if [ $? -eq 0 ]; then
    echo "✅ Conversion completed successfully!"
    echo "📁 Windows-compatible files are available in: file_windows/"

    # List converted files
    if [ -d "file_windows" ]; then
        echo ""
        echo "📄 Converted files:"
        ls -la file_windows/
    fi
else
    echo "❌ Conversion failed. Please check the error messages above."
    exit 1
fi