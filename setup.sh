#!/bin/bash
# CargoShipper MCP Server Setup Script

set -e

echo "🚀 CargoShipper MCP Server Setup"
echo "================================"

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.11"

if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "✅ Python $python_version detected (>= $required_version required)"
else
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "   Virtual environment already exists"
else
    python3 -m venv .venv
    echo "   Virtual environment created in .venv/"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Copy .env.example to .env and configure your API tokens:"
echo "   cp .env.example .env"
echo ""
echo "2. Edit .env with your API credentials:"
echo "   - DIGITALOCEAN_TOKEN=your_token_here"
echo "   - CLOUDFLARE_API_TOKEN=your_token_here"
echo ""
echo "3. Test the installation:"
echo "   source .venv/bin/activate"
echo "   python test_server.py"
echo ""
echo "4. Run the MCP server:"
echo "   source .venv/bin/activate"
echo "   python -m src.server"
echo ""
echo "🔗 The server is configured in .mcp.json and ready for Claude Code!"