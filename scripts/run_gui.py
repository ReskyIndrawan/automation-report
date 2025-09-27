#!/usr/bin/env python3
"""
GUI Launcher for Report Automation
Safe runner with fallback to CLI if GUI fails
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.report_automation.gui.gui_app import main as gui_main
    gui_main()
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔄 Trying CLI alternative...")

    # Fallback to CLI
    try:
        from src.report_automation.gui.simple_generate import simple_generate
        simple_generate()
    except ImportError as e2:
        print(f"❌ CLI fallback also failed: {e2}")
        sys.exit(1)
except Exception as e:
    print(f"❌ GUI failed: {e}")
    print("🔄 Trying CLI alternative...")

    # Fallback to CLI
    try:
        from src.report_automation.gui.simple_generate import simple_generate
        simple_generate()
    except Exception as e2:
        print(f"❌ CLI fallback also failed: {e2}")
        sys.exit(1)

def main():
    """Main function for GUI entry point"""
    # Re-execute this script to ensure proper path setup
    import subprocess
    import sys
    script_path = os.path.abspath(__file__)
    result = subprocess.run([sys.executable, script_path])
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()