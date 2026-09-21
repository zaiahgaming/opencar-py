#!/bin/bash
# Master build script for OpenCar

# Check for pyinstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

echo "Building OpenCar for Linux..."
pyinstaller --clean opencar.spec

echo "Copying assets and config..."
cp -r assets dist/
cp opencar.conf dist/

chmod +x dist/opencar

echo "================================================="
echo "Build success! Executable located at: $(pwd)/dist/opencar"
echo "================================================="
echo "Note: To build for Windows, use opencar-win.spec on a Windows machine or via Wine + Windows Python."
