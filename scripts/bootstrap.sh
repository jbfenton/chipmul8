#!/usr/bin/env bash
set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Please install uv first."
    exit 1
fi

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
