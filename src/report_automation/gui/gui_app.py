#!/usr/bin/env python3
"""
GUI Application untuk Report Automation dengan Tkinter
Sesuai dengan requirements di concept.txt - Optimized version
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import sys
import atexit
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.report_automation.core.report_automation import ReportAutomation
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global flag to prevent multiple instances
_gui_running = False
_root_window = None

class ReportAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("N5 Comparison Report Generator")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)

        # File paths with defaults
        self.work_file_path = tk.StringVar(value="")
        self.inspection_file_path = tk.StringVar(value="")
        self.output_file_path = tk.StringVar()

        # Data storage
        self.work_data = None
        self.inspection_data = None
        self.preview_data = None
        self.preview_limit = 50  # Limit preview rows for performance

        # Process tracking
        self.is_processing = False

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # File Selection Section
        file_frame = ttk.LabelFrame(main_frame, text="ファイル選択", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Work Data File
        ttk.Label(file_frame, text="作業実績ファイル:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(file_frame, textvariable=self.work_file_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="参照", command=self.browse_work_file).grid(row=0, column=2)

        # Inspection Data File
        ttk.Label(file_frame, text="検査工数ファイル:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(file_frame, textvariable=self.inspection_file_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="参照", command=self.browse_inspection_file).grid(row=1, column=2)

        # Output File
        ttk.Label(file_frame, text="出力ファイル名:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(file_frame, textvariable=self.output_file_path, width=50).grid(row=2, column=1, padx=5)
        ttk.Button(file_frame, text="参照", command=self.browse_output_file).grid(row=2, column=2)

        # N5 Calculation Method
        n5_method_frame = ttk.LabelFrame(file_frame, text="N5基準計算方法", padding="5")
        n5_method_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Radio button variable
        self.n5_calculation_method = tk.StringVar(value="average")

        # Radio buttons
        ttk.Radiobutton(n5_method_frame, text="平均時間（現在のロジック）", variable=self.n5_calculation_method, value="average").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Radiobutton(n5_method_frame, text="最長時間", variable=self.n5_calculation_method, value="maximum").grid(row=0, column=1, sticky=tk.W, padx=5)

        # Data Preview Section
        preview_frame = ttk.LabelFrame(main_frame, text="データプレビュー", padding="10")
        preview_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Preview Notebook
        self.preview_notebook = ttk.Notebook(preview_frame)
        self.preview_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Work Data Preview
        self.work_preview_frame = ttk.Frame(self.preview_notebook)
        self.preview_notebook.add(self.work_preview_frame, text="作業実績プレビュー")
        self.work_tree = self.create_preview_tree(self.work_preview_frame)

        # N5 Standard Preview
        self.n5_preview_frame = ttk.Frame(self.preview_notebook)
        self.preview_notebook.add(self.n5_preview_frame, text="N5基準プレビュー")
        self.n5_tree = self.create_preview_tree(self.n5_preview_frame)

        # Comparison Preview
        self.comparison_preview_frame = ttk.Frame(self.preview_notebook)
        self.preview_notebook.add(self.comparison_preview_frame, text="比較プレビュー")
        self.comparison_tree = self.create_preview_tree(self.comparison_preview_frame)

        # Control Buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(control_frame, text="データ読込", command=self.load_data).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="比較プレビュー", command=self.preview_comparison).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="レポート生成", command=self.generate_report).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="終了", command=self.safe_exit).grid(row=0, column=3, padx=5)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("準備完了")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

    def create_preview_tree(self, parent):
        """Create a treeview for data preview with horizontal and vertical scrollbars"""
        # Create treeview with both scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Use simpler approach with direct treeview and scrollbars
        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create treeview
        tree = ttk.Treeview(tree_frame, selectmode='extended',
                           yscrollcommand=v_scrollbar.set,
                           xscrollcommand=h_scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbars
        v_scrollbar.config(command=tree.yview)
        h_scrollbar.config(command=tree.xview)

        return tree

    def browse_work_file(self):
        """Browse for work data file"""
        filename = filedialog.askopenfilename(
            title="作業実績ファイルを選択",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.work_file_path.set(filename)

    def browse_inspection_file(self):
        """Browse for inspection data file"""
        filename = filedialog.askopenfilename(
            title="検査工数ファイルを選択",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.inspection_file_path.set(filename)

    def browse_output_file(self):
        """Browse for output file location"""
        filename = filedialog.asksaveasfilename(
            title="出力ファイルを保存",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.output_file_path.set(filename)

    def load_data(self):
        """Load data from selected files"""
        if not self.work_file_path.get() or not self.inspection_file_path.get():
            messagebox.showerror("Error", "Please select both input files")
            return

        self.is_processing = True
        self.status_var.set("Loading data...")
        self.progress.start()

        # Load data in separate thread to avoid freezing UI
        threading.Thread(target=self._load_data_thread, daemon=True).start()

    def _load_data_thread(self):
        """Load data in separate thread with progress feedback"""
        try:
            self.root.after(0, lambda: self.status_var.set("Loading work data..."))

            # Load work data
            self.work_data = pd.read_excel(self.work_file_path.get())
            logger.info(f"Work data loaded: {len(self.work_data)} records")

            self.root.after(0, lambda: self.status_var.set("Loading inspection data..."))

            # Load inspection data
            xls = pd.ExcelFile(self.inspection_file_path.get())
            self.inspection_data = {}
            total_sheets = len(xls.sheet_names)

            for i, sheet_name in enumerate(xls.sheet_names):
                try:
                    df = pd.read_excel(self.inspection_file_path.get(), sheet_name=sheet_name)
                    self.inspection_data[sheet_name] = df

                    # Update progress
                    progress = (i + 1) / total_sheets * 100
                    self.root.after(0, lambda p=progress: self.status_var.set(f"Loading inspection data... {p:.0f}%"))

                except Exception as e:
                    logger.warning(f"Failed to load sheet {sheet_name}: {e}")

            logger.info(f"Inspection data loaded: {len(self.inspection_data)} sheets")

            # Update UI in main thread
            self.root.after(0, self._update_preview_after_load)

        except Exception as e:
            self.is_processing = False
            self.root.after(0, lambda: self._show_error(f"Error loading data: {str(e)}"))

    def _update_preview_after_load(self):
        """Update preview after data is loaded"""
        self.progress.stop()
        self.is_processing = False
        self.status_var.set("Data loaded successfully")

        # Update work data preview with relevant columns only
        if self.work_data is not None:
            relevant_columns = ['日付', '社員名', '品目番号', '作業内容', '作業時間']
            available_columns = [col for col in relevant_columns if col in self.work_data.columns]
            if available_columns:
                work_preview = self.work_data[available_columns].head(50)
                self.update_tree_preview(self.work_tree, work_preview)

        # Update N5 standard preview with relevant columns only
        if 'N5基準' in self.inspection_data:
            n5_data = self.inspection_data['N5基準']
            relevant_columns = ['品番', '分', 'OP']
            available_columns = [col for col in relevant_columns if col in n5_data.columns]
            if available_columns:
                n5_preview = n5_data[available_columns].head(50)
                self.update_tree_preview(self.n5_tree, n5_preview)

        messagebox.showinfo("Success", "Data loaded successfully!")

    def update_tree_preview(self, tree, data):
        """Update treeview with data preview - optimized for large data"""
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)

        if data is None or data.empty:
            return

        # Limit data for preview
        if len(data) > self.preview_limit:
            preview_data = data.head(self.preview_limit)
        else:
            preview_data = data

        # Special formatting for comparison data
        if '日月' in preview_data.columns:
            # Format date to remove time
            if pd.api.types.is_datetime64_any_dtype(preview_data['日月']):
                preview_data['日月'] = pd.to_datetime(preview_data['日月']).dt.date

            # Format difference to 2 decimal places
            if '差分' in preview_data.columns:
                preview_data['差分'] = preview_data['差分'].round(2)

        # Set columns
        columns = list(preview_data.columns)
        tree["columns"] = columns
        tree["show"] = "headings"

        # Set headings with truncated text for long column names
        for col in columns:
            heading_text = str(col)
            if len(heading_text) > 20:
                heading_text = heading_text[:17] + "..."
            tree.heading(col, text=heading_text)
            tree.column(col, width=120, minwidth=80)

        # Add data with optimized display
        for _, row in preview_data.iterrows():
            values = []
            for value in row.values:
                # Format numeric values
                if isinstance(value, float):
                    str_value = f"{value:.2f}"
                else:
                    # Truncate long text values
                    str_value = str(value)
                    if len(str_value) > 50:
                        str_value = str_value[:47] + "..."
                values.append(str_value)
            tree.insert("", tk.END, values=values)

        # Show info if data was truncated
        if len(data) > self.preview_limit:
            tree.insert("", tk.END, values=[f"... Showing {self.preview_limit} of {len(data)} records ..."] + [""] * (len(columns) - 1))

        # Auto-resize columns after data is loaded
        self.root.after(100, lambda: self._auto_resize_columns(tree))

    def _auto_resize_columns(self, tree):
        """Auto-resize treeview columns"""
        for col in tree["columns"]:
            # Calculate max width
            max_width = max(80, len(str(col)) * 8)  # Minimum 80 pixels
            for item in tree.get_children():
                try:
                    item_text = tree.item(item, "values")[tree["columns"].index(col)]
                    item_width = len(str(item_text)) * 8
                    max_width = max(max_width, min(item_width, 300))  # Max 300 pixels
                except (IndexError, ValueError):
                    pass

            tree.column(col, width=max_width)

    def preview_comparison(self):
        """Preview comparison data"""
        if self.work_data is None or self.inspection_data is None:
            messagebox.showerror("Error", "Please load data first")
            return

        self.is_processing = True
        self.status_var.set("Generating comparison preview...")
        self.progress.start()

        threading.Thread(target=self._preview_comparison_thread, daemon=True).start()

    def _preview_comparison_thread(self):
        """Generate comparison preview in separate thread"""
        try:
            # Filter work data
            current_date = datetime.now()
            year = current_date.year
            month = current_date.month

            # Filter by work content
            if '作業内容' in self.work_data.columns:
                filtered_work = self.work_data[
                    self.work_data['作業内容'] == '検査作業(受入れ・工程内・出荷前)'
                ].copy()
            else:
                filtered_work = self.work_data.copy()

            # Get N5 standard data based on selected method
            if 'N5基準' in self.inspection_data:
                n5_df = self.inspection_data['N5基準']
                if self.n5_calculation_method.get() == "maximum":
                    n5_standard = n5_df.groupby('品番')['分'].max().reset_index()
                else:
                    n5_standard = n5_df.groupby('品番')['分'].mean().reset_index()
                n5_standard.columns = ['品目番号', 'N5基準時間']
            else:
                n5_standard = pd.DataFrame()

            # Create comparison
            if not filtered_work.empty and not n5_standard.empty:
                comparison = filtered_work[[
                    '日付', '社員名', '品目番号', '作業時間'
                ]].copy()
                comparison.columns = ['日月', 'OP', '作業内容（№を記入）', '分N1']

                comparison = comparison.merge(
                    n5_standard,
                    left_on='作業内容（№を記入）',
                    right_on='品目番号',
                    how='left'
                )

                comparison['分N5'] = comparison['N5基準時間'].fillna(0)
                comparison = comparison[['日月', 'OP', '作業内容（№を記入）', '分N5', '分N1']]
                comparison['差分'] = comparison['分N1'] - comparison['分N5']

                self.preview_data = comparison.head(100)

                # Update UI
                self.root.after(0, self._update_comparison_preview)
            else:
                self.root.after(0, lambda: self._show_error("No matching data for comparison"))

        except Exception as e:
            self.is_processing = False
            self.root.after(0, lambda: self._show_error(f"Error generating preview: {str(e)}"))

    def _update_comparison_preview(self):
        """Update comparison preview"""
        self.progress.stop()
        self.is_processing = False
        self.status_var.set("Comparison preview generated")

        if self.preview_data is not None:
            # Filter out records with N5 = 0 for preview
            filtered_preview = self.preview_data[self.preview_data['分N5'] > 0].copy()
            if not filtered_preview.empty:
                self.update_tree_preview(self.comparison_tree, filtered_preview)
                messagebox.showinfo("Success", f"Comparison preview generated! ({len(filtered_preview)} valid records)")
            else:
                messagebox.showwarning("Warning", "No valid N5 comparison data available (all N5 = 0)")
        else:
            messagebox.showwarning("Warning", "No comparison data available")

    def generate_report(self):
        """Generate final report"""
        # Validate input files
        if not self.work_file_path.get():
            messagebox.showerror("Error", "Please select work data file (9.xlsx)")
            return

        if not self.inspection_file_path.get():
            messagebox.showerror("Error", "Please select inspection file (検査工数.xlsx)")
            return

        # Check if files exist
        if not os.path.exists(self.work_file_path.get()):
            messagebox.showerror("Error", f"Work file not found: {self.work_file_path.get()}")
            return

        if not os.path.exists(self.inspection_file_path.get()):
            messagebox.showerror("Error", f"Inspection file not found: {self.inspection_file_path.get()}")
            return

        # Check if data is loaded
        if self.work_data is None or self.inspection_data is None:
            response = messagebox.askyesno("Data Not Loaded",
                                         "Data has not been loaded yet. Load data now?\n\n"
                                         "This may take a moment for large files.")
            if response:
                self.load_data()
            else:
                return

        # Set default output filename if not provided
        if not self.output_file_path.get():
            current_date = datetime.now()
            default_name = f"月次報告書_{current_date.year}_{current_date.month:02d}.xlsx"
            self.output_file_path.set(default_name)

        self.is_processing = True
        self.status_var.set("Generating report...")
        self.progress.start()

        threading.Thread(target=self._generate_report_thread, daemon=True).start()

    def _generate_report_thread(self):
        """Generate report in separate thread"""
        try:
            self.root.after(0, lambda: self.status_var.set("Initializing report automation..."))

            # Create output directory if needed
            output_dir = os.path.dirname(self.output_file_path.get())
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Initialize report automation with N5 calculation method
            report_automation = ReportAutomation(
                self.work_file_path.get(),
                self.inspection_file_path.get(),
                self.n5_calculation_method.get()
            )

            self.root.after(0, lambda: self.status_var.set("Loading data..."))

            # Load data first - this is the missing step!
            report_automation.load_data()

            # Get current month and year
            current_date = datetime.now()
            year = current_date.year
            month = current_date.month

            self.root.after(0, lambda: self.status_var.set(f"Generating report for {year}-{month:02d}..."))

            # Generate report
            report_automation.process_monthly_report(year, month, self.output_file_path.get())

            # Update UI
            self.root.after(0, lambda: self._report_generation_success())

        except Exception as e:
            self.is_processing = False
            self.root.after(0, lambda: self._show_error(f"Error generating report: {str(e)}"))

    def _report_generation_success(self):
        """Handle successful report generation"""
        self.progress.stop()
        self.is_processing = False
        self.status_var.set("Report generated successfully")

        # Get method description
        method_text = "平均時間" if self.n5_calculation_method.get() == "average" else "最長時間"

        messagebox.showinfo("Success",
            f"レポートが正常に生成されました！\n\n"
            f"生成されたシート:\n"
            f"• N5比較\n"
            f"• 報告サマリー\n\n"
            f"N5基準計算方法: {method_text}\n\n"
            f"保存先: {self.output_file_path.get()}")

    def _show_error(self, message):
        """Show error message"""
        self.progress.stop()
        self.is_processing = False
        self.status_var.set("Error occurred")
        messagebox.showerror("Error", message)

    def safe_exit(self):
        """Safely exit the application"""
        global _gui_running, _root_window

        try:
            # Confirm exit if there are running processes
            if self.is_processing:
                response = messagebox.askyesno("Confirm Exit",
                                               "A process is currently running.\nAre you sure you want to exit?")
                if not response:
                    return

            # Stop any running progress
            if hasattr(self, 'progress'):
                self.progress.stop()

            # Update status
            if hasattr(self, 'status_var'):
                self.status_var.set("Exiting...")

            # Clean up resources
            self.work_data = None
            self.inspection_data = None
            self.preview_data = None
            self.is_processing = False

            # Reset global flag
            _gui_running = False
            _root_window = None

            # Quit the mainloop
            self.root.quit()

        except Exception as e:
            logger.error(f"Error during exit: {e}")
            # Force quit if normal exit fails
            try:
                _gui_running = False
                _root_window = None
                self.root.quit()
            except:
                # Last resort - terminate the entire process
                os._exit(0)

def cleanup_on_exit():
    """Cleanup function called on exit"""
    global _gui_running, _root_window

    try:
        _gui_running = False
        if _root_window:
            try:
                _root_window.quit()
                _root_window.destroy()
            except:
                pass
            _root_window = None
    except:
        pass

def main():
    """Main function to run the GUI application"""
    global _gui_running, _root_window

    # Prevent multiple instances
    if _gui_running:
        print("GUI is already running")
        return

    _gui_running = True

    # Register cleanup function
    atexit.register(cleanup_on_exit)

    try:
        # Create root window
        root = tk.Tk()
        _root_window = root

        # Create app instance
        app = ReportAutomationGUI(root)

        # Start the mainloop
        root.mainloop()

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        cleanup_on_exit()
        sys.exit(0)
    except Exception as e:
        print(f"Application error: {e}")
        cleanup_on_exit()
        sys.exit(1)
    finally:
        cleanup_on_exit()

if __name__ == "__main__":
    main()