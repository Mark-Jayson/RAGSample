import os
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
import pandas as pd
import numpy as np
from typing import List, Optional, Tuple
import chardet
import logging
import warnings
import getpass
import nest_asyncio
from llama_parse import LlamaParse
import json

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

    def read_file_with_description(self, file_path: str, encoding: str, delimiter: str) -> Tuple[str, str, pd.DataFrame]:
        """Read CSV file, extract the description from the first row, and a link from the second row."""
        # Open the file
        with open(file_path, 'r', encoding=encoding) as file:
            # Read the first line as description
            description = file.readline().strip().replace('"', '')
            
            # Read the second line as the link
            # link = file.readline().strip()
        
        # Read the rest of the file as DataFrame, skipping the first two rows
        df = pd.read_csv(file_path, encoding=encoding, sep=delimiter, skiprows=2, on_bad_lines='warn')
        
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
    """Process multiple CSV files and store metadata externally."""
    csv_handler = CSVHandler()
    documents = []
    metadata_dir = "metadata"

    # Ensure metadata directory exists
    os.makedirs(metadata_dir, exist_ok=True)

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
            
            # Metadata for external storage
            detailed_metadata = {
                "source": file_path,
                "description": description,
                "warnings": warnings,
                "encoding": encoding,
                "delimiter": delimiter,
                "num_rows": len(df),
                "num_columns": len(df.columns),
                "column_names": list(df.columns),
            }
            
            # Save detailed metadata to a JSON file
            metadata_filename = os.path.join(metadata_dir, f"{Path(file_path).stem}_metadata.json")
            with open(metadata_filename, "w") as metadata_file:
                json.dump(detailed_metadata, metadata_file, indent=4)
            
            # Create a reference to the metadata file in the Document object
            text = f"File Description: {description}\n\nData:\n{df.to_string(index=False)}"
            document = Document(
                text=text,
                metadata={
                    "source": file_path,
                    "description": description[:200],  # Truncated description
                    "metadata_reference": metadata_filename  # External reference
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

    

    PERSIST_DIR = "./storage"
    if not os.path.exists(PERSIST_DIR):
    # load the documents and create the index
        data_folder = "data"
        csv_files = [os.path.join(data_folder, file) for file in os.listdir(data_folder) if os.path.isfile(os.path.join(data_folder, file))]
        documents = process_csv_files(csv_files)
        if documents:
            # Print descriptions of processed files
            print("\nProcessed Files:")
            for doc in documents:
                try:
                    # Load external metadata
                    metadata_reference = doc.metadata.get("metadata_reference")
                    if metadata_reference and os.path.exists(metadata_reference):
                        with open(metadata_reference, "r") as metadata_file:
                            detailed_metadata = json.load(metadata_file)
                    else:
                        detailed_metadata = {}  # Fallback if metadata file is missing

                    # Extract data from the external metadata
                    source = detailed_metadata.get("source", "Unknown")
                    description = doc.metadata.get("description", "No description available")
                    num_rows = detailed_metadata.get("num_rows", "N/A")
                    num_columns = detailed_metadata.get("num_columns", "N/A")
                    warnings = detailed_metadata.get("warnings", [])

                    # Print the file details
                    print(f"\nFile: {source}")
                    print(f"Description: {description}")
                    print(f"Rows: {num_rows}")
                    print(f"Columns: {num_columns}")
                    print("Warnings:", warnings)
                    print("-" * 50)

                except Exception as e:
                    print(f"Error loading metadata for document: {str(e)}")
                    continue
        else:
            logger.error("No documents were successfully processed")
        index = VectorStoreIndex.from_documents(documents)
        # store it for later
        index.storage_context.persist(persist_dir=PERSIST_DIR)

    else:
    # load the existing index
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
   
    
    

        
    query_engine = index.as_query_engine()

    while True:
        res = input("\nEnter your query (or 'quit' to exit): ")
        if res.lower() == 'quit':
            break
        response = query_engine.query(res)
        print("\nResponse:", response)


if __name__ == "__main__":
    main()