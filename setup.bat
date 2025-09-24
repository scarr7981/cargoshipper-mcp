@echo off
REM CargoShipper MCP Server Setup Script for Windows

echo 🚀 CargoShipper MCP Server Setup
echo ================================

REM Check Python version
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python 3.11 or higher is required
    exit /b 1
)

for /f "tokens=*" %%i in ('python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"') do set python_version=%%i
echo ✅ Python %python_version% detected

REM Create virtual environment
echo 📦 Creating virtual environment...
if exist ".venv" (
    echo    Virtual environment already exists
) else (
    python -m venv .venv
    echo    Virtual environment created in .venv\
)

REM Activate virtual environment  
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
pip install --upgrade pip

REM Install dependencies
echo 📋 Installing dependencies...
pip install -r requirements.txt

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo 1. Copy .env.example to .env and configure your API tokens:
echo    copy .env.example .env
echo.
echo 2. Edit .env with your API credentials:
echo    - DIGITALOCEAN_TOKEN=your_token_here
echo    - CLOUDFLARE_API_TOKEN=your_token_here
echo.
echo 3. Test the installation:
echo    .venv\Scripts\activate.bat
echo    python test_server.py
echo.
echo 4. Run the MCP server:
echo    .venv\Scripts\activate.bat
echo    python -m src.server
echo.
echo 🔗 The server is configured in .mcp.json and ready for Claude Code!