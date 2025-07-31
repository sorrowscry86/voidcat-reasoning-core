# Setting Up MCP Servers on Windows
A step-by-step guide to setting up Model Context Protocol (MCP) servers for Claude Desktop on Windows.

## Prerequisites
1. Install Node.js (v18.x or later)
   - Download from: https://nodejs.org/
   - Verify installation by opening Command Prompt (CMD) and running:
     ```cmd
     node --version
     npm --version
     where node
     npm root -g
     ```
   - Note down the paths returned by the last two commands - you'll need them later

2. Install Python 3.10 or later (for Python-based servers)
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

## Installation Steps

### 1. Install Package Managers
Open Command Prompt (CMD) as administrator and run:
```cmd
# For Python-based servers
npm install -g uv
```

### 2. Install MCP Servers
You have multiple options for installing and configuring servers:

#### Option A: Global NPM Installation (Recommended for getting started)
```cmd
# Install core servers globally
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-brave-search
```

#### Option B: Using NPX (Alternative for package-managed servers)
Some servers can be run directly through npx without global installation:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\YourUsername\\Downloads",
        "C:\\Users\\YourUsername\\Documents"
      ]
    }
  }
}
```

#### Option C: Local Development Setup
For locally developed or modified servers, point directly to their dist files:
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "node",
      "args": ["C:\\Users\\YourUsername\\Dev\\servers\\src\\sequentialthinking\\dist\\index.js"],
      "env": {
        "DEBUG": "*"
      }
    }
  }
}
```

### Python-based Servers

Some MCP servers are Python-based and require different installation steps. Here's how to set them up:

#### Fetch Server
```cmd
# Install the fetch server using pip
pip install mcp-server-fetch

# Configure in claude_desktop_config.json:
{
  "mcpServers": {
    "fetch": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server_fetch"
      ],
      "env": {
        "DEBUG": "*"
      }
    }
  }
}
```

The fetch server provides web content fetching capabilities and converts HTML to markdown for easier consumption by LLMs. It requires Python 3.10 or later.

### 3. Configure Claude Desktop

1. Navigate to: `%AppData%\Claude Desktop\`
2. Create or edit `claude_desktop_config.json`
3. Use this configuration structure (replace paths with your actual Node.js and npm paths):

```json
{
  "globalShortcut": "Ctrl+Space",
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "C:\\Users\\YourUsername\\test.db"]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\YourUsername\\Downloads",
        "C:\\Users\\YourUsername\\Documents",
        "C:\\Users\\YourUsername\\Desktop"
      ],
      "env": {
        "DEBUG": "*"
      }
    },
    "memory": {
      "command": "C:\\Program Files\\nodejs\\node.exe",
      "args": [
        "C:\\Users\\YourUsername\\AppData\\Roaming\\npm\\node_modules\\@modelcontextprotocol\\server-memory\\dist\\index.js"
      ],
      "env": {
        "DEBUG": "*"
      }
    },
    "mcp-installer": {
      "command": "npx",
      "args": [
        "@anaisbetts/mcp-installer"
      ]
    }
  }
}
```

**Important Notes:**
- Replace `YourUsername` with your Windows username
- For npx-based installations, the `-y` flag automatically accepts installation prompts
- Local development paths should point to the compiled `dist/index.js` files
- The `DEBUG` environment variable helps with troubleshooting
- You can mix and match installation methods based on your needs:
  - Use npx for quick testing or occasional use
  - Use global installations for better performance
  - Use local paths for development or customized versions

## Verification & Troubleshooting

### Verify Installations
```cmd
# List installed packages
npm list -g --depth=0

# Test individual servers directly
node C:\Users\YourUsername\AppData\Roaming\npm\node_modules\@modelcontextprotocol\server-memory\dist\index.js
```

### Common Issues
1. "Could not attach to MCP server"
   - Verify all paths in config match your system exactly
   - Make sure all packages are installed globally (-g flag)
   - Test servers directly using the node command as shown above
   - Run Claude Desktop as administrator

2. PowerShell Security Errors
   - Use Command Prompt (CMD) instead
   - Or run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell as admin

3. Server not showing in Claude
   - Ensure you have Claude Desktop Pro subscription
   - Make sure you have the latest Claude Desktop version
   - Look for the MCP icon in the interface
   - Restart Claude Desktop after configuration changes
   - Verify JSON syntax in config file

## Tips
- Always use global installations (`npm install -g`)
- Use absolute paths to both Node.js and server files
- Keep DEBUG env variable for troubleshooting
- Restart Claude Desktop after config changes
- Run Claude Desktop as administrator when testing new configurations