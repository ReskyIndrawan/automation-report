#!/usr/bin/env python3
"""
CLI Launcher for Report Automation
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.report_automation.gui.simple_generate import main as cli_main

def main():
    """Main function for CLI entry point"""
    cli_main()

if __name__ == "__main__":
    main()