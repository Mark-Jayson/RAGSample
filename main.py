import os
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
import pandas as pd
import numpy as np
from typing import List, Optional, Tuple
import chardet
import logging
import warnings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVHandler:
    def __init__(self):
        self.supported_encodings = ['utf-8', 'latin1', 'utf-16', 'ascii', 'iso-8859-1']
        self.possible_delimiters = [';', ',', '\t', '|']

    def detect_encoding(self, file_path: str) -> str:
        """Detect the file encoding."""
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            return result['encoding']

    def detect_delimiter(self, file_path: str, encoding: str) -> str:
        """Detect the CSV delimiter."""
        with open(file_path, 'r', encoding=encoding) as file:
            header = file.readline()
            for delimiter in self.possible_delimiters:
                if delimiter in header:
                    return delimiter
        return ','  # Default to comma if no other delimiter is found

    def read_file_with_description(self, file_path: str, encoding: str, delimiter: str) -> Tuple[str, pd.DataFrame]:
        """Read CSV file and extract the description from first row."""
        # Read the first line separately as description
        with open(file_path, 'r', encoding=encoding) as file:
            description = file.readline().strip().replace('"', '')
        
        # Read the rest of the file as DataFrame, skipping the description row
        df = pd.read_csv(file_path, encoding=encoding, sep=delimiter, skiprows=1, on_bad_lines='warn')
        
        return description, df

    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize column names."""
        df.columns = df.columns.map(lambda x: str(x)  # Convert to string
            .strip()  # Remove leading/trailing spaces
            .lower()  # Convert to lowercase
            .replace('"', '')  # Remove quotes
            .replace("'", "")  # Remove single quotes
            .replace(" ", "_")  # Replace spaces with underscores
            .replace("-", "_")  # Replace hyphens with underscores
            .replace(r"[^\w\s]", "")  # Remove special characters
        )
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean data in all columns based on their data types."""
        # Handle string (object) columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(lambda x: self._clean_string(x))
            
            # Try to convert string columns to numeric if possible
            try:
                numeric_conversion = pd.to_numeric(df[col], errors='coerce')
                if numeric_conversion.notna().all():
                    df[col] = numeric_conversion
            except:
                pass

        # Handle numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Handle date columns
        df = self._convert_date_columns(df)

        return df

    def _clean_string(self, value) -> str:
        """Clean individual string values."""
        if pd.isna(value):
            return np.nan
        try:
            value = str(value)
            value = value.strip()
            value = value.replace('"', '')
            value = value.replace('\n', ' ')
            value = value.replace('\r', ' ')
            value = ' '.join(value.split())  # Remove multiple spaces
            return value if value else np.nan
        except:
            return np.nan

    def _convert_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Attempt to convert columns that look like dates to datetime."""
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # Try to convert to datetime
                    date_series = pd.to_datetime(df[col], errors='coerce')
                    # If most values were converted successfully, keep the conversion
                    if date_series.notna().sum() > 0.5 * len(date_series):
                        df[col] = date_series
                except:
                    continue
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values based on column type."""
        # For numeric columns, fill NaN with median
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].median())

        # For categorical/string columns, fill NaN with mode
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown')

        return df

    def validate_data(self, df: pd.DataFrame) -> List[str]:
        """Validate data and return list of warnings."""
        warnings = []
        
        # Check for duplicate columns
        if any(df.columns.duplicated()):
            warnings.append("Duplicate column names found")
        
        # Check for too many missing values
        missing_percentages = df.isnull().sum() / len(df) * 100
        cols_with_many_missing = missing_percentages[missing_percentages > 50].index.tolist()
        if cols_with_many_missing:
            warnings.append(f"Columns with >50% missing values: {cols_with_many_missing}")

        # Check for potential data type mismatches
        for col in df.columns:
            unique_values = df[col].nunique()
            if df[col].dtype == 'object' and unique_values < 10:
                warnings.append(f"Column {col} might be better as categorical")

        return warnings

def process_csv_files(file_paths: List[str]) -> List[Document]:
    """Process multiple CSV files and return list of Documents for LlamaIndex."""
    csv_handler = CSVHandler()
    documents = []

    for file_path in file_paths:
        try:
            # Detect file encoding and delimiter
            encoding = csv_handler.detect_encoding(file_path)
            delimiter = csv_handler.detect_delimiter(file_path, encoding)
            
            logger.info(f"Processing {file_path} with encoding {encoding} and delimiter {delimiter}")
            
            # Read the CSV file with description
            description, df = csv_handler.read_file_with_description(file_path, encoding, delimiter)
            
            # Clean and process the data
            df = csv_handler.clean_column_names(df)
            df = csv_handler.clean_data(df)
            df = csv_handler.handle_missing_values(df)
            
            # Validate data and log warnings
            warnings = csv_handler.validate_data(df)
            for warning in warnings:
                logger.warning(f"{file_path}: {warning}")
            
            # Convert to string for LlamaIndex
            text = f"File Description: {description}\n\nData:\n{df.to_string(index=False)}"
            
            # Create document with metadata
            document = Document(
                text=text,
                metadata={
                    "source": file_path,
                    "description": description,
                    "warnings": warnings,
                    "encoding": encoding,
                    "delimiter": delimiter,
                    "num_rows": len(df),
                    "num_columns": len(df.columns),
                    "column_names": list(df.columns)
                }
            )
            documents.append(document)
            
            logger.info(f"Successfully processed {file_path}")
            logger.info(f"Description: {description}")
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            continue

    return documents

# Main execution
def main():
    load_dotenv()
    Settings.llm = OpenAI()

    csv_files = ["data/Population.csv", "data/PopulationProjection.csv", "data/2020CensusAndPopulation.csv", "data/Household.csv"]
    documents = process_csv_files(csv_files)

    if documents:
        # Print descriptions of processed files
        print("\nProcessed Files:")
        for doc in documents:
            print(f"\nFile: {doc.metadata['source']}")
            print(f"Description: {doc.metadata['description']}")
            print(f"Rows: {doc.metadata['num_rows']}")
            print(f"Columns: {doc.metadata['num_columns']}")
            if doc.metadata['warnings']:
                print("Warnings:", doc.metadata['warnings'])
            print("-" * 50)

        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()

        while True:
            res = input("\nEnter your query (or 'quit' to exit): ")
            if res.lower() == 'quit':
                break
            response = query_engine.query(res)
            print("\nResponse:", response)
    else:
        logger.error("No documents were successfully processed")

if __name__ == "__main__":
    main()