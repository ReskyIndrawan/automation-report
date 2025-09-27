#!/usr/bin/env python3
"""
Build Windows Executable
Creates a standalone Windows executable for the Report Automation application
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"],
                          check=True, capture_output=True, text=True)
            print("PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install PyInstaller: {e}")
            return False

def build_executable():
    """Build the Windows executable"""
    print("Building Windows executable...")

    # Create build directory
    build_dir = Path("build")
    dist_dir = Path("dist")

    # Clean previous builds
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=ReportAutomation",
        "--windowed",  # No console window for GUI app
        "--onefile",   # Single executable file
        "--add-data=src;src",
        "--add-data=data;data",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=src.report_automation",
        "--collect-all=src.report_automation",
        "--icon=NONE",  # You can add an icon file later
        "scripts/run_gui.py"
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(e.stderr)
        return False

def create_installer():
    """Create a simple installer script"""
    installer_script = """@echo off
echo Installing Report Automation...
echo Creating desktop shortcut...

set TARGET=%USERPROFILE%\\Desktop\\ReportAutomation.exe
set SOURCE=%CD%\\dist\\ReportAutomation.exe

copy "%SOURCE%" "%TARGET%"
echo Installation complete!
echo You can now run ReportAutomation from your desktop.
pause
"""

    with open("install.bat", "w") as f:
        f.write(installer_script)

    print("Created install.bat for easy installation")

def main():
    """Main build function"""
    print("Report Automation - Windows Executable Builder")
    print("=" * 50)

    # Check if we're on Windows
    if sys.platform != "win32":
        print("Warning: This script is designed for Windows. Building on other platforms may not work.")

    # Install PyInstaller
    if not install_pyinstaller():
        print("Failed to install PyInstaller. Please install it manually:")
        print("pip install pyinstaller")
        return 1

    # Build executable
    if not build_executable():
        print("Failed to build executable")
        return 1

    # Create installer
    create_installer()

    print("\nBuild completed successfully!")
    print("Executable location: dist/ReportAutomation.exe")
    print("Run install.bat to copy to desktop")

    return 0

if __name__ == "__main__":
    sys.exit(main())