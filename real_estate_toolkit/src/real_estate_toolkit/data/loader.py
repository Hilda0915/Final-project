from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Union
import csv
import re

class Cleaner:
    def __init__(self, data):
        """
        Initialize the Cleaner with loaded data.

        Args:
            data (List[Dict[str, Any]]): The dataset to be cleaned, as a list of dictionaries.
        """
        print("Cleaner initialized with data:")
        print(data[:5])  # Debugging: Show a sample of data
        if not data:
            raise ValueError("Data cannnot be empty or None.")
        self.data = data

    def rename_with_best_practices(self):
        """
        Rename columns to follow snake_case naming conventions.
        """
        if not self.data:
            raise ValueError("Data is empty or None.")
        print("Before renaming columns:", self.data[:5])
        for row in self.data:
            row.update({key.lower(): row.pop(key) for key in list(row.keys())})
        print("After renaming columns:", self.data[:5])

    def na_to_none(self):
        """
        Replace 'NA', 'N/A', 'null', or empty string values with None.
        """
        if not self.data:
            raise ValueError("Data is empty or None.")
        print("Before cleaning NA values:", self.data[:5])
        for row in self.data:
            for key, value in row.items():
                if value in ["NA", "N/A", "null", ""]:
                    row[key] = None
        print("After cleaning NA values:", self.data[:5])
        return self.data
@dataclass
class DataLoader:
    """Class for loading and basic processing of real estate data."""
    data_path: Union[Path, str]  # Accept either a Path or string

    def __init__(self, data_dir):
        """
        Initialize the DataLoader with a directory containing data files.

        Args:
            data_dir (Path): Path object pointing to the directory containing CSV files.
        """
        self.data_dir = data_dir
        print(f"DataLoader initialized with data_dir: {self.data_dir}")
    def __post_init__(self):
        # Ensure data_path is a Path object
        if isinstance(self.data_path, str):
            self.data_path = Path(self.data_path)

    def load_data_from_csv(self, file_name: str) -> List[Dict[str, Any]]:
        """
        Load data from a specific CSV file into a list of dictionaries.

        Args:
            file_name (str): Name of the CSV file to load.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries where each dictionary represents a row.
        """
        data = []
        file_path = self.data_dir / file_name  # Combine the base path and file name
        if not file_path.is_file():
            raise FileNotFoundError(f"CSV File {file_name} does not exist at {file_path}.")
        print("Loading CSV data from:", file_path)

        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)  # Automatically maps columns to values
                data = [row for row in reader]  # Convert reader object to a list of dictionaries
                print(f"Loaded {len(data)} rows from {file_name}.")
                if not data:
                    raise ValueError(f"No data found in {file_name}.")
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {file_name} does not exist at {self.data_dir}.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while reading {file_name}: {e}")
        return data
        

    def validate_columns(self, file_name: str, required_columns: List[str]) -> bool:
        """
        Validate that the specified CSV file contains all required columns.

        Args:
            file_name (str): Name of the CSV file to validate.
            required_columns (List[str]): List of column names that are required.
        
        Returns:
            bool: True if all required columns are present, False otherwise.
        """
        file_path = self.data_dir / file_name  # Combine the base path and file name

        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)  # Extract header from the first row
            
            return all(col in header for col in required_columns)  # Check required columns
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {file_name} does not exist at {self.data_dir}.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while validating {file_name}: {e}")
    
    def infer_and_convert_types(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Infer and convert column data types for numeric columns.

        Args:
            data: List of dictionaries where each dictionary represents a row.

        Returns:
            List of dictionaries with numeric values converted to appropriate types.
        """
        for row in data:
            for column, value in row.items():
                # Skip None or empty values
                if value is None or value == "":
                    continue
                try:
                    # Convert to float if it has a decimal point, else int
                    if "." in value:
                        row[column] = float(value)
                    else:
                        row[column] = int(value)
                except ValueError:
                    pass  # Leave non-numeric values as-is
        return data
    
    def is_valid_snake_case(string: str) -> bool:
        """
        Check if a string follows snake_case naming convention.

        Args:
            string (str): String to validate.

        Returns:
            bool: True if the string is in snake_case, False otherwise.
        """
        return bool(re.match(r'^[a-z_][a-z0-9_]*$', string))
