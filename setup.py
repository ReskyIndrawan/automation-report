"""
Setup configuration for Report Automation Package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="report-automation",
    version="2.0.0",
    author="Report Automation Team",
    author_email="support@company.com",
    description="Automated monthly report generation comparing actual work data with N5 standards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/company/report-automation",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
        # tkinter is built-in with Python, no external package needed
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "report-gui=src.report_automation.gui.gui_app:main",
            "report-cli=src.report_automation.gui.simple_generate:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.xlsx"],
    },
)