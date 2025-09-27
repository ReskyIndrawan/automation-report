# Struktur Proyek Report Automation

## 🏗️ Struktur Folder Best Practice Python

```
report-automation/
├── 📁 src/                          # Source code utama
│   └── 📁 report_automation/         # Package utama
│       ├── 🐍 __init__.py            # Package initialization
│       ├── 📁 core/                  # Core functionality
│       │   ├── 🐍 __init__.py
│       │   └── 🐍 report_automation.py  # Main logic class
│       ├── 📁 gui/                   # GUI applications
│       │   ├── 🐍 __init__.py
│       │   ├── 🐍 gui_app.py          # Tkinter GUI
│       │   ├── 🐍 simple_generate.py  # CLI generator
│       │   └── 🐍 interactive_app.py  # Interactive CLI
│       └── 📁 utils/                 # Utility functions
│           └── 🐍 __init__.py
├── 📁 data/                          # Data files
│   ├── 📊 9.xlsx                     # Data aktual kerja
│   ├── 📊 検査工数.xlsx               # Data standar N5
│   └── 📁 output/                    # Generated reports
├── 📁 tests/                         # Unit tests
│   ├── 🐍 __init__.py
│   ├── 🐍 test_gui_generate.py
│   ├── 🐍 test_gui_imports.py
│   └── 🐍 test_report_logic.py
├── 📁 docs/                          # Documentation
│   ├── 📝 PENJELASAN_SHEET.txt       # Penjelasan sheet
│   ├── 📝 consept.txt               # Konsep awal
│   ├── 📝 report.txt                # Format laporan
│   ├── 📝 FORMAT_IMPROVEMENTS.md    # History improvements
│   ├── 📝 GUI_GENERATE_FIX.md       # GUI fixes
│   └── 📝 GUI_OPTIMIZATIONS.md      # GUI optimizations
├── 📁 scripts/                       # Launcher scripts
│   ├── 🚀 run_gui.py                 # GUI launcher
│   ├── 🚀 run_cli.py                 # CLI launcher
│   └── 🗂️ main.py                    # Legacy main script
├── 📋 pyproject.toml                # Project configuration
├── 📋 setup.py                      # Package setup
├── 📋 requirements.txt              # Dependencies
├── 📋 README.md                     # Project documentation
├── 📋 LICENSE                       # MIT License
├── 📋 Makefile                      # Development tasks
├── 📋 .gitignore                    # Git ignore rules
├── 📋 .python-version               # Python version
└── 🗃️ uv.lock                       # uv lock file
```

## 🎯 Kenapa Struktur Ini?

### 1. **Modularity**
- **`src/`** - Source code terpisah dari data dan config
- **`core/`** - Business logic utama terpisah dari UI
- **`gui/`** - Interface logic terpisah
- **`utils/`** - Utility functions terpisah

### 2. **Python Best Practices**
- **Package structure** dengan `__init__.py`
- **Relative imports** yang tepat
- **Entry points** untuk CLI tools
- **Configuration files** terpisah

### 3. **Development Friendly**
- **`tests/`** - Testing terpisah dari source
- **`docs/`** - Dokumentasi terorganisir
- **`scripts/`** - Launcher scripts
- **`Makefile`** - Development tasks

### 4. **Production Ready**
- **`pyproject.toml`** - Modern Python packaging
- **`requirements.txt`** - Dependencies management
- **`.gitignore`** - Version control optimization
- **Setup configuration** untuk distribusi

## 🚀 Cara Penggunaan

### CLI Mode
```bash
# Install dependencies
uv sync

# Run CLI
python3 scripts/run_cli.py

# Atau dengan make
make run-cli
```

### GUI Mode
```bash
# Run GUI
python3 scripts/run_gui.py

# Atau dengan make
make run-gui
```

### Development
```bash
# Setup development environment
make setup-dev

# Run tests
make test

# Format code
make format

# Lint code
make lint
```

## 📝 File Configuration

### `pyproject.toml`
- Metadata project
- Dependencies
- Build configuration
- Development tools config

### `requirements.txt`
- Runtime dependencies
- Development dependencies
- Optional dependencies

### `Makefile`
- Common development tasks
- Build automation
- Testing commands

## 🔧 Import Paths

### Relative imports dalam package:
```python
from ...core.report_automation import ReportAutomation
```

### Absolute imports dari scripts:
```python
from src.report_automation.core.report_automation import ReportAutomation
```

## 📊 Data Flow

1. **Input**: `data/9.xlsx` + `data/検査工数.xlsx`
2. **Processing**: `src/report_automation/core/report_automation.py`
3. **Output**: `data/output/月次報告書_YYYY_MM.xlsx`
4. **Interface**: `src/report_automation/gui/` files

## 🎨 Fitur Tambahan

### 1. **Multiple Entry Points**
- CLI via `scripts/run_cli.py`
- GUI via `scripts/run_gui.py`
- Interactive via `src/report_automation/gui/interactive_app.py`

### 2. **Error Handling**
- Graceful fallback dari GUI ke CLI
- Comprehensive error messages
- Logging yang terstruktur

### 3. **Development Tools**
- Black untuk code formatting
- Flake8 untuk linting
- MyPy untuk type checking
- Pytest untuk testing

## 🌟 Best Practice Implementation

✅ **Separation of Concerns**: Logic, UI, dan Utils terpisah
✅ **Package Structure**: Mengikuti Python packaging standards
✅ **Documentation**: README, docs, dan inline documentation
✅ **Testing**: Test suite terpisah dan terorganisir
✅ **Configuration**: Centralized configuration management
✅ **Error Handling**: Robust error handling dan logging
✅ **Development Tools**: Linting, formatting, dan type checking
✅ **Distribution**: Ready untuk pip/uv distribution

Struktur ini mengikuti best practice Python project yang modern dan siap untuk production deployment!