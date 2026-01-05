#!/bin/bash
# Build script for Render deployment

echo "Installing system dependencies..."
apt-get update
apt-get install -y build-essential wget

echo "Installing TA-Lib..."
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

echo "Installing Python packages..."
pip install --upgrade pip setuptools wheel
pip install -r requirements_minimal.txt

echo "Build complete!"
