#!/usr/bin/env python3
"""
Simple command line report generator
Alternative to GUI when Tkinter has issues
"""

import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.report_automation.core.report_automation import ReportAutomation

def simple_generate():
    """Simple report generation without GUI"""
    print("=" * 60)
    print("SIMPLE REPORT GENERATOR")
    print("=" * 60)

    # File paths
    work_file = "data/9.xlsx"
    inspection_file = "data/検査工数.xlsx"

    # Check if files exist
    if not os.path.exists(work_file):
        print(f"❌ Error: Work file not found: {work_file}")
        return

    if not os.path.exists(inspection_file):
        print(f"❌ Error: Inspection file not found: {inspection_file}")
        return

    print(f"✅ Work file: {work_file}")
    print(f"✅ Inspection file: {inspection_file}")

    # Get output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        current_date = datetime.now()
        output_file = f"data/output/月次報告書_{current_date.year}_{current_date.month:02d}.xlsx"

    # Create output directory
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"📁 Output file: {output_file}")

    try:
        # Initialize and run report automation
        print("🔄 Loading data...")
        report_automation = ReportAutomation(work_file, inspection_file)
        report_automation.load_data()

        # Get current month and year
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        print(f"🔄 Generating report for {year}-{month:02d}...")

        # Generate report
        report_automation.process_monthly_report(year, month, output_file)

        # Check results
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"\n✅ SUCCESS! Report generated successfully!")
            print(f"   📄 File: {output_file}")
            print(f"   📏 Size: {file_size:,} bytes")

            # Show sheet info
            try:
                import pandas as pd
                xls = pd.ExcelFile(output_file)
                print(f"   📋 Sheets: {len(xls.sheet_names)}")
                print(f"   📑 Sheet names: {', '.join(xls.sheet_names)}")

                # Show N5 comparison stats if available
                if 'N5比較' in xls.sheet_names:
                    n5_data = pd.read_excel(output_file, sheet_name='N5比較')
                    if not n5_data.empty:
                        print(f"   📊 N5 comparison records: {len(n5_data)}")
                        print(f"   ⏱️  Average N5 time: {n5_data['分N5'].mean():.2f} min")
                        print(f"   ⏱️  Average actual time: {n5_data['分N1'].mean():.2f} min")
                        print(f"   📈 Average difference: {n5_data['差分'].mean():.2f} min")
                        print(f"   💰 Total N5 time: {n5_data['分N5'].sum():.0f} min")
                        print(f"   💰 Total actual time: {n5_data['分N1'].sum():.0f} min")
                        print(f"   📉 Total difference: {n5_data['差分'].sum():.0f} min")

                        # Calculate efficiency
                        total_n5 = n5_data['分N5'].sum()
                        total_n1 = n5_data['分N1'].sum()
                        if total_n5 > 0:
                            efficiency = (total_n1 / total_n5 * 100)
                            reduction = 100 - efficiency
                            print(f"   📈 Efficiency: {efficiency:.2f}%")
                            print(f"   📉 Reduction: {reduction:.2f}%")

                # Show report summary if available
                if '報告サマリー' in xls.sheet_names:
                    print(f"   📋 Report summary sheet generated!")

            except Exception as e:
                print(f"   ⚠️  Could not read sheet details: {str(e)}")

        else:
            print(f"❌ Error: Output file not created: {output_file}")

    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)

def main():
    """Main function for CLI entry point"""
    simple_generate()

if __name__ == "__main__":
    main()