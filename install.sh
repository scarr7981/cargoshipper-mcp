#!/bin/bash
# CargoShipper MCP Server - Install with uvx

set -e

echo "🚀 Installing CargoShipper MCP Server"
echo "===================================="

# Check if uvx is available
if ! command -v uvx &> /dev/null; then
    echo "❌ uvx is not installed."
    echo "Please install uvx first:"
    echo "  pip install uvx"
    echo "  # or"
    echo "  pipx install uvx"
    exit 1
fi

echo "✅ uvx found"

# Install the package
echo "📦 Installing cargoshipper-mcp..."
uvx install .

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Copy and configure environment variables:"
echo "   cp .env.example ~/.config/cargoshipper-mcp/.env"
echo "   # Edit ~/.config/cargoshipper-mcp/.env with your API tokens"
echo ""
echo "2. The server is now available as 'cargoshipper-mcp' and configured in .mcp.json"
echo ""
echo "3. Test the installation:"
echo "   uvx run cargoshipper-mcp"
echo ""
echo "🔗 Ready for use with Claude Code!"