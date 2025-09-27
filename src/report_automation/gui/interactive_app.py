#!/usr/bin/env python3
"""
Interactive Command Line Application untuk Report Automation
Sesuai dengan requirements di concept.txt
"""

import pandas as pd
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.report_automation.core.report_automation import ReportAutomation
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractiveReportApp:
    def __init__(self):
        self.work_file = "file/9.xlsx"
        self.inspection_file = "file/検査工数.xlsx"
        self.output_dir = "output"

    def display_banner(self):
        """Display application banner"""
        print("=" * 60)
        print("   REPORT AUTOMATION - N5 COMPARISON TOOL")
        print("=" * 60)
        print()

    def display_menu(self):
        """Display main menu"""
        print("Main Menu:")
        print("1. Load and Preview Data")
        print("2. Generate Monthly Report")
        print("3. Custom Report with Date Range")
        print("4. View Data Statistics")
        print("5. Exit")
        print()

    def preview_data(self):
        """Preview data from both files"""
        print("\n" + "=" * 50)
        print("DATA PREVIEW")
        print("=" * 50)

        try:
            # Load work data
            print("\n1. Loading Work Data...")
            work_data = pd.read_excel(self.work_file)
            print(f"   ✓ Work data loaded: {len(work_data)} records")
            print(f"   ✓ Columns: {len(work_data.columns)} columns")

            # Display sample work data
            print("\n   Sample Work Data (first 5 rows):")
            work_sample = work_data[['日付', '社員名', '品目番号', '作業内容', '作業時間']].head()
            print(work_sample.to_string(index=False))

            # Load inspection data
            print("\n2. Loading Inspection Data...")
            xls = pd.ExcelFile(self.inspection_file)
            print(f"   ✓ Inspection data loaded: {len(xls.sheet_names)} sheets")

            # Display N5基準 data
            if 'N5基準' in xls.sheet_names:
                n5_data = pd.read_excel(self.inspection_file, sheet_name='N5基準')
                print(f"   ✓ N5基準 data: {len(n5_data)} records")
                print(f"   ✓ Unique items: {n5_data['品番'].nunique()}")

                print("\n   Sample N5基準 Data (first 5 rows):")
                n5_sample = n5_data[['品番', '分', 'OP']].head()
                print(n5_sample.to_string(index=False))

            # Filter inspection work data
            print("\n3. Filtering Inspection Work Data...")
            if '作業内容' in work_data.columns:
                inspection_work = work_data[
                    work_data['作業内容'] == '検査作業(受入れ・工程内・出荷前)'
                ]
                print(f"   ✓ Inspection work records: {len(inspection_work)}")
                print(f"   ✓ Percentage of total: {len(inspection_work)/len(work_data)*100:.1f}%")

                print("\n   Sample Inspection Work Data:")
                inspection_sample = inspection_work[['日付', '社員名', '品目番号', '作業時間']].head()
                print(inspection_sample.to_string(index=False))

            print("\n" + "=" * 50)
            input("Press Enter to continue...")

        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            input("Press Enter to continue...")

    def generate_monthly_report(self):
        """Generate monthly report"""
        print("\n" + "=" * 50)
        print("GENERATE MONTHLY REPORT")
        print("=" * 50)

        try:
            # Create output directory
            os.makedirs(self.output_dir, exist_ok=True)

            # Initialize report automation
            report_automation = ReportAutomation(self.work_file, self.inspection_file)
            report_automation.load_data()  # Load data first

            # Get current month and year
            current_date = datetime.now()
            year = current_date.year
            month = current_date.month

            # Generate output filename
            output_file = os.path.join(self.output_dir, f"月次報告書_{year}_{month:02d}.xlsx")

            print(f"\nGenerating report for {year}-{month:02d}...")
            print(f"Output file: {output_file}")

            # Generate report
            report_automation.process_monthly_report(year, month, output_file)

            print(f"\n✅ Report generated successfully!")
            print(f"   File: {output_file}")

            # Display report summary
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"   Size: {file_size:,} bytes")

                # Try to read and display summary
                try:
                    xls = pd.ExcelFile(output_file)
                    print(f"   Sheets: {len(xls.sheet_names)}")
                    print(f"   Sheet names: {', '.join(xls.sheet_names)}")
                except:
                    pass

            print("\n" + "=" * 50)
            input("Press Enter to continue...")

        except Exception as e:
            print(f"❌ Error generating report: {str(e)}")
            input("Press Enter to continue...")

    def custom_report(self):
        """Generate custom report with specific date range"""
        print("\n" + "=" * 50)
        print("CUSTOM REPORT GENERATION")
        print("=" * 50)

        try:
            # Get year and month from user
            print("Enter report details:")
            year = int(input("Year (e.g., 2025): "))
            month = int(input("Month (1-12): "))

            if month < 1 or month > 12:
                print("❌ Invalid month. Please enter 1-12.")
                input("Press Enter to continue...")
                return

            # Get custom output filename
            custom_name = input("Output filename (press Enter for default): ").strip()
            if not custom_name:
                custom_name = f"月次報告書_{year}_{month:02d}.xlsx"

            # Create output directory
            os.makedirs(self.output_dir, exist_ok=True)
            output_file = os.path.join(self.output_dir, custom_name)

            print(f"\nGenerating custom report for {year}-{month:02d}...")
            print(f"Output file: {output_file}")

            # Initialize report automation
            report_automation = ReportAutomation(self.work_file, self.inspection_file)

            # Generate report
            report_automation.process_monthly_report(year, month, output_file)

            print(f"\n✅ Custom report generated successfully!")
            print(f"   File: {output_file}")

            print("\n" + "=" * 50)
            input("Press Enter to continue...")

        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"❌ Error generating custom report: {str(e)}")
            input("Press Enter to continue...")

    def view_statistics(self):
        """View data statistics"""
        print("\n" + "=" * 50)
        print("DATA STATISTICS")
        print("=" * 50)

        try:
            # Load work data
            work_data = pd.read_excel(self.work_file)
            print(f"\n1. Work Data Statistics:")
            print(f"   Total records: {len(work_data):,}")
            print(f"   Date range: {work_data['日付'].min()} to {work_data['日付'].max()}")
            print(f"   Unique employees: {work_data['社員名'].nunique()}")
            print(f"   Unique items: {work_data['品目番号'].nunique()}")

            # Work content distribution
            if '作業内容' in work_data.columns:
                print(f"\n2. Work Content Distribution:")
                work_content_counts = work_data['作業内容'].value_counts()
                for content, count in work_content_counts.head(5).items():
                    percentage = count / len(work_data) * 100
                    print(f"   {content}: {count:,} ({percentage:.1f}%)")

            # Load N5 data
            if 'N5基準' in pd.ExcelFile(self.inspection_file).sheet_names:
                n5_data = pd.read_excel(self.inspection_file, sheet_name='N5基準')
                print(f"\n3. N5基準 Statistics:")
                print(f"   Total N5 records: {len(n5_data):,}")
                print(f"   Unique N5 items: {n5_data['品番'].nunique()}")
                print(f"   Average N5 time: {n5_data['分'].mean():.1f} minutes")
                print(f"   N5 time range: {n5_data['分'].min()} - {n5_data['分'].max()} minutes")

                # Operator distribution
                if 'OP' in n5_data.columns:
                    print(f"\n4. N5 Operator Distribution:")
                    op_counts = n5_data['OP'].value_counts()
                    for op, count in op_counts.items():
                        percentage = count / len(n5_data) * 100
                        print(f"   {op}: {count:,} ({percentage:.1f}%)")

            # Time analysis
            if '作業時間' in work_data.columns:
                print(f"\n5. Work Time Analysis:")
                print(f"   Average work time: {work_data['作業時間'].mean():.1f} minutes")
                print(f"   Total work time: {work_data['作業時間'].sum():,.0f} minutes")
                print(f"   Work time range: {work_data['作業時間'].min()} - {work_data['作業時間'].max()} minutes")

            print("\n" + "=" * 50)
            input("Press Enter to continue...")

        except Exception as e:
            print(f"❌ Error generating statistics: {str(e)}")
            input("Press Enter to continue...")

    def run(self):
        """Run the interactive application"""
        while True:
            self.display_banner()
            self.display_menu()

            try:
                choice = input("Enter your choice (1-5): ").strip()

                if choice == '1':
                    self.preview_data()
                elif choice == '2':
                    self.generate_monthly_report()
                elif choice == '3':
                    self.custom_report()
                elif choice == '4':
                    self.view_statistics()
                elif choice == '5':
                    print("\nThank you for using Report Automation Tool!")
                    print("Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-5.")
                    input("Press Enter to continue...")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {str(e)}")
                input("Press Enter to continue...")

def main():
    """Main function"""
    app = InteractiveReportApp()
    app.run()

if __name__ == "__main__":
    main()