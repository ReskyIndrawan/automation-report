#!/usr/bin/env python3
"""
Excel to Windows Format Converter
Converts Excel files to Windows-compatible format with enhanced compatibility
"""

import os
import sys
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

def convert_excel_for_windows(input_file, output_file):
    """Convert Excel file to Windows-compatible format with enhanced compatibility"""
    print(f"Converting file to Windows format...")

    try:
        # Load the original workbook
        wb = load_workbook(input_file)

        # Create a new workbook for Windows compatibility
        from openpyxl import Workbook
        wb_windows = Workbook()

        # Remove the default sheet
        if 'Sheet' in wb_windows.sheetnames:
            wb_windows.remove(wb_windows['Sheet'])

        # Copy each sheet with Windows-compatible formatting
        for sheet_name in wb.sheetnames:
            try:
                sheet_name.encode('cp1252')
                print(f"Processing sheet: {sheet_name}")
                sheet_name_display = sheet_name
            except UnicodeEncodeError:
                print(f"Processing sheet (sheet with Japanese characters)")
                # Use a generic name for the sheet
                sheet_name_display = f"Sheet_{wb.sheetnames.index(sheet_name) + 1}"
            sheet = wb[sheet_name]

            # Create new sheet in Windows workbook
            new_sheet = wb_windows.create_sheet(sheet_name_display)

            # Copy merged cells first
            for merge_range in sheet.merged_cells.ranges:
                new_sheet.merge_cells(str(merge_range))

            # Copy all cell values and formatting
            for row in sheet.iter_rows():
                for cell in row:
                    new_cell = new_sheet.cell(row=cell.row, column=cell.column, value=cell.value)

                    # Copy font formatting with Windows compatibility
                    if cell.font:
                        font_name = cell.font.name or 'Arial'  # Default to Arial for Windows
                        font_size = cell.font.size or 10

                        new_cell.font = Font(
                            name=font_name,
                            size=font_size,
                            bold=cell.font.bold or False,
                            italic=cell.font.italic or False,
                            underline=cell.font.underline or 'none',
                            strikethrough=cell.font.strikethrough or False,
                            color=cell.font.color
                        )

                    # Copy fill formatting
                    if cell.fill and cell.fill.fill_type:
                        new_cell.fill = PatternFill(
                            start_color=cell.fill.start_color,
                            end_color=cell.fill.end_color,
                            fill_type=cell.fill.fill_type
                        )

                    # Copy border formatting
                    if cell.border:
                        try:
                            new_cell.border = Border(
                                left=cell.border.left,
                                right=cell.border.right,
                                top=cell.border.top,
                                bottom=cell.border.bottom
                            )
                        except:
                            # Fallback to simple border if copying fails
                            thin_border = Border(
                                left=Side(style='thin'), right=Side(style='thin'),
                                top=Side(style='thin'), bottom=Side(style='thin')
                            )
                            new_cell.border = thin_border

                    # Copy alignment
                    if cell.alignment:
                        new_cell.alignment = Alignment(
                            horizontal=cell.alignment.horizontal or 'general',
                            vertical=cell.alignment.vertical or 'bottom',
                            wrap_text=cell.alignment.wrap_text or False,
                            shrink_to_fit=cell.alignment.shrink_to_fit or False,
                            indent=cell.alignment.indent or 0
                        )

                    # Copy number format with Windows compatibility
                    if hasattr(cell, 'number_format') and cell.number_format:
                        # Ensure number format is Windows-compatible
                        number_format = cell.number_format
                        if number_format not in ['general', 'General']:
                            new_cell.number_format = number_format

                    # Copy data validation if any
                    if cell.data_type and cell.data_type != 'n':
                        new_cell.data_type = cell.data_type

            # Copy column widths
            for col_letter, dimension in sheet.column_dimensions.items():
                if dimension.width:
                    new_sheet.column_dimensions[col_letter].width = dimension.width

            # Copy row heights
            for row_idx, dimension in sheet.row_dimensions.items():
                if dimension.height:
                    new_sheet.row_dimensions[row_idx].height = dimension.height

            # Copy print settings
            if sheet.print_options:
                new_sheet.print_options = sheet.print_options

            # Copy page setup
            if sheet.page_setup:
                new_sheet.page_setup = sheet.page_setup

            print(f"Successfully copied sheet: {sheet_name_display}")

        # Set the active sheet to match the original
        if wb.active:
            active_sheet_name = wb.active.title
            if active_sheet_name in wb_windows.sheetnames:
                wb_windows.active = wb_windows[active_sheet_name]

        # Save the Windows-compatible file
        wb_windows.save(output_file)
        print(f"Successfully converted to {output_file}")

        return True

    except Exception as e:
        print(f"Error converting {input_file}: {e}")
        return False

