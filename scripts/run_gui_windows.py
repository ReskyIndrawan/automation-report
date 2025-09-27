#!/usr/bin/env python3
"""
Windows-compatible GUI Launcher for Report Automation
Handles Windows-specific issues and provides better error handling
"""

import sys
import os
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def show_error_dialog(title, message):
    """Show error dialog using Windows MessageBox"""
    try:
        import ctypes
        MB_OK = 0x00000000
        MB_ICONERROR = 0x00000010
        ctypes.windll.user32.MessageBoxW(None, message, title, MB_OK | MB_ICONERROR)
    except:
        print(f"{title}: {message}")

def main():
    """Main function for Windows GUI"""
    try:
        print("Starting Report Automation GUI...")

        # Try to import and run GUI
        from src.report_automation.gui.gui_app import main as gui_main
        gui_main()

    except ImportError as e:
        error_msg = f"Import error: {e}\n\n{traceback.format_exc()}"
        print(error_msg)
        show_error_dialog("Import Error", f"Failed to import GUI components:\n{str(e)}")

        # Fallback to CLI
        try:
            print("Trying CLI alternative...")
            from src.report_automation.gui.simple_generate import simple_generate
            simple_generate()
        except ImportError as e2:
            error_msg = f"CLI fallback failed: {e2}\n\n{traceback.format_exc()}"
            print(error_msg)
            show_error_dialog("Fatal Error", f"Failed to start application:\n{str(e2)}")
            return 1

    except Exception as e:
        error_msg = f"GUI failed: {e}\n\n{traceback.format_exc()}"
        print(error_msg)
        show_error_dialog("Application Error", f"Application failed to start:\n{str(e)}")

        # Fallback to CLI
        try:
            print("Trying CLI alternative...")
            from src.report_automation.gui.simple_generate import simple_generate
            simple_generate()
        except Exception as e2:
            error_msg = f"CLI fallback failed: {e2}\n\n{traceback.format_exc()}"
            print(error_msg)
            show_error_dialog("Fatal Error", f"Failed to start application:\n{str(e2)}")
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())