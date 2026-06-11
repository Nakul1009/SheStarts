# SheStarts RAG Database Setup

This folder contains the code and data to build and query a localized vector database for our RAG (Retrieval-Augmented Generation) system.

## Dataset Contents
The database embeds two types of records:
1. **Returnship Programs**: Structured restart roles for women (Tata, Amazon, Capgemini, IBM, Microsoft, Goldman Sachs).
2. **In-Demand Skills**: Transition paths and skills suitable for women returning to the workforce (AI & Prompt Engineering, Data Analytics, Digital Marketing, Technical Writing, HR, No-Code).

## Setup & API Key
Before running the scripts, make sure the `NVIDIA_API_KEY` is configured in the parent directory's `.env` file:
```env
NVIDIA_API_KEY=nvapi-your-key-here
```

## How to Build the Database
Run the build script from the project root folder. It will fetch the data from `data.py`, call the NVIDIA embedding model, and write to a persistent Chroma database in `rag/chroma_db/`:

```bash
python rag/build_db.py
```

## How to Query the Database
You can query the database using the verification script. Provide your search term as a command-line argument:

```bash
python rag/query_db.py "remote digital marketing and data analytics"
```

If no argument is provided, the script runs a default search query for: `"structured returnships for women in India"`.

## Integration in Python Code
You can retrieve relevant documents in your application logic (e.g. streamlit pages or counselor agents) like this:

```python
import os
import dotenv
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_chroma import Chroma

# Load environment
dotenv.load_dotenv()

# Initialize embeddings
embeddings = NVIDIAEmbeddings(
    model="nvidia/embeddings-nv-embed-qa-4",
    model_type="query"
)

# Load the vector store
db = Chroma(
    persist_directory="rag/chroma_db",
    embedding_function=embeddings
)

# Perform similarity search
results = db.similarity_search("your query here", k=3)
for doc in results:
    print(doc.page_content)
```
