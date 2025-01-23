from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import os
import json
import chardet
import logging
import pandas as pd
import numpy as np
from typing import List, Optional, Tuple
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    Document,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core import Settings
from llama_index.llms.groq import Groq
from sentence_transformers import SentenceTransformer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        return ','

    def read_file_with_description(self, file_path: str, encoding: str, delimiter: str) -> Tuple[str, str, pd.DataFrame]:
        """Read CSV file and extract description."""
        with open(file_path, 'r', encoding=encoding) as file:
            description = file.readline().strip().replace('"', '')
        
        df = pd.read_csv(file_path, encoding=encoding, sep=delimiter, skiprows=2, on_bad_lines='warn')
        return description, df

    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize column names."""
        df.columns = df.columns.map(lambda x: str(x)
            .strip()
            .lower()
            .replace('"', '')
            .replace("'", "")
            .replace(" ", "_")
            .replace("-", "_")
            .replace(r"[^\w\s]", "")
        )
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean data in all columns."""
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(lambda x: self._clean_string(x))
            try:
                numeric_conversion = pd.to_numeric(df[col], errors='coerce')
                if numeric_conversion.notna().all():
                    df[col] = numeric_conversion
            except:
                pass

        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df = self._convert_date_columns(df)
        return df

    def _clean_string(self, value) -> str:
        """Clean individual string values."""
        if pd.isna(value):
            return np.nan
        try:
            value = str(value).strip().replace('"', '').replace('\n', ' ').replace('\r', ' ')
            return ' '.join(value.split()) if value else np.nan
        except:
            return np.nan

    def _convert_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert date-like columns to datetime."""
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    date_series = pd.to_datetime(df[col], errors='coerce')
                    if date_series.notna().sum() > 0.5 * len(date_series):
                        df[col] = date_series
                except:
                    continue
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the DataFrame."""
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].median())

        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown')

        return df

def process_csv_files(file_paths: List[str]) -> List[Document]:
    """Process multiple CSV files and create documents."""
    csv_handler = CSVHandler()
    documents = []
    metadata_dir = "metadata"
    os.makedirs(metadata_dir, exist_ok=True)

    for file_path in file_paths:
        try:
            encoding = csv_handler.detect_encoding(file_path)
            delimiter = csv_handler.detect_delimiter(file_path, encoding)
            
            description, df = csv_handler.read_file_with_description(file_path, encoding, delimiter)
            
            df = csv_handler.clean_column_names(df)
            df = csv_handler.clean_data(df)
            df = csv_handler.handle_missing_values(df)
            
            detailed_metadata = {
                "source": file_path,
                "description": description,
                "encoding": encoding,
                "delimiter": delimiter,
                "num_rows": len(df),
                "num_columns": len(df.columns),
                "column_names": list(df.columns)
                
            }
            
            metadata_filename = os.path.join(metadata_dir, f"{Path(file_path).stem}_metadata.json")
            with open(metadata_filename, "w") as metadata_file:
                json.dump(detailed_metadata, metadata_file, indent=4)
            
            text = f"File Description: {description}\n\nData:\n{df.to_string(index=False)}"
            document = Document(
                text=text,
                metadata={
                    "source": file_path,
                    "description": description[:200],
                    "metadata_reference": metadata_filename
                }
            )
            documents.append(document)
            logger.info(f"Successfully processed {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            continue

    return documents

# Initialize LlamaIndex components
def initialize_index():
    load_dotenv()
    PERSIST_DIR = "./storage"
    DATA_FOLDER = "./data"  # Ensure this path is correct
    
    try:
        # Validate API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Groq API key is missing. Please check your .env file.")
        
        # Initialize LLM and Embedding Model
        llm = Groq(model="llama3-70b-8192", api_key=api_key)
        Settings.llm = llm
        
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.embed_model = embed_model

        # Check if data folder exists
        if not os.path.exists(DATA_FOLDER):
            raise FileNotFoundError(f"Data folder not found: {DATA_FOLDER}")

        # Find CSV files
        csv_files = [
            os.path.join(DATA_FOLDER, file) 
            for file in os.listdir(DATA_FOLDER) 
            if file.endswith('.csv')
        ]
        
        if not csv_files:
            raise ValueError(f"No CSV files found in {DATA_FOLDER}")

        # Process documents
        documents = process_csv_files(csv_files)
        
        if not documents:
            raise ValueError("No valid documents were processed")

        # Create or load index
        if not os.path.exists(PERSIST_DIR):
            os.makedirs(PERSIST_DIR, exist_ok=True)
            index = VectorStoreIndex.from_documents(documents, show_progress=True)
            index.storage_context.persist(persist_dir=PERSIST_DIR)
        else:
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
        
        return index
    
    except Exception as e:
        logger.error(f"Index initialization error: {str(e)}", exc_info=True)
        raise

# Initialize only once
try:
    index = initialize_index()
    query_engine = index.as_query_engine()
except Exception as e:
    logger.error(f"Failed to initialize index and query engine: {str(e)}")
    index = None
    query_engine = None

class Query(BaseModel):
    text: str

@app.post("/api/chat")
async def chat(query: Query):
    try:
        response = query_engine.query(query.text)
        return {"response": str(response)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def root():
    return Path("static/conversation.html").read_text()

# Run with: uvicorn main:app --reload