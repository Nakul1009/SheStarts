# SheStarts 🌸

**SheStarts** is an empathetic, AI-powered multi-agent counseling platform designed to guide women restarting their professional journeys after a career break. Built on a robust orchestrator framework, SheStarts parses the candidate's profile and resume, analyzes market demand, scores employability, identifies skill gaps, and constructs a customized 30/60/90-day upskilling roadmap.

---

## 🌟 Key Features

- **Empathetic Career Counsel**: Specifically designed around returnships, remote suitability, and career gaps.
- **Multi-Agent Orchestration**: Powered by **LangGraph**, where specialized agents collaborate dynamically to build a unified profile.
- **Retrieval-Augmented Generation (RAG)**: Integrates market data from a **Chroma Vector Database** utilizing semantic search.
- **Employability Index & Score factors**: Evaluates candidate readiness across experience, skill relevance, market demand, time availability, and gap mitigation.
- **Dynamic Learning Roadmaps**: Generates custom 30/60/90-day learning plans with curated resource links (Coursera, Udemy, etc.).
- **Transparent Logging**: Real-time agent collaboration logs visible directly in the UI dashboard.

---

## ⚙️ Architecture & Agent Pipeline

SheStarts operates as a state-based multi-agent network orchestrated by a **Supervisor Node**.


### Specialized Agents
1. **Profiler Agent**: Extracts and aggregates form inputs and resume text (PDF/Docx) into a structured `UserProfile`.
2. **Recommender Agent**: Recommends 3–5 tailored career paths by pulling relevant market data using Chroma DB semantic searches.
3. **Skill Gap Agent**: Performs a detailed comparison of candidate skills against the target role, dividing them into matching and missing skills.
4. **Roadmap Agent**: Builds a targeted 30/60/90-day upskilling path with learning milestones and online resources.
5. **Scorer Agent**: Calculates a weighted employability score out of 100 with breakdowns on experience, skill relevance, market opportunities, commitment hours, and gap mitigation.
6. **Synthesizer Agent**: Merges all outputs into a final, unified career restart counseling guide.

---

## 🛠️ Technology Stack

- **Core**: Python 3.10+
- **Frontend**: Streamlit
- **Agent Orchestration**: LangGraph, LangChain
- **Vector Database**: Chroma DB (chromadb, langchain-chroma)
- **AI / LLM Integration**: 
  - NVIDIA NIM (`langchain-nvidia-ai-endpoints`)
  - **LLM**: `meta/llama-3.3-70b-instruct` (supports native structured Pydantic outputs)
  - **Embeddings**: `nvidia/nv-embedqa-e5-v5`

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- An active NVIDIA NIM API Key (Sign up at [NVIDIA API Catalog](https://build.nvidia.com/))

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd SheStarts
   ```

2. **Create a Virtual Environment & Install Dependencies**
   ```bash
   # Create environment
   python -m venv env

   # Activate environment (Windows)
   .\env\Scripts\activate

   # Activate environment (Mac/Linux)
   source env/bin/activate

   # Install requirements
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   NVIDIA_API_KEY=your_nvidia_api_key_here
   ```

4. **Initialize Vector Database (RAG Data)**
   Populate the Chroma vector store with initial counseling and market knowledge:
   ```bash
   python rag/build_db.py
   ```

5. **Run the Streamlit Application**
   ```bash
   streamlit run app.py
   ```

---

## 📁 Project Structure

```text
SheStarts/
│
├── agents/             # Multi-agent logic
│   ├── graph.py        # LangGraph StateGraph pipeline
│   ├── state.py        # Pydantic schemas and typed state dicts
│   ├── llm_helper.py   # ChatNVIDIA connection configuration
│   ├── profiler.py     # Profiler Agent
│   ├── recommender.py  # Recommender Agent (RAG query logic)
│   ├── skill_gap.py    # Skill Gap Agent
│   ├── roadmap.py      # Roadmap Agent
│   ├── scorer.py       # Scorer Agent
│   └── synthesizer.py  # Synthesizer Agent
│
├── rag/                # Retrieval-augmented generation
│   ├── build_db.py     # Database initialization script
│   ├── data.py         # Baseline market and returnship data
│   └── chroma_db/      # Persisted Chroma database folder (auto-generated)
│
├── app.py              # Main Streamlit web application
├── requirements.txt    # Python dependencies list
└── README.md           # Project documentation
```
