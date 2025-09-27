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
