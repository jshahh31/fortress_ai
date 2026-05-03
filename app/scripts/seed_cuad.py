import asyncio
import os
import json
import pandas as pd
from datasets import load_dataset
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from app.core.config import settings

async def seed_cuad_to_qdrant(limit: int = 10):
    """
    Seeds Qdrant with sample contracts from the CUAD dataset.
    This helps in demonstrating the search and analysis capabilities of Fortress AI.
    """
    print("Loading CUAD dataset...")
    # Using verification_mode="no_checks" to bypass metadata mismatches
    ds = load_dataset("theatticusproject/cuad", split="train", verification_mode="no_checks")
    
    print("Extracting text from PDF objects...")
    unique_contracts = []
    seen_prefixes = set()
    
    for i, item in enumerate(ds):
        if len(unique_contracts) >= limit:
            break
            
        pdf = item.get("pdf")
        if not pdf:
            continue
            
        # Extract text from PDF pages
        text = ""
        try:
            for page in pdf.pages:
                text += page.extract_text() or ""
        except Exception as e:
            print(f"Error extracting text from contract {i}: {e}")
            continue
            
        if text.strip() and text[:500] not in seen_prefixes:
            unique_contracts.append({"id": i, "text": text})
            seen_prefixes.add(text[:500])
            print(f"Extracted contract {len(unique_contracts)}/{limit}")

    # Initialize Qdrant client
    # Override for local script execution if using docker-internal name
    url = settings.QDRANT_URL
    if "qdrant" in url and "localhost" not in url and "127.0.0.1" not in url:
        url = "http://127.0.0.1:6333"
        
    client = QdrantClient(url=url)
    collection_name = settings.QDRANT_COLLECTION
    client.set_model("BAAI/bge-small-en-v1.5")
    
    for contract in unique_contracts:
        title = f"CUAD Contract {contract['id']}"
        print(f"Indexing: {title}...")
        
        client.add(
            collection_name=collection_name,
            documents=[contract["text"]],
            metadata=[{"title": title, "source": "CUAD", "type": "Legal Contract"}],
            ids=[contract["id"]]
        )
    
    print(f"Successfully seeded {len(unique_contracts)} contracts into Qdrant!")

if __name__ == "__main__":
    # Note: This script assumes Qdrant is running and accessible via settings.QDRANT_URL
    asyncio.run(seed_cuad_to_qdrant())
