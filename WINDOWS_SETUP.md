# Windows Setup — AnyLogic MCP Server

---

## Step 1: Install Python (if needed)

1. Download Python 3.10+ from https://www.python.org/downloads/
2. Run the installer — **check "Add Python to PATH"**
3. Verify: open Command Prompt and run `python --version`

---

## Step 2: Install the package

Open Command Prompt in the `anylogic-mcp-github` folder:

```cmd
cd "<path to anylogic-mcp-github>"
pip install -e .
```

Find the installed entry point:
```cmd
where anylogic-mcp
```
Copy this path — you need it in Step 3.

---

## Step 3: Create `.mcp.json`

In your working directory (the folder you open in VS Code), create a file named `.mcp.json`:

```json
{
  "mcpServers": {
    "anylogic": {
      "command": "<paste anylogic-mcp.exe path here>",
      "args": [],
      "env": {
        "ALP_OUTPUT_DIR": "<folder where .alp files will be saved>"
      }
    }
  }
}
```

**Example:**
```json
{
  "mcpServers": {
    "anylogic": {
      "command": "C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python312\\Scripts\\anylogic-mcp.exe",
      "args": [],
      "env": {
        "ALP_OUTPUT_DIR": "C:\\Users\\YourName\\Documents\\Simulations"
      }
    }
  }
}
```

> Use double backslashes (`\\`) in JSON paths on Windows.

---

## Step 4: Activate in Claude Code

1. Open VS Code in the folder containing `.mcp.json`
2. Press `Ctrl+Shift+P` → **Developer: Reload Window**
3. When prompted to approve the `anylogic` MCP server, click **Allow**

**Verify it works** — ask Claude Code:
```
What are the AnyLogic PLE limits?
```
It should call the `anylogic_get_ple_limits` tool and return a structured answer.

---

## Step 5: Install AnyLogic PLE (Free)

1. Download: https://www.anylogic.com/downloads/personal-learning-edition-download/
2. Install (~15 minutes)
3. Open `.alp` files from your `ALP_OUTPUT_DIR`
4. Click **Run** to see the simulation

---

## Troubleshooting

| Error | Fix |
|---|---|
| `python is not recognized` | Python not in PATH — reinstall and check "Add Python to PATH" |
| `pip is not recognized` | Use `python -m pip install -e .` |
| `anylogic-mcp not found` | Re-run `pip install -e .` in the correct directory |
| MCP tools not appearing in Claude Code | Check `.mcp.json` is in the open folder; reload window; approve server |
| `Access denied` during install | Run Command Prompt as Administrator |
| OneDrive sync issues | Pause OneDrive sync during install, or install in a non-OneDrive location |

---

## Optional: AnyLogic Cloud API key

Only needed for uploading models to AnyLogic Cloud. Add to `.mcp.json`:

```json
"env": {
  "ALP_OUTPUT_DIR": "...",
  "ANYLOGIC_API_KEY": "your_key_here"
}
```

Get a key at: https://cloud.anylogic.com/settings/api-keys
