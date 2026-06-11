import os
import sys
import shutil
import dotenv
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Add current directory to path for relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data import DATA

def build_vector_db():
    print("Initializing environment...")
    # Load .env file from the parent directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, "..", ".env")
    dotenv.load_dotenv(env_path)
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("ERROR: NVIDIA_API_KEY environment variable is not set. Please define it in your .env file.")
        sys.exit(1)
        
    print("Connecting to NVIDIA NIM Embedding Service...")
    # Use the standard NVIDIA QA embedding model
    try:
        embeddings = NVIDIAEmbeddings(
            model="nvidia/nv-embedqa-e5-v5",
            nvidia_api_key=api_key,
            model_type="passage"  # Specifically for indexing passage data
        )
    except Exception as e:
        print(f"Failed to initialize embeddings with model 'nvidia/nv-embedqa-e5-v5'. Error: {e}")
        print("Attempting fallback with default model initialization...")
        embeddings = NVIDIAEmbeddings(nvidia_api_key=api_key)
        
    # Prepare documents
    print(f"Preparing {len(DATA)} documents for vectorization...")
    documents = []
    for i, item in enumerate(DATA):
        # Formulate a structured string for semantic searching
        text_content = f"Title: {item['title']}\nContent: {item['content']}"
        
        # Merge metadata nicely
        metadata = {
            "source_index": i,
            "title": item["title"]
        }
        if "metadata" in item:
            for k, v in item["metadata"].items():
                metadata[k] = v
                
        doc = Document(page_content=text_content, metadata=metadata)
        documents.append(doc)
        
    persist_dir = os.path.join(base_dir, "chroma_db")
    print(f"Persisting Chroma DB to: {persist_dir}")
    
    # Clean up existing database directory if it exists to start fresh
    if os.path.exists(persist_dir):
        print("Removing existing Chroma database directory to rebuild...")
        try:
            shutil.rmtree(persist_dir)
        except Exception as e:
            print(f"Warning: Could not remove directory {persist_dir}: {e}")
            
    try:
        db = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_dir
        )
        print("Chroma DB successfully created and persisted!")
        print(f"Total documents added: {len(DATA)}")
    except Exception as e:
        print(f"ERROR: Failed to write to Chroma DB. Details: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_vector_db()
