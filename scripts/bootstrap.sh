# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Please install UV first."
    exit 1
fi

# Install dependencies
uv sync
