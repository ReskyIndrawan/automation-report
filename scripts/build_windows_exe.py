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

def build_executable(debug=False):
    """Build the Windows executable"""
    print("Building Windows executable...")
    if debug:
        print("DEBUG MODE: Building with console window for debugging")

    # Create build directory
    build_dir = Path("build")
    dist_dir = Path("dist")

    # Clean previous builds
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    # Check if main source file exists
    main_file = Path("src/report_automation/gui/gui_app.py")
    if not main_file.exists():
        print(f"Error: Main source file not found: {main_file}")
        return False

    # Check if src directory exists
    src_dir = Path("src")
    if not src_dir.exists():
        print(f"Error: Source directory not found: {src_dir}")
        return False

    # PyInstaller command with better error handling
    cmd = [
        "pyinstaller",
        "--clean",
        "--log-level=INFO",
        "--name=ReportAutomation",
        "--windowed" if not debug else "",  # Console window if debug mode
        "--onefile",   # Single executable file
        "--add-data=src;src",
        "--paths=src",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=openpyxl.utils",
        "--hidden-import=openpyxl.utils.dataframe",
        "--hidden-import=openpyxl.styles",
        "--hidden-import=openpyxl.styles.font",
        "--hidden-import=openpyxl.styles.colors",
        "--hidden-import=openpyxl.styles.borders",
        "--hidden-import=openpyxl.styles.alignment",
        "--hidden-import=openpyxl.styles.patternfill",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.font",
        "--hidden-import=src.report_automation",
        "--hidden-import=src.report_automation.core",
        "--hidden-import=src.report_automation.gui",
        "--collect-all=openpyxl",
        "--collect-all=src.report_automation",
        "--icon=NONE",  # You can add an icon file later
        str(main_file)
    ]

    try:
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        # Verify executable was created
        exe_file = Path("dist/ReportAutomation.exe")
        if exe_file.exists():
            print(f"Executable created successfully: {exe_file}")
            print(f"File size: {exe_file.stat().st_size} bytes")
        else:
            print("Error: Executable was not created in dist directory")
            return False

        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with return code: {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)

        # Check for PyInstaller logs
        log_files = list(Path(".").glob("*.log"))
        if log_files:
            print("PyInstaller log files:")
            for log_file in log_files:
                print(f"  {log_file}:")
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        print(f.read())
                except Exception as log_e:
                    print(f"    Could not read log file: {log_e}")

        return False
    except Exception as e:
        print(f"Unexpected error during build: {e}")
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

    # Parse command line arguments
    debug_mode = "--debug" in sys.argv

    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")

    # Check if we're on Windows
    if sys.platform != "win32":
        print("Warning: This script is designed for Windows. Building on other platforms may not work.")

    # Install PyInstaller
    if not install_pyinstaller():
        print("Failed to install PyInstaller. Please install it manually:")
        print("pip install pyinstaller")
        return 1

    # Build executable
    if not build_executable(debug=debug_mode):
        print("Failed to build executable")
        return 1

    # Create installer
    create_installer()

    print("\nBuild completed successfully!")
    print("Executable location: dist/ReportAutomation.exe")
    if debug_mode:
        print("DEBUG version created with console window")
    print("Run install.bat to copy to desktop")

    if debug_mode:
        print("\nTo run in debug mode:")
        print("  dist/ReportAutomation.exe")
        print("  (This will show console output for debugging)")

    return 0

if __name__ == "__main__":
    sys.exit(main())