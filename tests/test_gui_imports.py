#!/usr/bin/env python3
"""
Test script to validate GUI imports and basic functionality
"""

def test_gui_imports():
    """Test if GUI imports work correctly"""
    try:
        import tkinter as tk
        print("✅ tkinter import successful")

        from tkinter import ttk, filedialog, messagebox
        print("✅ tkinter submodules import successful")

        import pandas as pd
        print("✅ pandas import successful")

        from report_automation import ReportAutomation
        print("✅ ReportAutomation import successful")

        # Test creating a root window (without showing it)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        print("✅ Tkinter root window created successfully")

        # Test basic GUI components
        frame = ttk.Frame(root)
        label = ttk.Label(frame, text="Test")
        button = ttk.Button(frame, text="Test Button")
        print("✅ GUI components created successfully")

        root.destroy()
        print("✅ Test completed successfully")

        return True

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_gui_imports()