"""
Custom Reporting System for Screenshots and Videos
Organizes reports by date and test case with proper naming conventions
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class TestReportManager:
    """Manages test execution reports with organized folder structure and naming conventions."""

    def __init__(self, base_report_dir: str = "reports"):
        """
        Initialize the report manager.
        
        Args:
            base_report_dir: Base directory for all reports
        """
        self.base_report_dir = Path(base_report_dir)
        self.execution_date = datetime.now().strftime("%Y-%m-%d")
        self.execution_time = datetime.now()
        self.date_folder = self.base_report_dir / self.execution_date
        
        # Create date folder if it doesn't exist
        self.date_folder.mkdir(parents=True, exist_ok=True)

    def get_test_folder(self, test_name: str) -> Path:
        """
        Get or create the folder for a specific test case.
        
        Args:
            test_name: Name of the test case
            
        Returns:
            Path to the test case folder
        """
        # Clean test name (remove module paths and parameters)
        clean_test_name = test_name.split("::")[-1].split("[")[0]
        test_folder = self.date_folder / clean_test_name
        test_folder.mkdir(parents=True, exist_ok=True)
        return test_folder

    def get_screenshot_filename(self, test_name: str) -> str:
        """
        Generate screenshot filename with test name and timestamp.
        
        Args:
            test_name: Name of the test case
            
        Returns:
            Filename for screenshot with timestamp
        """
        clean_test_name = test_name.split("::")[-1].split("[")[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        return f"{clean_test_name}_{timestamp}.png"

    def get_video_filename(self, test_name: str) -> str:
        """
        Generate video filename with test name and timestamp.
        
        Args:
            test_name: Name of the test case
            
        Returns:
            Filename for video with timestamp
        """
        clean_test_name = test_name.split("::")[-1].split("[")[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        return f"{clean_test_name}_{timestamp}.webm"

    def save_screenshot(self, page, test_name: str) -> Path:
        """
        Save screenshot for a test case with proper naming and folder structure.
        
        Args:
            page: Playwright page object
            test_name: Name of the test case
            
        Returns:
            Path to saved screenshot
        """
        test_folder = self.get_test_folder(test_name)
        screenshots_folder = test_folder / "screenshots"
        screenshots_folder.mkdir(parents=True, exist_ok=True)
        
        filename = self.get_screenshot_filename(test_name)
        filepath = screenshots_folder / filename
        
        page.screenshot(path=str(filepath))
        return filepath

    def get_report_structure_info(self) -> dict:
        """
        Get information about the current report structure.
        
        Returns:
            Dictionary with report structure info
        """
        return {
            "base_directory": str(self.base_report_dir),
            "execution_date": self.execution_date,
            "date_folder": str(self.date_folder),
            "structure": "reports/YYYY-MM-DD/test_case_name/screenshots/[test_case_name_YYYYMMDD_HHMMSS_mmm.png]"
        }


def get_test_report_manager(base_dir: str = "reports") -> TestReportManager:
    """Factory function to get report manager instance."""
    return TestReportManager(base_dir)
