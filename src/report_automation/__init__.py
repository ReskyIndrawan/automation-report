"""
Report Automation Package

A Python application for automated monthly report generation
comparing actual work data with N5 standards.
"""

__version__ = "2.0.0"
__author__ = "Report Automation Team"
__email__ = "support@company.com"

from .core.report_automation import ReportAutomation

__all__ = ["ReportAutomation"]