def create_csv_backup(input_file, output_dir):
    """Create CSV backup for maximum compatibility"""
    try:
        wb = load_workbook(input_file)

        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            # Handle sheet names with Japanese characters
            try:
                sheet_name.encode('cp1252')
                safe_sheet_name = sheet_name
            except UnicodeEncodeError:
                safe_sheet_name = f"Sheet_{wb.sheetnames.index(sheet_name) + 1}"

            data = []

            # Extract data from sheet
            for row in sheet.iter_rows(values_only=True):
                data.append([cell if cell is not None else '' for cell in row])

            if data and len(data) > 0:
                # Create DataFrame
                if len(data) > 1 and data[0]:
                    df = pd.DataFrame(data[1:], columns=data[0])
                else:
                    df = pd.DataFrame(data)

                # Save as CSV with UTF-8 BOM for Excel compatibility
                csv_filename = f"{os.path.splitext(os.path.basename(input_file))[0]}_{safe_sheet_name}.csv"
                csv_path = os.path.join(output_dir, csv_filename)

                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                print(f"Created CSV backup: {csv_path}")

        return True

    except Exception as e:
        print(f"Error creating CSV backup for {input_file}: {e}")
        return False

def main():
    """Main conversion function"""
    input_dir = "data"
    output_dir = "file_windows"

    print("Starting Excel to Windows conversion...")

    # Check input directory
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' not found")
        return 1

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Convert all Excel files
    converted_files = []
    error_files = []

    for filename in os.listdir(input_dir):
        if filename.endswith('.xlsx') and not filename.startswith('~'):
            input_path = os.path.join(input_dir, filename)
            output_filename = filename.replace('.xlsx', '_windows.xlsx')
            output_path = os.path.join(output_dir, output_filename)

            # Skip files with Japanese characters that can't be encoded in cp1252
            try:
                filename.encode('cp1252')
                print(f"\nProcessing: {filename}")
            except UnicodeEncodeError:
                print(f"\nSkipping file (contains characters not supported on Windows)")
                continue

            # Convert Excel file
            try:
                if convert_excel_for_windows(input_path, output_path):
                    converted_files.append(output_filename)

                    # Create CSV backup
                    try:
                        create_csv_backup(input_path, output_dir)
                    except Exception as e:
                        print(f"Warning: Could not create CSV backup: {e}")
                else:
                    error_files.append(filename)
            except Exception as e:
                print(f"Error processing file: {e}")
                error_files.append(filename)

    # Print summary
    print(f"\nConversion Summary:")
    print(f"Successfully converted: {len(converted_files)} files")
    print(f"Failed to convert: {len(error_files)} files")

    if converted_files:
        print(f"\nConverted files available in: {output_dir}")
        for filename in converted_files:
            print(f"   - {filename}")

    if error_files:
        print(f"\nFiles with errors:")
        for filename in error_files:
            print(f"   - {filename}")

    # Return success if at least one file was converted
    return 0 if len(converted_files) > 0 else 1

if __name__ == "__main__":
    sys.exit(main())