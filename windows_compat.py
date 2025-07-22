"""
VoidCat Reasoning Core - Windows Compatibility Module
====================================================

This module provides Windows-specific compatibility functions and utilities
to ensure smooth operation of the VoidCat MCP server on Windows systems.

Features:
- Path normalization for Windows paths
- Console color support for Windows terminals
- Process management utilities for Windows
- File system operations with Windows compatibility
- Environment variable handling for Windows

Author: VoidCat Reasoning Core Team
License: MIT
Version: 1.0.0
"""

import ctypes
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Check if running on Windows
IS_WINDOWS = platform.system().lower() == "windows"

# Windows console color constants
ENABLE_PROCESSED_OUTPUT = 0x0001
ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
STD_OUTPUT_HANDLE = -11


class WindowsConsoleColors:
    """Windows console color support."""

    @staticmethod
    def enable_vt100():
        """Enable VT100 escape sequences for Windows console."""
        if not IS_WINDOWS:
            return True

        kernel32 = ctypes.windll.kernel32
        stdout_handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

        # Get current console mode
        mode = ctypes.c_ulong()
        if not kernel32.GetConsoleMode(stdout_handle, ctypes.byref(mode)):
            return False

        # Enable VIRTUAL_TERMINAL_PROCESSING flag
        mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING

        # Set the new console mode
        if not kernel32.SetConsoleMode(stdout_handle, mode):
            return False

        return True


class WindowsPathHandler:
    """Windows path handling utilities."""

    @staticmethod
    def normalize_path(path: Union[str, Path]) -> str:
        """
        Normalize a path for Windows compatibility.

        Args:
            path: The path to normalize

        Returns:
            Normalized path string
        """
        if not IS_WINDOWS:
            return str(path)

        # Convert to Path object
        path_obj = Path(path)

        # Resolve to absolute path
        abs_path = path_obj.resolve()

        # Convert to string with forward slashes
        return str(abs_path).replace("\\", "/")

    @staticmethod
    def convert_to_posix_path(windows_path: str) -> str:
        """
        Convert a Windows path to a POSIX-compatible path.

        Args:
            windows_path: Windows-style path

        Returns:
            POSIX-compatible path
        """
        if not IS_WINDOWS:
            return windows_path

        # Replace backslashes with forward slashes
        posix_path = windows_path.replace("\\", "/")

        # Handle drive letters (C: -> /c)
        if len(posix_path) >= 2 and posix_path[1] == ":":
            drive_letter = posix_path[0].lower()
            posix_path = f"/{drive_letter}{posix_path[2:]}"

        return posix_path

    @staticmethod
    def convert_to_windows_path(posix_path: str) -> str:
        """
        Convert a POSIX path to a Windows-compatible path.

        Args:
            posix_path: POSIX-style path

        Returns:
            Windows-compatible path
        """
        if not IS_WINDOWS:
            return posix_path

        # Handle /c/ style paths
        if posix_path.startswith("/") and len(posix_path) >= 3 and posix_path[2] == "/":
            drive_letter = posix_path[1].upper()
            windows_path = f"{drive_letter}:{posix_path[2:]}"
        else:
            windows_path = posix_path

        # Replace forward slashes with backslashes
        windows_path = windows_path.replace("/", "\\")

        return windows_path


class WindowsProcessManager:
    """Windows process management utilities."""

    @staticmethod
    def run_command(
        command: Union[str, List[str]],
        shell: bool = False,
        capture_output: bool = True,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, str, str]:
        """
        Run a command with Windows compatibility.

        Args:
            command: Command to run (string or list)
            shell: Whether to run in shell
            capture_output: Whether to capture stdout/stderr
            cwd: Working directory
            env: Environment variables

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        if isinstance(command, list) and IS_WINDOWS and not shell:
            # Ensure the command is properly quoted for Windows
            command = [str(arg) for arg in command]

        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=capture_output,
                text=True,
                cwd=cwd,
                env=env,
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)


class WindowsEnvironment:
    """Windows environment variable handling."""

    @staticmethod
    def get_appdata_path() -> str:
        """
        Get the Windows AppData path.

        Returns:
            Path to AppData directory
        """
        if IS_WINDOWS:
            return os.environ.get("APPDATA", "")
        return ""

    @staticmethod
    def get_localappdata_path() -> str:
        """
        Get the Windows LocalAppData path.

        Returns:
            Path to LocalAppData directory
        """
        if IS_WINDOWS:
            return os.environ.get("LOCALAPPDATA", "")
        return ""

    @staticmethod
    def get_temp_path() -> str:
        """
        Get the Windows temp directory path.

        Returns:
            Path to temp directory
        """
        if IS_WINDOWS:
            return os.environ.get("TEMP", "")
        return "/tmp"


class WindowsFileSystem:
    """Windows file system operations."""

    @staticmethod
    def create_junction(source: str, target: str) -> bool:
        """
        Create a Windows junction point (similar to symlink).

        Args:
            source: Source path
            target: Target path

        Returns:
            Success status
        """
        if not IS_WINDOWS:
            # Fall back to symlink on non-Windows
            try:
                os.symlink(target, source)
                return True
            except:
                return False

        try:
            # Use mklink /J for junction
            cmd = f'mklink /J "{source}" "{target}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False


# Initialize Windows console colors on module import
if IS_WINDOWS:
    WindowsConsoleColors.enable_vt100()


def setup_windows_compatibility():
    """
    Set up Windows compatibility features.

    This function should be called at the start of the application
    to ensure proper Windows compatibility.
    """
    if not IS_WINDOWS:
        return

    # Enable console colors
    WindowsConsoleColors.enable_vt100()

    # Set up environment variables
    os.environ["VOIDCAT_WINDOWS_COMPAT"] = "true"

    # Ensure temp directory exists
    temp_dir = WindowsEnvironment.get_temp_path()
    if temp_dir and not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir, exist_ok=True)
        except:
            pass


def is_windows_compatible() -> bool:
    """
    Check if the current environment is Windows-compatible.

    Returns:
        True if Windows-compatible, False otherwise
    """
    return IS_WINDOWS or os.environ.get("VOIDCAT_WINDOWS_COMPAT", "").lower() == "true"


# Convenience functions
normalize_path = WindowsPathHandler.normalize_path
to_posix_path = WindowsPathHandler.convert_to_posix_path
to_windows_path = WindowsPathHandler.convert_to_windows_path
run_command = WindowsProcessManager.run_command
get_appdata_path = WindowsEnvironment.get_appdata_path
get_localappdata_path = WindowsEnvironment.get_localappdata_path
get_temp_path = WindowsEnvironment.get_temp_path
