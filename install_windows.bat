@echo off
echo ========================================
echo AnyLogic MCP Server - Windows Install
echo ========================================
echo.

echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ from python.org
    echo        Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)
python --version
echo.

echo Installing anylogic-mcp-server...
pip install -e .
if errorlevel 1 (
    echo ERROR: Installation failed.
    pause
    exit /b 1
)

echo.
echo Entry point installed at:
where anylogic-mcp
echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Create .mcp.json in your VS Code working directory.
echo    See WINDOWS_SETUP.md for the exact format.
echo.
echo 2. In VS Code: Ctrl+Shift+P ^> Developer: Reload Window
echo    Approve the "anylogic" MCP server when prompted.
echo.
echo 3. Ask Claude Code: "What are the AnyLogic PLE limits?"
echo    to verify the server is connected.
echo.
pause
