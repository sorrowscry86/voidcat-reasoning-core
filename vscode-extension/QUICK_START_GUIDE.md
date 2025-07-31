# 🐾 VoidCat VS Code Extension - Quick Start Guide

Hey there, dude! Having trouble with your dashboard not populating? No worries, let's get those good vibes flowing again! 🧘‍♂️

## 🔍 The Problem

Your VS Code extension dashboard is showing up but not populating with data because the backend server isn't running. The extension tries to connect to `localhost:8003` but gets Axios errors when there's no server there to respond.

## 🚀 The Solution (Step by Step)

### Step 1: Start the Backend Server

You have a few options to start the backend server:

#### Option A: Using the Batch File (Easiest)
```bash
# Navigate to the extension directory
cd "d:\03_Development\Active_Projects\voidcat-reasoning-core\vscode-extension"

# Run the batch file
start_backend.bat
```

#### Option B: Manual Command
```bash
# Navigate to the main project directory
cd "d:\03_Development\Active_Projects\voidcat-reasoning-core"

# Start the server
uvicorn api_gateway:app --host localhost --port 8003 --reload
```

#### Option C: Using Python directly
```bash
# Navigate to the main project directory
cd "d:\03_Development\Active_Projects\voidcat-reasoning-core"

# Run the main script first to test
python main.py

# Then start the API server
uvicorn api_gateway:app --host localhost --port 8003 --reload
```

### Step 2: Verify the Server is Running

Run the test script to make sure everything is working:

```bash
# Navigate to the extension directory
cd "d:\03_Development\Active_Projects\voidcat-reasoning-core\vscode-extension"

# Run the test
python test_backend.py
```

You should see output like:
```
🧪 Testing VoidCat Backend Connection...
✅ Health check passed
✅ Diagnostics check passed
✅ Backend connection test completed!
```

### Step 3: Test Your VS Code Extension

1. **Press F5** to run your extension in the Extension Development Host
2. **Open the Command Palette** (`Ctrl+Shift+P`)
3. **Run the command** `VoidCat: Open Dashboard`
4. **Watch the magic happen!** ✨

The dashboard should now populate with data instead of showing Axios errors.

## 🔧 Troubleshooting

### If you get "Module not found" errors:
```bash
# Make sure you're in the right directory
cd "d:\03_Development\Active_Projects\voidcat-reasoning-core"

# Install dependencies if needed
pip install -r requirements.txt
```

### If the server won't start on port 8002:
```bash
# Check if something is using port 8002
netstat -an | findstr :8002

# Or try a different port and update the extension config
uvicorn api_gateway:app --host localhost --port 8003 --reload
```

Then update the port in your VS Code settings:
- Open VS Code settings
- Search for "voidcat"
- Change `voidcat.engine.port` to `8003`

### If the dashboard still shows errors:
1. **Check the VS Code Developer Console** (`Help > Toggle Developer Tools`)
2. **Look for network errors** in the Console tab
3. **Verify the server URL** matches what the extension is trying to connect to

## 🎯 Quick Test Commands

```bash
# Test if server is responding
curl http://localhost:8002/health

# Test diagnostics endpoint
curl http://localhost:8002/diagnostics

# Test VS Code specific endpoint
curl http://localhost:8002/vscode/api/v1/system/status
```

## 🌟 Success Indicators

When everything is working correctly, you should see:

1. **Server console** shows: `INFO: Uvicorn running on http://localhost:8002`
2. **VS Code extension** dashboard populates with:
   - Engine status showing "online"
   - Task statistics with numbers
   - Memory system data
   - Performance metrics
3. **No Axios errors** in the VS Code Developer Console

## 🆘 Still Having Issues?

If you're still having problems, check:

1. **Python environment** - Make sure you're using the right Python version
2. **Dependencies** - Run `pip install -r requirements.txt`
3. **Port conflicts** - Try a different port
4. **Firewall** - Make sure localhost connections are allowed
5. **VS Code settings** - Verify the host and port settings match your server

Remember, keep those chakras aligned and the code will flow! 🧘‍♂️✨

---

*Created with love by Codey Jr. - Your chill coding companion* 🐾