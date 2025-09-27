#!/usr/bin/env python3
"""
Test script to validate GUI report generation functionality
"""

import os
from datetime import datetime
from gui_app import ReportAutomationGUI

def test_gui_generate_report():
    """Test GUI report generation without actually showing GUI"""
    print("Testing GUI Report Generation...")

    try:
        # Create a dummy root window (hidden)
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide window

        # Create GUI instance
        app = ReportAutomationGUI(root)

        # Set file paths
        app.work_file_path.set("file/9.xlsx")
        app.inspection_file_path.set("file/検査工数.xlsx")

        # Set output filename
        current_date = datetime.now()
        output_filename = f"test_gui_output_{current_date.year}_{current_date.month:02d}.xlsx"
        app.output_file_path.set(output_filename)

        print(f"Work file: {app.work_file_path.get()}")
        print(f"Inspection file: {app.inspection_file_path.get()}")
        print(f"Output file: {app.output_file_path.get()}")

        # Check if files exist
        if not os.path.exists(app.work_file_path.get()):
            print(f"❌ Work file not found: {app.work_file_path.get()}")
            return False

        if not os.path.exists(app.inspection_file_path.get()):
            print(f"❌ Inspection file not found: {app.inspection_file_path.get()}")
            return False

        print("✅ Input files found")

        # Test loading data
        print("Loading data...")
        app.load_data()

        if app.work_data is None or app.inspection_data is None:
            print("❌ Failed to load data")
            return False

        print(f"✅ Data loaded successfully")
        print(f"   Work data: {len(app.work_data)} records")
        print(f"   Inspection data: {len(app.inspection_data)} sheets")

        # Test generate report
        print("Generating report...")
        app.generate_report()

        # Wait a moment for generation (simulating GUI behavior)
        import time
        time.sleep(2)

        # Check if output file was created
        if os.path.exists(output_filename):
            file_size = os.path.getsize(output_filename)
            print(f"✅ Report generated successfully!")
            print(f"   File: {output_filename}")
            print(f"   Size: {file_size:,} bytes")

            # Clean up test file
            os.remove(output_filename)
            print("   Test file cleaned up")
            return True
        else:
            print(f"❌ Output file not created: {output_filename}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_generate_report()
    if success:
        print("\n🎉 GUI report generation test PASSED!")
    else:
        print("\n❌ GUI report generation test FAILED!")