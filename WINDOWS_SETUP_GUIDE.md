# VoidCat Reasoning Core - Windows Setup Guide

## Enhanced Windows Integration Setup

This guide covers the enhanced Windows integration for the VoidCat Reasoning Core MCP server.

### 🚀 Quick Setup

1. **Enhanced MCP Launcher**: `enhanced_mcp_launcher.bat`
   - Automated dependency checking
   - Console color support
   - Enhanced error handling
   - Windows-specific optimizations

2. **Windows Compatibility Module**: `windows_compat.py`
   - Path normalization for Windows
   - Console color support
   - Process management utilities
   - File system operations

3. **MCP Server Integration**: `mcp_server_windows_integration.py`
   - Windows-specific MCP tools
   - Enhanced environment handling
   - Seamless integration with Claude Desktop

### 📁 Files Created

- `enhanced_mcp_launcher.bat` - Enhanced Windows launcher
- `windows_compat.py` - Windows compatibility module  
- `mcp_server_windows_integration.py` - MCP Windows integration
- `.env.example` - Environment configuration template

### ⚙️ Configuration

Your Claude Desktop config has been updated to use:

```json
"voidcat-reasoning-core": {
  "command": "cmd",
  "args": ["/C", "D:\\03_Development\\Active_Projects\\voidcat-reasoning-core\\enhanced_mcp_launcher.bat"],
  "enabled": true,
  "env": {
    "OPENAI_API_KEY": "your-api-key",
    "DEEPSEEK_API_KEY": "your-deepseek-key"
  }
}
```

### 🔧 Usage

1. **Restart Claude Desktop** to apply the new configuration
2. **Test the connection** by asking: "Can you check the VoidCat reasoning engine status?"
3. **Verify tools** - You should see 15+ VoidCat tools available

### 🛠️ Troubleshooting

**Windows Asyncio Warnings**: These are normal and harmless:
```
OSError: [WinError 6] The handle is invalid
AttributeError: '_ProactorReadPipeTransport' object has no attribute '_empty_waiter'
```

**Key Success Messages**:
```
[VoidCat-Debug] 🚀 VoidCat MCP Server starting...
[VoidCat-Debug] 📡 Listening for MCP requests...
```

### ✨ Features

- **Automatic dependency checking and installation**
- **Enhanced error handling and logging**
- **Windows-specific path normalization**
- **Console color support for better readability**
- **Robust environment variable handling**
- **Seamless Claude Desktop integration**

### 🎯 Next Steps

Your VoidCat Reasoning Core is now ready with enhanced Windows compatibility! The asyncio warnings are harmless - the server is functioning perfectly.

**Ready to use your enhanced AI reasoning capabilities!** 🧠✨
