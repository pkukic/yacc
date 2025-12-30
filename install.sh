#!/bin/bash

# Install script for yacc - Syntax analyzer generator

echo "Installing yacc - Syntax Analyzer Generator"
echo "============================================"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "uv found: $(uv --version)"

# Sync dependencies using uv
echo "Setting up Python environment with uv..."
uv sync

echo ""
echo "Installation complete!"
echo ""
echo "Usage:"
echo "  uv run python GSA.py < language_definition"
echo ""
echo "For testing:"
echo "  ./test_lab.sh"
echo "  or"
echo "  uv run python test_lab.py"
echo ""
