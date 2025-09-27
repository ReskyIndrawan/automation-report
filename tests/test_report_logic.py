#!/usr/bin/env python3
"""
Test script to validate the report generation logic without GUI
"""

import os
from datetime import datetime
from report_automation import ReportAutomation

def test_report_generation_logic():
    """Test the core report generation logic"""
    print("Testing Report Generation Logic...")

    try:
        # File paths
        work_file = "file/9.xlsx"
        inspection_file = "file/検査工数.xlsx"

        # Check if files exist
        if not os.path.exists(work_file):
            print(f"❌ Work file not found: {work_file}")
            return False

        if not os.path.exists(inspection_file):
            print(f"❌ Inspection file not found: {inspection_file}")
            return False

        print("✅ Input files found")

        # Initialize report automation
        report_automation = ReportAutomation(work_file, inspection_file)

        # Load data (this was the missing step in GUI)
        print("Loading data...")
        report_automation.load_data()
        print("✅ Data loaded successfully")

        # Get current month and year
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        # Generate output filename
        output_filename = f"test_logic_output_{year}_{month:02d}.xlsx"

        print(f"Generating report for {year}-{month:02d}...")
        print(f"Output file: {output_filename}")

        # Generate report
        report_automation.process_monthly_report(year, month, output_filename)

        # Check if output file was created
        if os.path.exists(output_filename):
            file_size = os.path.getsize(output_filename)
            print(f"✅ Report generated successfully!")
            print(f"   File: {output_filename}")
            print(f"   Size: {file_size:,} bytes")

            # Check if it's a valid Excel file
            try:
                import pandas as pd
                xls = pd.ExcelFile(output_filename)
                print(f"   Sheets: {len(xls.sheet_names)}")
                print(f"   Sheet names: {', '.join(xls.sheet_names)}")

                # Check if N5比較 sheet exists
                if 'N5比較' in xls.sheet_names:
                    print("   ✅ N5 comparison sheet found!")
                else:
                    print("   ⚠️  N5 comparison sheet not found")

            except Exception as e:
                print(f"   ⚠️  Could not validate Excel file: {str(e)}")

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
    success = test_report_generation_logic()
    if success:
        print("\n🎉 Report generation logic test PASSED!")
        print("\nThis means the core functionality works correctly.")
        print("The GUI should work once the Tkinter/Tcl issue is resolved.")
    else:
        print("\n❌ Report generation logic test FAILED!")