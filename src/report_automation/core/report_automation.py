#!/usr/bin/env python3
"""
Aplikasi Otomasi Pelaporan Kerja Bulanan
Menggabungkan data dari作業実績一覧 dan 検査工数 untuk generate laporan bulanan
"""

import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import calendar
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportAutomation:
    def __init__(self, work_file: str, inspection_file: str, n5_calculation_method: str = "average"):
        self.work_file = work_file
        self.inspection_file = inspection_file
        self.n5_calculation_method = n5_calculation_method  # "average" or "maximum"
        self.work_df = None
        self.inspection_data = {}

    def load_data(self):
        """Load data from Excel files"""
        logger.info("Loading work performance data...")
        self.work_df = pd.read_excel(self.work_file)

        logger.info("Loading inspection man-hours data...")
        self.inspection_data = self._load_inspection_data()

    def _load_inspection_data(self) -> Dict:
        """Load multi-sheet inspection data"""
        data = {}
        xls = pd.ExcelFile(self.inspection_file)

        for sheet_name in xls.sheet_names:
            try:
                df = pd.read_excel(self.inspection_file, sheet_name=sheet_name)
                data[sheet_name] = df
            except Exception as e:
                logger.warning(f"Failed to load sheet {sheet_name}: {e}")
                continue

        return data

    def process_monthly_report(self, year: int, month: int, output_path: str):
        """Generate monthly report for specified year and month"""
        logger.info(f"Generating monthly report for {year}-{month:02d}")

        # Filter work data for the specified month and work content
        work_data = self._filter_and_prepare_work_data(year, month)

        if work_data.empty:
            logger.warning(f"No work data found for {year}-{month:02d}")
            return

        # Get N5基準 data
        n5_data = self._get_n5_standard_data()

        # Create comparison data
        comparison_data = self._create_comparison_data(work_data, n5_data)

        # Create Excel report with multiple sheets
        wb = openpyxl.Workbook()

        # Remove default sheet
        wb.remove(wb.active)

        # Create only required report sheets
        self._create_n5_comparison_sheet(wb, comparison_data, year, month)
        self._create_report_summary_sheet(wb, comparison_data, year, month)

        # Save report
        wb.save(output_path)
        logger.info(f"Monthly report saved to: {output_path}")

    def _filter_work_by_month(self, df: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
        """Filter work data by specified year and month"""
        logger.info(f"Filtering data for {year}-{month:02d}")
        logger.info(f"Original data shape: {df.shape}")
        logger.info(f"Available columns: {list(df.columns)}")

        # Convert date columns if needed
        date_columns = ['日付', '年月日', '作業開始年月日時分', '作業終了年月日時分']

        for col in date_columns:
            if col in df.columns:
                logger.info(f"Converting column {col} to datetime")
                df[col] = pd.to_datetime(df[col], errors='coerce')
                logger.info(f"Column {col} after conversion: {df[col].dtype}")

        # Filter by month - try multiple date columns
        for col in date_columns:
            if col in df.columns and df[col].notna().any():
                mask = (df[col].dt.year == year) & (df[col].dt.month == month)
                filtered = df[mask].copy()
                logger.info(f"Filtered by {col}: {len(filtered)} records")
                if len(filtered) > 0:
                    return filtered

        # If no date filtering worked, return all data for testing
        logger.warning("Could not filter by date, returning all data for testing")
        return df.copy()

    def _filter_and_prepare_work_data(self, year: int, month: int) -> pd.DataFrame:
        """Filter work data for specified month and work content"""
        # Filter by month
        work_data = self._filter_work_by_month(self.work_df, year, month)

        if work_data.empty:
            return pd.DataFrame()

        # Filter by work content: only include 検査作業(受入れ・工程内・出荷前)
        if '作業内容' in work_data.columns:
            filtered_data = work_data[
                work_data['作業内容'] == '検査作業(受入れ・工程内・出荷前)'
            ].copy()

            # Filter out records with work time = 0
            if '作業時間' in filtered_data.columns:
                initial_count = len(filtered_data)
                filtered_data = filtered_data[filtered_data['作業時間'] > 0].copy()
                logger.info(f"Filtered work time = 0: {initial_count} -> {len(filtered_data)} records")

            # Group duplicate entries (same date, employee, product) and sum work times
            group_columns = []
            if '日付' in filtered_data.columns:
                group_columns.append('日付')
            if '社員名' in filtered_data.columns:
                group_columns.append('社員名')
            if '品目番号' in filtered_data.columns:
                group_columns.append('品目番号')

            if group_columns and '作業時間' in filtered_data.columns:
                initial_count = len(filtered_data)

                # Define aggregation dictionary
                agg_dict = {'作業時間': 'sum'}

                # For other columns, keep first value
                for col in filtered_data.columns:
                    if col not in group_columns and col != '作業時間':
                        agg_dict[col] = 'first'

                # Group by key columns and aggregate
                grouped_data = filtered_data.groupby(group_columns).agg(agg_dict).reset_index()
                logger.info(f"Grouped duplicate entries: {initial_count} -> {len(grouped_data)} records")

                filtered_data = grouped_data

            logger.info(f"Final filtered work data: {len(filtered_data)} records (from {len(work_data)})")
            return filtered_data

        return work_data

    def _get_n5_standard_data(self) -> pd.DataFrame:
        """Extract N5基準 data from inspection file"""
        if 'N5基準' not in self.inspection_data:
            logger.warning("N5基準 sheet not found in inspection data")
            return pd.DataFrame()

        n5_df = self.inspection_data['N5基準']
        logger.info(f"N5基準 data loaded: {len(n5_df)} records")

        # Map columns to expected names
        column_mapping = {
            '品番': '品目番号',
            '分': 'N5基準時間'
        }

        n5_data = n5_df.copy()
        for old_name, new_name in column_mapping.items():
            if old_name in n5_data.columns:
                n5_data = n5_data.rename(columns={old_name: new_name})

        # Calculate N5 time per item number based on selected method
        if '品目番号' in n5_data.columns and 'N5基準時間' in n5_data.columns:
            if self.n5_calculation_method == "maximum":
                # Use maximum time for each item number
                n5_standard = n5_data.groupby('品目番号')['N5基準時間'].max().reset_index()
                logger.info(f"N5基準 standard times calculated using MAXIMUM method for {len(n5_standard)} unique items")
            else:
                # Use average time (default behavior)
                n5_standard = n5_data.groupby('品目番号')['N5基準時間'].mean().reset_index()
                logger.info(f"N5基準 standard times calculated using AVERAGE method for {len(n5_standard)} unique items")
            return n5_standard

        return pd.DataFrame()

    def _create_comparison_data(self, work_data: pd.DataFrame, n5_data: pd.DataFrame) -> pd.DataFrame:
        """Create comparison data between actual work and N5 standard"""
        if work_data.empty or n5_data.empty:
            return pd.DataFrame()

        # Prepare work data for comparison
        comparison = work_data[[
            '日付', '社員名', '品目番号', '作業時間'
        ]].copy()

        # Rename columns to match desired output format
        comparison.columns = ['日月', 'OP', '作業内容（№を記入）', '分N1']

        # Merge with N5 standard data
        comparison = comparison.merge(
            n5_data,
            left_on='作業内容（№を記入）',
            right_on='品目番号',
            how='left'
        )

        # Fill missing N5 values with 0
        comparison['分N5'] = comparison['N5基準時間'].fillna(0)

        # Select and reorder final columns
        final_columns = ['日月', 'OP', '作業内容（№を記入）', '分N5', '分N1']
        comparison = comparison[final_columns]

        # Calculate difference
        comparison['差分'] = comparison['分N1'] - comparison['分N5']

        logger.info(f"Comparison data created: {len(comparison)} records")
        return comparison

    def _create_n5_comparison_sheet(self, wb: openpyxl.Workbook, comparison_data: pd.DataFrame, year: int, month: int):
        """Create N5 comparison sheet with professional formatting"""
        ws = wb.create_sheet("N5比較")

        if comparison_data.empty:
            ws['A1'] = f"{year}年{month}月 N5比較データなし"
            ws['A1'].font = Font(size=14, bold=True, color='FF0000')
            return

        # Filter out records with N5 = 0
        filtered_data = comparison_data[comparison_data['分N5'] > 0].copy()
        if filtered_data.empty:
            ws['A1'] = f"{year}年{month}月 有効なN5データなし"
            ws['A1'].font = Font(size=14, bold=True, color='FF0000')
            return

        # Title styling
        title_font = Font(name='Arial', size=16, bold=True, color='1F497D')
        title_fill = PatternFill(start_color='E6E6FA', end_color='E6E6FA', fill_type='solid')

        ws.merge_cells('A1:F1')
        ws['A1'] = f"{year}年{month}月 N5基準比較"
        ws['A1'].font = title_font
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws['A1'].fill = title_fill

        # Apply border to title
        for col in range(1, 7):
            ws.cell(row=1, column=col).border = Border(
                left=Side(style='thin'), right=Side(style='thin'),
                top=Side(style='thin'), bottom=Side(style='medium')
            )

        # Format date to remove time (日月 - date only)
        filtered_data['日月'] = pd.to_datetime(filtered_data['日月']).dt.date

        # Format difference to 2 decimal places
        filtered_data['差分'] = filtered_data['差分'].round(2)

        # Headers with special styling for N5 comparison
        headers = ['日月', 'OP', '作業内容（№を記入）', '分N5', '分N1', '差分']
        self._apply_header_styling(ws, headers, start_row=3, start_col=1)

        # Data without conditional formatting first
        data_start_row = 4
        for row, (_, comp_data) in enumerate(filtered_data.iterrows(), data_start_row):
            ws.cell(row=row, column=1, value=comp_data['日月'])
            ws.cell(row=row, column=2, value=comp_data['OP'])
            ws.cell(row=row, column=3, value=comp_data['作業内容（№を記入）'])
            ws.cell(row=row, column=4, value=comp_data['分N5'])
            ws.cell(row=row, column=5, value=comp_data['分N1'])
            ws.cell(row=row, column=6, value=comp_data['差分'])

        # Apply data styling to main table (skip difference column)
        if len(filtered_data) > 0:
            # Apply styling to columns 1-5 only
            self._apply_data_styling(ws, (data_start_row, 1), (data_start_row + len(filtered_data) - 1, 5))

            # Apply conditional formatting to difference column
            for row, (_, comp_data) in enumerate(filtered_data.iterrows(), data_start_row):
                difference_cell = ws.cell(row=row, column=6)

                # Ensure the difference value is numeric
                difference_value = float(comp_data['差分']) if pd.notna(comp_data['差分']) else 0.0

                # Create border for each cell
                thin_border = Border(
                    left=Side(style='thin'), right=Side(style='thin'),
                    top=Side(style='thin'), bottom=Side(style='thin')
                )

                if difference_value < 0:
                    # Time saved (negative difference) - GREEN
                    difference_cell.font = Font(color='006100', bold=True, name='Arial', size=10)
                    difference_cell.fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
                elif difference_value > 0:
                    # Time exceeded (positive difference) - RED
                    difference_cell.font = Font(color='9C0006', bold=True, name='Arial', size=10)
                    difference_cell.fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
                else:
                    # No difference - neutral styling
                    difference_cell.font = Font(color='000000', bold=True, name='Arial', size=10)
                    # Apply light gray fill for neutral values to maintain consistency
                    difference_cell.fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')

                # Apply border and alignment
                difference_cell.border = thin_border
                difference_cell.alignment = Alignment(horizontal='right', vertical='center')

                # Set number format to ensure proper display
                difference_cell.number_format = '0.00'

        # Add summary statistics section
        summary_start_row = data_start_row + len(filtered_data) + 2

        # Summary title
        ws.merge_cells(f'A{summary_start_row}:F{summary_start_row}')
        ws.cell(row=summary_start_row, column=1, value="統計サマリー")
        summary_title_cell = ws.cell(row=summary_start_row, column=1)
        summary_title_cell.font = Font(name='Arial', size=14, bold=True, color='1F497D')
        summary_title_cell.alignment = Alignment(horizontal='center', vertical='center')
        summary_title_cell.fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')

        # Apply border to summary title
        for col in range(1, 7):
            ws.cell(row=summary_start_row, column=col).border = Border(
                left=Side(style='thin'), right=Side(style='thin'),
                top=Side(style='double'), bottom=Side(style='thin')
            )

        # Summary headers and data
        summary_row = summary_start_row + 1
        summary_headers = ['項目', '値', '項目', '値']
        self._apply_header_styling(ws, summary_headers, start_row=summary_row, start_col=1)

        # Summary data in two columns
        summary_data = [
            ("平均分N5", f"{filtered_data['分N5'].mean():.2f}", "平均分N1", f"{filtered_data['分N1'].mean():.2f}"),
            ("平均差分", f"{filtered_data['差分'].mean():.2f}", "検査品目数", f"{len(filtered_data)}個"),
            ("合計分N5", f"{filtered_data['分N5'].sum():.0f}", "合計分N1", f"{filtered_data['分N1'].sum():.0f}"),
            ("合計差分", f"{filtered_data['差分'].sum():.0f}", "有効データ", f"{len(filtered_data)}件")
        ]

        for i, (col1_item, col1_value, col2_item, col2_value) in enumerate(summary_data, summary_row + 1):
            ws.cell(row=i, column=1, value=col1_item)
            ws.cell(row=i, column=2, value=col1_value)
            ws.cell(row=i, column=3, value=col2_item)
            ws.cell(row=i, column=4, value=col2_value)

        # Apply styling to summary data
        summary_end_row = summary_row + len(summary_data)
        self._apply_data_styling(ws, (summary_row + 1, 1), (summary_end_row, 4))

        # Apply special styling to total rows
        total_rows = [summary_row + 3, summary_row + 4]  # 合計分N5, 合計分N1, 合計差分 rows
        self._apply_total_styling(ws, total_rows, start_col=1, end_col=4)

        # Apply enhanced auto-fit
        self._enhanced_auto_fit_columns(ws, max_width=40)

    def _create_report_summary_sheet(self, wb: openpyxl.Workbook, comparison_data: pd.DataFrame, year: int, month: int):
        """Create report summary sheet in the format specified in report.txt"""
        ws = wb.create_sheet("報告サマリー")

        if comparison_data.empty:
            ws['A1'] = f"{year}年{month}月 データなし"
            ws['A1'].font = Font(size=14, bold=True, color='FF0000')
            return

        # Filter out records with N5 = 0
        filtered_data = comparison_data[comparison_data['分N5'] > 0].copy()
        if filtered_data.empty:
            ws['A1'] = f"{year}年{month}月 有効なN5データなし"
            ws['A1'].font = Font(size=14, bold=True, color='FF0000')
            return

        # Calculate totals
        total_n5 = filtered_data['分N5'].sum()
        total_n1 = filtered_data['分N1'].sum()
        total_difference = total_n1 - total_n5
        reduction_percentage = (total_difference / total_n5 * 100) if total_n5 > 0 else 0
        efficiency_percentage = (total_n1 / total_n5 * 100) if total_n5 > 0 else 0

        # Professional title styling
        title_font = Font(name='Arial', size=16, bold=True, color='1F497D')
        title_fill = PatternFill(start_color='FFE6CC', end_color='FFE6CC', fill_type='solid')

        ws.merge_cells('A1:C1')
        ws['A1'] = f"{year}年{month}月 N＝5→N＝1検査時間削減報告"
        ws['A1'].font = title_font
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws['A1'].fill = title_fill

        # Apply border to title
        for col in range(1, 4):
            ws.cell(row=1, column=col).border = Border(
                left=Side(style='thin'), right=Side(style='thin'),
                top=Side(style='thin'), bottom=Side(style='medium')
            )

        # Report content with enhanced styling
        report_lines = [
            f"{year}年{month}月のN＝5→N＝1にした",
            f"検査品目数→{len(filtered_data)}個の品番(重複あり)",
            f"検査時間　N5(基準値)だったら{total_n5:.0f}分かかっていた。",
            f"N1にしたことで{total_n1:.0f}分で済んだ({total_difference:.0f}分短縮できた)",
            "",
            f"({total_n1:.0f}×100)÷{total_n5:.0f}＝{efficiency_percentage:.2f}",
            f"100-{efficiency_percentage:.2f}＝{reduction_percentage:.2f}％削減"
        ]

        # Create a bordered report area
        report_start_row = 3
        report_end_row = report_start_row + len(report_lines) - 1

        # Apply border to report area
        for row in range(report_start_row, report_end_row + 1):
            for col in range(1, 4):
                cell = ws.cell(row=row, column=col)
                if row == report_start_row:
                    # Top border for first row
                    border = Border(
                        left=Side(style='thin'), right=Side(style='thin'),
                        top=Side(style='medium'), bottom=Side(style='thin')
                    )
                elif row == report_end_row:
                    # Bottom border for last row
                    border = Border(
                        left=Side(style='thin'), right=Side(style='thin'),
                        top=Side(style='thin'), bottom=Side(style='medium')
                    )
                else:
                    # Regular border for middle rows
                    border = Border(
                        left=Side(style='thin'), right=Side(style='thin'),
                        top=Side(style='thin'), bottom=Side(style='thin')
                    )
                cell.border = border

        # Insert report content with styling
        for row, line in enumerate(report_lines, report_start_row):
            cell = ws.cell(row=row, column=1, value=line)

            if line:  # Non-empty lines
                # Special styling for key metrics
                if "検査品目数" in line:
                    cell.font = Font(name='Arial', size=12, bold=True, color='1F497D')
                elif "分かかっていた" in line or "で済んだ" in line:
                    cell.font = Font(name='Arial', size=11, bold=True, color='000000')
                elif any(char in line for char in "×100÷＝％"):
                    # Formula lines
                    cell.font = Font(name='Courier New', size=11, color='000080')
                    cell.alignment = Alignment(horizontal='left', vertical='center')
                else:
                    cell.font = Font(name='Arial', size=11, color='000000')
            else:
                # Empty line spacing
                continue

            # Background color for summary section
            if row >= report_start_row + 5:  # Formula lines
                cell.fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')

        # Add summary box at bottom
        summary_row = report_end_row + 2
        ws.merge_cells(f'A{summary_row}:C{summary_row}')
        summary_cell = ws.cell(row=summary_row, column=1)
        summary_cell.value = f"総合評価: {'時間短縮' if reduction_percentage < 0 else '時間超過'} {abs(reduction_percentage):.2f}%"

        # Summary styling based on performance
        if reduction_percentage < 0:
            # Positive performance
            summary_cell.font = Font(name='Arial', size=12, bold=True, color='006100')
            summary_cell.fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
        else:
            # Negative performance
            summary_cell.font = Font(name='Arial', size=12, bold=True, color='9C0006')
            summary_cell.fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')

        summary_cell.alignment = Alignment(horizontal='center', vertical='center')

        # Apply border to summary
        for col in range(1, 4):
            ws.cell(row=summary_row, column=col).border = Border(
                left=Side(style='thin'), right=Side(style='thin'),
                top=Side(style='double'), bottom=Side(style='medium')
            )

        # Apply enhanced auto-fit
        self._enhanced_auto_fit_columns(ws, max_width=50)

    def _apply_header_styling(self, ws: Worksheet, headers: list, start_row: int = 1, start_col: int = 1):
        """Apply professional header styling"""
        header_font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        header_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='medium')
        )

        for col_idx, header in enumerate(headers, start_col):
            cell = ws.cell(row=start_row, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = header_border
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    def _apply_data_styling(self, ws: Worksheet, data_range_start: tuple, data_range_end: tuple):
        """Apply data cell styling with borders and alternating colors"""
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        # Light gray for alternating rows
        light_gray_fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')
        data_font = Font(name='Arial', size=10)
        number_font = Font(name='Arial', size=10)

        start_row, start_col = data_range_start
        end_row, end_col = data_range_end

        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                cell = ws.cell(row=row, column=col)
                cell.border = thin_border

                # Alternating row colors
                if (row - start_row) % 2 == 1:
                    cell.fill = light_gray_fill

                # Font styling based on content type
                if isinstance(cell.value, (int, float)):
                    cell.font = number_font
                    # Align numbers to right
                    cell.alignment = Alignment(horizontal='right', vertical='center')
                else:
                    cell.font = data_font
                    cell.alignment = Alignment(horizontal='left', vertical='center')

    def _apply_total_styling(self, ws: Worksheet, total_rows: list, start_col: int = 1, end_col: int = None):
        """Apply special styling for total/summary rows"""
        total_font = Font(name='Arial', size=11, bold=True, color='1F497D')
        total_fill = PatternFill(start_color='E6E6FA', end_color='E6E6FA', fill_type='solid')
        total_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='double'), bottom=Side(style='medium')
        )

        for row_num in total_rows:
            for col in range(start_col, (end_col or ws.max_column) + 1):
                cell = ws.cell(row=row_num, column=col)
                cell.font = total_font
                cell.fill = total_fill
                cell.border = total_border
                cell.alignment = Alignment(horizontal='center', vertical='center')

    def _enhanced_auto_fit_columns(self, ws: Worksheet, max_width: int = 60):
        """Enhanced auto-fit with better width calculation based on cell content"""
        for column_idx, column in enumerate(ws.columns, 1):
            max_length = 0
            column_letter = get_column_letter(column_idx)

            # Find the maximum length from actual cell content (skip headers)
            for cell in column:
                try:
                    if not isinstance(cell, openpyxl.worksheet.cell.MergedCell) and cell.value is not None:
                        # Skip header row (typically row 1-3)
                        if cell.row <= 3:
                            continue

                        # Consider content length and font
                        content_length = len(str(cell.value))
                        # Add extra space for padding
                        adjusted_length = content_length + 4

                        # For Japanese characters, they might need more space
                        if any(ord(char) > 127 for char in str(cell.value)):
                            adjusted_length = int(adjusted_length * 1.4)

                        # For numbers, add more space for better readability
                        if isinstance(cell.value, (int, float)):
                            adjusted_length += 2

                        if adjusted_length > max_length:
                            max_length = adjusted_length
                except:
                    pass

            # If no content found, use header length as fallback
            if max_length == 0:
                for cell in column:
                    try:
                        if not isinstance(cell, openpyxl.worksheet.cell.MergedCell) and cell.value is not None:
                            content_length = len(str(cell.value))
                            adjusted_length = content_length + 3
                            if any(ord(char) > 127 for char in str(cell.value)):
                                adjusted_length = int(adjusted_length * 1.3)
                            max_length = max(max_length, adjusted_length)
                            break
                    except:
                        pass

            # Set reasonable minimum and maximum widths
            min_width = 10  # Increased minimum width
            adjusted_width = max(min_width, min(max_length, max_width))
            ws.column_dimensions[column_letter].width = adjusted_width

    def _auto_fit_columns(self, ws: Worksheet):
        """Legacy method - delegates to enhanced version"""
        self._enhanced_auto_fit_columns(ws)

def main():
    """Main function to run the report automation"""
    # File paths
    work_file = "file/9.xlsx"
    inspection_file = "file/検査工数.xlsx"

    # Check if files exist
    if not os.path.exists(work_file):
        print(f"Error: Work file not found: {work_file}")
        return

    if not os.path.exists(inspection_file):
        print(f"Error: Inspection file not found: {inspection_file}")
        return

    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Initialize report automation
    report_automation = ReportAutomation(work_file, inspection_file)

    try:
        # Load data
        report_automation.load_data()

        # Get current month and year
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        # Generate report
        output_file = os.path.join(output_dir, f"月次報告書_{year}_{month:02d}.xlsx")
        report_automation.process_monthly_report(year, month, output_file)

        print(f"✅ 月次報告書が生成されました: {output_file}")

    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        logger.error(f"Report generation failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()