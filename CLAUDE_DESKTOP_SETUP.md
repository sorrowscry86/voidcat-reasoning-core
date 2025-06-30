# 🔧 Claude Desktop Configuration Guide

## Adding VoidCat Reasoning Core to Claude Desktop

### Step 1: Locate Your Claude Desktop Configuration

**Windows Configuration Path:**

```text
C:\Users\[YourUsername]\AppData\Roaming\Claude\claude_desktop_config.json
```

### Step 2: Edit the Configuration File

1. **Open the configuration file** in your preferred text editor (e.g., VS Code, Notepad++)
2. **Add the VoidCat server configuration** to the `mcpServers` section

### Step 3: Complete Configuration

If the file doesn't exist or is empty, create it with this content:

```json
{
    "mcpServers": {
        "voidcat-reasoning-core": {
            "command": "python",
            "args": [
                "P:\\voidcat-reasoning-core\\mcp_server.py"
            ],
            "env": {
                "OPENAI_API_KEY": "your-openai-api-key-here",
                "PYTHONPATH": "P:\\voidcat-reasoning-core"
            }
        }
    }
}
```

**If you already have other MCP servers configured**, add the VoidCat server to the existing `mcpServers` object:

```json
{
    "mcpServers": {
        "existing-server": {
            "command": "...",
            "args": ["..."]
        },
        "voidcat-reasoning-core": {
            "command": "python",
            "args": [
                "P:\\voidcat-reasoning-core\\mcp_server.py"
            ],
            "env": {
                "OPENAI_API_KEY": "your-openai-api-key-here",
                "PYTHONPATH": "P:\\voidcat-reasoning-core"
            }
        }
    }
}
```

### Step 4: Set Your OpenAI API Key

Replace `"your-openai-api-key-here"` with your actual OpenAI API key.

#### Alternative: Environment Variable

You can also set the API key as a system environment variable:

1. Open System Properties → Advanced → Environment Variables
2. Add a new user variable: `OPENAI_API_KEY` = `your-actual-api-key`
3. Remove the `"OPENAI_API_KEY"` line from the configuration

### Step 5: Verify Dependencies

Ensure all required packages are installed in your Python environment:

```powershell
cd "p:\voidcat-reasoning-core"
pip install -r requirements.txt
```

### Step 6: Restart Claude Desktop

After saving the configuration file, completely restart Claude Desktop for the changes to take effect.

### Step 7: Test the Integration

Once Claude Desktop restarts, you should see the VoidCat Reasoning Core tools available. You can test with commands like:

- "Use VoidCat to analyze this data..."
- "Query the VoidCat engine about..."
- "What's the status of the VoidCat system?"

## 🛠️ Available Tools

After successful integration, you'll have access to these VoidCat tools:

### `voidcat_query`

- **Purpose**: Process intelligent queries using RAG-enhanced reasoning
- **Parameters**:
  - `query` (required): Your question or prompt
  - `model` (optional): OpenAI model to use (default: gpt-4o-mini)

### `voidcat_status`

- **Purpose**: Check the health and status of the VoidCat reasoning engine
- **Parameters**: None

## 🔍 Troubleshooting

### Common Issues

1. **Server not starting**: Check that Python can find the mcp_server.py file at the specified path
2. **Path errors ("can't open file")**: 
   - **Symptom**: Error like `python: can't open file 'c:\Users\...\mcp_server.py': [Errno 2] No such file or directory`
   - **Solution**: Use the full absolute path in the configuration instead of relying on `cwd`:
   ```json
   "args": ["P:\\voidcat-reasoning-core\\mcp_server.py"]
   ```
   Instead of:
   ```json
   "cwd": "P:\\voidcat-reasoning-core",
   "args": ["mcp_server.py"]
   ```
3. **API key errors**: Verify your OpenAI API key is correct and has sufficient credits
4. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
5. **Claude Desktop not recognizing changes**: Restart Claude Desktop after modifying the configuration file

### Verification Commands

Test the MCP server manually to ensure it works:

```powershell
# Test with absolute path (recommended)
python "P:\voidcat-reasoning-core\mcp_server.py"

# Should output JSON response indicating server is ready
```

### Debug Mode

To see detailed logs, you can run the MCP server manually:

```powershell
cd "p:\voidcat-reasoning-core"
python mcp_server.py
```

This will show any startup errors or issues.

## 🎯 Next Steps

Once configured, the VoidCat Reasoning Core will be available as a powerful tool within Claude Desktop, providing RAG-enhanced reasoning capabilities for all your queries and analyses.

For more detailed usage examples and advanced configuration options, see the complete [MCP_INTEGRATION.md](MCP_INTEGRATION.md) file.
