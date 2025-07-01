#!/usr/bin/env python3
"""
🛡️ VoidCat Reasoning Core - Automated Launcher & Management System
================================================================================
Strategic automation for VoidCat RDC deployment with comprehensive diagnostics
and process management.

Author: Albedo, Overseer of the Digital Scriptorium
Master: Lord Wykeve
Version: 1.0-Production
Date: July 1, 2025
================================================================================
"""

import os
import sys
import time
import signal
import psutil
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Ensure we're in the correct directory
VOIDCAT_ROOT = Path(__file__).parent.absolute()
os.chdir(VOIDCAT_ROOT)

# Add the project root to Python path
if str(VOIDCAT_ROOT) not in sys.path:
    sys.path.insert(0, str(VOIDCAT_ROOT))

class VoidCatProcessManager:
    """Strategic process management for VoidCat Reasoning Core."""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.python_exe = VOIDCAT_ROOT / ".venv" / "Scripts" / "python.exe"
        self.is_shutting_down = False
        
        # Ensure virtual environment exists
        if not self.python_exe.exists():
            self._setup_virtual_environment()
    
    def _setup_virtual_environment(self):
        """Initialize virtual environment and install dependencies."""
        print("🔧 Setting up virtual environment...")
        
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        
        # Install dependencies
        requirements_file = VOIDCAT_ROOT / "requirements.txt"
        if requirements_file.exists():
            subprocess.run([
                str(self.python_exe), "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True)
        
        # Install additional dependencies for diagnostics
        additional_deps = [
            "customtkinter", "pystray", "pillow", "requests", "psutil"
        ]
        subprocess.run([
            str(self.python_exe), "-m", "pip", "install"
        ] + additional_deps, check=True)
        
        print("✅ Virtual environment configured successfully")
    
    def find_existing_processes(self) -> List[psutil.Process]:
        """Find any existing VoidCat processes."""
        existing_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('mcp_server.py' in str(cmd) for cmd in cmdline):
                    existing_processes.append(proc)
                elif cmdline and any('diagnostics_widget.py' in str(cmd) for cmd in cmdline):
                    existing_processes.append(proc)
                elif cmdline and any('api_gateway.py' in str(cmd) for cmd in cmdline):
                    existing_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return existing_processes
    
    def terminate_existing_processes(self):
        """Gracefully terminate any existing VoidCat processes."""
        existing = self.find_existing_processes()
        
        if existing:
            print(f"🔄 Found {len(existing)} existing VoidCat processes. Terminating...")
            
            for proc in existing:
                try:
                    print(f"   Terminating PID {proc.pid}: {proc.name()}")
                    proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Wait for graceful shutdown
            time.sleep(2)
            
            # Force kill if necessary
            for proc in existing:
                try:
                    if proc.is_running():
                        print(f"   Force killing PID {proc.pid}")
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print("✅ Existing processes terminated")
    
    def start_mcp_server(self) -> subprocess.Popen:
        """Start the VoidCat MCP server."""
        print("🚀 Starting VoidCat MCP Server...")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = str(VOIDCAT_ROOT)
        env["VOIDCAT_DEBUG"] = "true"
        
        process = subprocess.Popen(
            [str(self.python_exe), "mcp_server.py"],
            cwd=VOIDCAT_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes["mcp_server"] = process
        print(f"✅ MCP Server started (PID: {process.pid})")
        return process
    
    def start_api_gateway(self) -> subprocess.Popen:
        """Start the VoidCat API Gateway."""
        print("🌐 Starting VoidCat API Gateway...")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = str(VOIDCAT_ROOT)
        
        process = subprocess.Popen(
            [str(self.python_exe), "api_gateway.py"],
            cwd=VOIDCAT_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes["api_gateway"] = process
        print(f"✅ API Gateway started (PID: {process.pid})")
        return process
    
    def start_diagnostics_widget(self) -> subprocess.Popen:
        """Start the VoidCat diagnostics widget."""
        print("📊 Starting VoidCat Diagnostics Widget...")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = str(VOIDCAT_ROOT)
        
        process = subprocess.Popen(
            [str(self.python_exe), "diagnostics_widget.py"],
            cwd=VOIDCAT_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes["diagnostics"] = process
        print(f"✅ Diagnostics Widget started (PID: {process.pid})")
        return process
    
    def monitor_processes(self):
        """Monitor running processes and restart if necessary."""
        while not self.is_shutting_down:
            for name, process in list(self.processes.items()):
                if process.poll() is not None:
                    print(f"⚠️ Process {name} (PID: {process.pid}) has stopped")
                    
                    # Restart critical processes
                    if name == "mcp_server":
                        print("🔄 Restarting MCP Server...")
                        self.processes[name] = self.start_mcp_server()
                    elif name == "api_gateway":
                        print("🔄 Restarting API Gateway...")
                        self.processes[name] = self.start_api_gateway()
                    # Don't auto-restart diagnostics widget (user may have closed it)
            
            time.sleep(5)
    
    def shutdown_all(self):
        """Gracefully shutdown all processes."""
        print("\n🛑 Initiating VoidCat system shutdown...")
        self.is_shutting_down = True
        
        for name, process in self.processes.items():
            try:
                print(f"   Stopping {name} (PID: {process.pid})")
                process.terminate()
            except:
                pass
        
        # Wait for graceful shutdown
        time.sleep(3)
        
        # Force kill if necessary
        for name, process in self.processes.items():
            try:
                if process.poll() is None:
                    print(f"   Force killing {name}")
                    process.kill()
            except:
                pass
        
        print("✅ VoidCat system shutdown complete")


class VoidCatLauncher:
    """Main launcher orchestrating the VoidCat Reasoning Core ecosystem."""
    
    def __init__(self):
        self.manager = VoidCatProcessManager()
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers."""
        def signal_handler(signum, frame):
            print(f"\n📡 Received signal {signum}")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def validate_environment(self) -> bool:
        """Validate the VoidCat environment and dependencies."""
        print("🔍 Validating VoidCat environment...")
        
        # Check critical files
        critical_files = [
            "mcp_server.py",
            "enhanced_engine.py",
            "api_gateway.py",
            "diagnostics_widget.py",
            "requirements.txt"
        ]
        
        missing_files = []
        for file in critical_files:
            if not (VOIDCAT_ROOT / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing critical files: {', '.join(missing_files)}")
            return False
        
        # Check Python executable
        if not self.manager.python_exe.exists():
            print("❌ Virtual environment not found")
            return False
        
        print("✅ Environment validation successful")
        return True
    
    def display_startup_banner(self):
        """Display the VoidCat startup banner."""
        banner = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    🛡️ VOIDCAT REASONING CORE                     ║
║                  Strategic Intelligence System                   ║
║                                                                  ║
║  Master: Lord Wykeve                                             ║
║  Overseer: Albedo, Guardian of the Digital Scriptorium          ║
║  Status: Production Deployment                                   ║
║  Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}                                   ║
║                                                                  ║
║  🚀 Initializing autonomous operation with strategic excellence  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def launch(self):
        """Launch the complete VoidCat Reasoning Core system."""
        try:
            self.display_startup_banner()
            
            # Validate environment
            if not self.validate_environment():
                print("❌ Environment validation failed. Cannot proceed.")
                return False
            
            # Terminate any existing processes
            self.manager.terminate_existing_processes()
            
            # Start core services
            print("\n🎯 Launching VoidCat Core Services...")
            
            # Start MCP Server (highest priority)
            mcp_server = self.manager.start_mcp_server()
            time.sleep(2)  # Allow MCP server to initialize
            
            # Start API Gateway
            api_gateway = self.manager.start_api_gateway()
            time.sleep(1)
            
            # Start Diagnostics Widget
            diagnostics = self.manager.start_diagnostics_widget()
            time.sleep(1)
            
            print("\n✅ VoidCat Reasoning Core deployment complete!")
            print("\n📊 System Status:")
            print(f"   🔧 MCP Server: Running (PID: {mcp_server.pid})")
            print(f"   🌐 API Gateway: Running (PID: {api_gateway.pid})")
            print(f"   📊 Diagnostics: Running (PID: {diagnostics.pid})")
            
            print("\n🎯 Strategic Intelligence System fully operational")
            print("   - MCP tools available in Claude Desktop")
            print("   - API Gateway accessible at http://localhost:8000")
            print("   - Diagnostics widget monitoring system health")
            
            print("\n🛡️ Autonomous monitoring active. Press Ctrl+C to shutdown.")
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self.manager.monitor_processes,
                daemon=True
            )
            monitor_thread.start()
            
            # Keep main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ VoidCat launch failed: {str(e)}")
            return False
    
    def shutdown(self):
        """Shutdown the VoidCat system."""
        self.manager.shutdown_all()


def main():
    """Main entry point for VoidCat Launcher."""
    launcher = VoidCatLauncher()
    
    try:
        success = launcher.launch()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"💥 Critical error: {str(e)}")
        sys.exit(1)
    finally:
        launcher.shutdown()


if __name__ == "__main__":
    main()
