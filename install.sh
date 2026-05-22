#!/bin/bash

echo "========================================"
echo "AnyLogic MCP Server - Install"
echo "========================================"
echo ""

# Check Python 3.10+
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found."
    echo "Install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"; then
    echo "Python $PYTHON_VERSION found."
else
    echo "ERROR: Python $PYTHON_VERSION is too old. Python 3.10+ required."
    exit 1
fi
echo ""

# Install package
echo "Installing anylogic-mcp-server..."
pip3 install -e .
if [ $? -ne 0 ]; then
    echo "ERROR: Installation failed."
    exit 1
fi

# Find entry point
ENTRY=$(which anylogic-mcp 2>/dev/null)
if [ -z "$ENTRY" ]; then
    ENTRY=$(python3 -c "import site, os; dirs = site.getusersitepackages(); scripts = os.path.join(os.path.dirname(dirs), 'bin'); print(os.path.join(scripts, 'anylogic-mcp'))" 2>/dev/null)
fi

echo ""
echo "========================================"
echo "Installation complete!"
echo "========================================"
echo ""
echo "Entry point: ${ENTRY:-anylogic-mcp (run 'which anylogic-mcp' to confirm)}"
echo ""
echo "Next steps:"
echo ""
echo "1. Create .mcp.json in your VS Code working directory:"
echo ""
echo '   {
     "mcpServers": {
       "anylogic": {
         "command": "'"${ENTRY:-$(which anylogic-mcp 2>/dev/null || echo '/path/to/anylogic-mcp')}"'",
         "args": [],
         "env": {
           "ALP_OUTPUT_DIR": "/path/to/your/output/folder"
         }
       }
     }
   }'
echo ""
echo "2. In VS Code: Ctrl+Shift+P > Developer: Reload Window"
echo "   Approve the 'anylogic' MCP server when prompted."
echo ""
echo "3. Verify: ask Claude Code 'What are the AnyLogic PLE limits?'"
echo ""
echo "See WINDOWS_SETUP.md / README.md for full instructions."
echo ""
