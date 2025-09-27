# GitHub Actions for Excel Windows Conversion

This repository includes automated GitHub Actions to convert Excel files to Windows-compatible format.

## 🚀 What It Does

- Automatically converts Excel files from the `file/` directory to Windows-compatible format
- Creates backup CSV files for maximum compatibility
- Runs on every push to main/master branch
- Generates releases with converted files

## 📁 File Structure

```
.github/
└── workflows/
    └── convert-excel.yml          # GitHub Action workflow

scripts/
├── convert_excel_windows.py      # Main conversion script
└── convert_to_windows.sh         # Bash script for local conversion

file/                              # Input Excel files
file_windows/                      # Output Windows-compatible files
```

## 🔄 How It Works

### Automatic Conversion (GitHub Actions)

1. **Trigger**: Runs on push to main/master branch or manual dispatch
2. **Environment**: Windows-latest with Python 3.11
3. **Process**:
   - Converts all `.xlsx` files in `file/` directory
   - Creates Windows-compatible versions in `file_windows/`
   - Generates CSV backups for each sheet
   - Uploads artifacts and creates releases

### Local Conversion

#### Method 1: Using Bash Script
```bash
./scripts/convert_to_windows.sh
```

#### Method 2: Using Python Directly
```bash
python3 scripts/convert_excel_windows.py
```

## 📋 Requirements

### For Local Usage
- Python 3.8+
- Required packages:
  ```bash
  pip install pandas openpyxl
  ```

### For GitHub Actions
- No additional requirements (handled automatically)

## 📄 Output Files

### Excel Files
- **Format**: `_windows.xlsx` suffix
- **Compatibility**: Optimized for Microsoft Excel on Windows
- **Features**: Preserves all formatting, colors, borders, and styles

### CSV Files
- **Format**: `_sheetname.csv` suffix
- **Encoding**: UTF-8 with BOM (Excel-compatible)
- **Usage**: Maximum compatibility across all platforms

## 🎯 Features

### Windows Compatibility
- Uses Arial font (Windows default)
- Optimized number formats
- Proper encoding support
- Enhanced print settings

### Formatting Preservation
- ✅ Cell values and formulas
- ✅ Colors and fills
- ✅ Borders and alignment
- ✅ Font styles and sizes
- ✅ Column widths and row heights
- ✅ Merged cells
- ✅ Number formats

### Error Handling
- Comprehensive error reporting
- Graceful failure handling
- Detailed logging

## 🔧 Customization

### Modifying Conversion Settings
Edit `scripts/convert_excel_windows.py`:
```python
# Change default font
font_name = cell.font.name or 'Calibri'  # Instead of Arial

# Modify output directory
output_dir = "custom_output"
```

### Adding New File Types
Extend the conversion script to handle other formats:
```python
if filename.endswith(('.xlsx', '.xls')):
    # Handle Excel files
elif filename.endswith('.csv'):
    # Handle CSV files
```

## 📊 Monitoring

### GitHub Actions Status
- Check Actions tab in repository
- View conversion logs and results
- Download generated artifacts

### Local Usage
- Console output shows progress
- Error messages for failed conversions
- Summary statistics

## 🐛 Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   chmod +x scripts/convert_to_windows.sh
   ```

2. **Missing Dependencies**
   ```bash
   pip install pandas openpyxl
   ```

3. **File Not Found**
   - Ensure Excel files are in `file/` directory
   - Check file permissions

4. **Encoding Issues**
   - CSV files use UTF-8 with BOM
   - Excel files preserve original encoding

### Debug Mode
Enable verbose logging:
```python
# In convert_excel_windows.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Usage Statistics

The conversion process tracks:
- Number of files converted
- Files with errors
- Processing time
- Output directory location

## 🔄 Version History

### v1.0
- Initial release
- Basic Excel to Windows conversion
- CSV backup generation
- GitHub Actions integration

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Open an issue with details about your specific case

## 🎉 Next Steps

- [ ] Add support for more file formats
- [ ] Implement batch processing optimizations
- [ ] Add email notifications
- [ ] Create web interface for conversion