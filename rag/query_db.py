import os
import sys
import dotenv
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_chroma import Chroma

def query_vector_db(query_text: str, k: int = 3):
    print("Initializing environment...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, "..", ".env")
    dotenv.load_dotenv(env_path)
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("ERROR: NVIDIA_API_KEY environment variable is not set. Please define it in your .env file.")
        sys.exit(1)
        
    persist_dir = os.path.join(base_dir, "chroma_db")
    if not os.path.exists(persist_dir):
        print(f"ERROR: Chroma DB directory not found at: {persist_dir}")
        print("Please run build_db.py first to create the database.")
        sys.exit(1)
        
    print("Connecting to NVIDIA NIM Embedding Service...")
    try:
        embeddings = NVIDIAEmbeddings(
            model="nvidia/nv-embedqa-e5-v5",
            nvidia_api_key=api_key,
            model_type="query"  # Specifically for query searches
        )
    except Exception as e:
        print(f"Failed to initialize embeddings with model 'nvidia/nv-embedqa-e5-v5'. Error: {e}")
        print("Attempting fallback with default model initialization...")
        embeddings = NVIDIAEmbeddings(nvidia_api_key=api_key)
        
    print(f"Loading Chroma DB from: {persist_dir}")
    db = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )
    
    print(f"\nQuery: '{query_text}'")
    print(f"Retrieving top {k} matches...")
    
    results = db.similarity_search_with_score(query_text, k=k)
    
    print("\n--- Search Results ---")
    for i, (doc, score) in enumerate(results):
        print(f"\n[{i+1}] Distance Score (lower is closer): {score:.4f}")
        # Strip the Title prefix we added during ingestion if we print page_content,
        # or just print the document metadata and content directly
        print(f"Title: {doc.metadata.get('title')}")
        print(f"Category: {doc.metadata.get('category')}")
        print(f"Content: {doc.page_content.strip()}")
        print(f"All Metadata: {doc.metadata}")
        
if __name__ == "__main__":
    # If command line arguments are provided, use them as the query
    default_query = "structured returnships for women in India"
    if len(sys.argv) > 1:
        query_str = " ".join(sys.argv[1:])
    else:
        query_str = default_query
        
    query_vector_db(query_str)
