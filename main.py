import os
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
import pandas as pd

load_dotenv()
Settings.llm = OpenAI()

documents = []
for file in ["data/Population.csv", "data/PopulationProjection.csv"]:
    try:
        df = pd.read_csv(file, encoding='latin1', sep=';')
        # Clean column names and data
        df.columns = df.columns.str.strip().str.replace('"', '')
        df = df.apply(lambda x: x.str.strip().str.replace('"', '') if isinstance(x, pd.Series) else x)
        text = df.to_string(index=False)
        documents.append(Document(text=text))
    except Exception as e:
        print(f"Error reading {file}: {e}")

index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

res = input("Enter your query: ")
response = query_engine.query(res)
print(response)