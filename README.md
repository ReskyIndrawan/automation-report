# Report Automation

Python application for automated monthly report generation comparing actual work data with N5 standards.

## 🚀 Main Features

- **Automated Reports**: Generate monthly reports with 2 main sheets (N5比較, 方向く報告サマリー)
- **Standard Comparison**: Compare actual work time vs N5 standards
- **Filtering & Aggregation**: Filter zero data and group duplicates
- **Multi-Interface**: GUI with Tkinter and Command Line Interface
- **Professional Formatting**: Export to Excel with automatic formatting
- **GitHub Actions**: Automatic Excel to Windows format conversion

## 📋 Generated Sheets

1. **N5比較 (N5 Comparison)** - Compare actual vs N5 standard times
2. **方向く報告サマリー (Direction Report Summary)** - Monthly summary report

## 🏗️ Project Structure

```
report-automation/
├── src/
│   └── report_automation/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── report_automation.py
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── gui_app.py
│       │   ├── simple_generate.py
│       │   ├── interactive_app.py
│       │   └── run_gui.py
│       └── utils/
│           └── __init__.py
├── file/                        # Input files
│   ├── 9.xlsx                  # Actual work data
│   └── 検査工数.xlsx           # N5 standard data
├── file_windows/               # Windows-compatible output
├── scripts/                    # Utility scripts
│   ├── main.py
│   ├── convert_excel_windows.py
│   ├── convert_to_windows.sh
│   └── test_conversion.py
├── .github/workflows/          # GitHub Actions
│   └── convert-excel.yml
├── tests/                      # Unit tests
├── pyproject.toml
└── README.md
```

## 💿 Installation

### With uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### With pip

```bash
# Install dependencies
pip install pandas openpyxl

# Or install from source
pip install -e .
```

## 🎮 Usage

### GUI Mode

```bash
# Run GUI
python scripts/main.py

# Or run directly
python src/report_automation/gui/gui_app.py
```

### Command Line Mode

```bash
# Generate simple report
python src/report_automation/gui/simple_generate.py

# With custom output
python src/report_automation/gui/simple_generate.py custom_output.xlsx
```

### Interactive Mode

```bash
# Interactive mode
python src/report_automation/gui/interactive_app.py
```

## 🔄 GitHub Actions - Excel Conversion

This project includes automated GitHub Actions to convert Excel files to Windows-compatible format:

### Automatic Features:
- **Windows Conversion**: Converts `.xlsx` files to Windows format
- **CSV Backups**: Creates UTF-8 CSV files for maximum compatibility
- **Automatic Releases**: Generates releases on main branch pushes
- **Artifact Upload**: Uploads converted files for download

### Local Conversion:
```bash
# Convert Excel files to Windows format
./scripts/convert_to_windows.sh

# Or use Python directly
python scripts/convert_excel_windows.py
```

### Output Files:
- `file_windows/*_windows.xlsx` - Windows-compatible Excel files
- `file_windows/*_sheetname.csv` - CSV backup files

## ⚙️ Configuration

### Input Files
- `file/9.xlsx` - Actual work data
- `file/検査工数.xlsx` - N5 standard data (sheet: N5基準)

### Output Files
- `file_windows/*_windows.xlsx` - Windows-compatible monthly reports

### N5 Calculation Methods
The GUI provides radio buttons to select N5 calculation method:
- **平均時間 (Average Time)** - Current logic (average of duplicate records)
- **最長時間 (Maximum Time)** - Take longest time for duplicate records

## 🎨 Features

### Color Coding
- **差分 (Difference) Column**:
  - 🟢 **Green**: Negative values (time saved vs N5)
  - 🔴 **Red**: Positive values (time exceeded vs N5)
  - ⚪ **Gray**: Zero values (exact match with N5)

### Excel Formatting
- Auto-fit column widths based on content
- Professional headers with colors and borders
- Alternating row colors for readability
- Number formatting with 2 decimal places

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Test Excel conversion
python scripts/test_conversion.py
```

## 🛠️ Development

### Code Style
```bash
# Format code with black
black src/ scripts/

# Type checking
mypy src/
```

### Adding New Features
1. Create a new branch
2. Add features in appropriate folders
3. Add tests in `tests/`
4. Update documentation
5. Submit pull request

## 🤝 Contributing

1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- QC & Engineering Team for requirements and feedback
- Open source community for the libraries used
- Management for support and approval

## 🆘 Support

For questions or issues:
- GitHub Issues: [Report Issues](https://github.com/company/report-automation/issues)
- Email: support@company.com

---

Created with ❤️ by Report Automation Team