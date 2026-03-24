import csv
import os
from typing import Dict, List, Any
from .data_provider_interface import DataProviderInterface


class CsvDataProvider(DataProviderInterface):
    """Data provider for CSV files."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_data(self) -> List[Dict[str, Any]]:
        """Load data from CSV file."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")

        data = []
        with open(self.file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data

    def save_data(self, data: List[Dict[str, Any]]) -> None:
        """Save data to CSV file."""
        if not data:
            return

        fieldnames = data[0].keys()
        with open(self.file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)