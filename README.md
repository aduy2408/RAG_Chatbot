# APEC 2025 Korea RAG Chatbot

A multilingual Retrieval-Augmented Generation (RAG) chatbot system for APEC 2025 Korea events, built with FastAPI backend and Streamlit frontend.

## Architecture Overview

```
Web Scraping → Data  → Processing →Chunking → Embeddings → ChromaDB → Backend → Frontend
```

### Components:
- **Backend**: FastAPI with multilingual RAG processing
- **Frontend**: Streamlit web interface
- **Models**: E5 multilingual embeddings + Gemini 2.0 Flash LLM
- **Database**: ChromaDB vector store
- **Languages**: Vietnamese and English support

## Project Structure

```
├── README.md                    # Project documentation
├── requirements_api.txt         # Dependencies
├── start_api.py                # Main API startup script (root)
├── start_frontend.py           # Main frontend startup script (root)
├── Notebook files(for data scraping, processing and embedding)/
│   ├── RAG_LLM_Integration.ipynb    # Model integration
│   ├── RAG_Prep.ipynb              # Data preparation
│   ├── RAG_Test_Embedding.ipynb    # Embedding testing
│   └── Scraper.ipynb              # Web scraping
├── backend/                    # Backend directory
│   ├── .env                   # Environment variables
│   ├── modules/               # Core modules
│   │   ├── chatbot_core.py   # RAG logic and model handling
│   │   ├── config.py         # Configuration and styling
│   │   ├── ui_components.py  # Streamlit UI components
│   │   └── utils.py          # Utility functions
│   ├── api_backend/          # API backend service
│   │   ├── api_backend.py    # FastAPI backend service
│   │   ├── app_api.py        # Streamlit frontend (API version)
│   │   └── start_api_backend.py # Backend startup script
│   └── chroma_db_langchain_e5/ # Vector database storage
├── data/processed/            # Processed documents and embeddings
├── demo/                      # Demo startup scripts
│   └── start_frontend.py     # Demo frontend startup
└── direct loading/           # Original direct loading version
    ├── app.py               # Direct model loading app
    └── run_app.py           # Direct loading startup
```

## Quick Start

### Prerequisites
```bash
pip install -r requirements_api.txt
```

### Environment Setup
Create `.env` file in the `backend/` directory:
```
GOOGLE_API_KEY=your_google_api_key_here
```

### 1. Start API Backend
```bash
# From root directory
python start_api.py

# Or directly from backend directory
python backend/api_backend/start_api_backend.py
```
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

### 2. Start Frontend
```bash
# From root directory
python start_frontend.py

# Or directly from demo directory
python demo/start_frontend.py
```
- Frontend: `http://localhost:8502`

## Data Pipeline

### 1. Data Collection (`Scraper.ipynb`)
- Web scraping of APEC 2025 content
- Content extraction and cleaning
- Metadata preservation

### 2. Data Processing (`RAG_Development.ipynb`)
```python
# Document processing pipeline
Raw Text → Cleaning → Chunking → Metadata Addition
```

Key Features:
- Recursive character text splitting
- Table preservation logic
- Chunk size: 1000 characters
- Overlap: 200 characters
- Minimum chunk size: 200 characters

### 3. Embedding Generation (`RAG_Test_Embedding.ipynb`)
```python
# E5 multilingual embeddings with task prefixes
Documents: "passage: {content}"
Queries: "query: {question}"
```

Model: `intfloat/multilingual-e5-large`
- Supports Vietnamese and English
- 1024-dimensional embeddings
- Optimized for multilingual retrieval

### 4. Vector Database Setup
```python
# ChromaDB with persistent storage
vectorstore = Chroma(
    persist_directory="./chroma_db_langchain_e5",
    embedding_function=embeddings
)
```

## RAG System

### Core Components (`modules/chatbot_core.py`)

#### Language Detection
```python
def detect_language(text):
    # Combines langdetect with Vietnamese character detection
    # Returns: 'vi' or 'en'
```

#### Multilingual Prompts
- **Vietnamese**: Specialized prompt for Vietnamese responses
- **English**: Optimized prompt for English responses
- **Context-aware**: Includes specific instructions for table data

#### Retrieval Process
1. **Query Processing**: Language detection + task prefix
2. **Vector Search**: Similarity search in ChromaDB
3. **Context Assembly**: Top-k relevant documents
4. **LLM Generation**: Gemini 2.0 Flash with language-specific prompts

## API Endpoints

### `POST /chat`
Main RAG endpoint for chat responses.

**Request**:
```json
{
  "message": "What are the main APEC 2025 events?",
  "auto_detect": true,
  "preferred_language": "vi",
  "top_k": 5
}
```

**Response**:
```json
{
  "answer": "APEC 2025 sẽ có các sự kiện chính...",
  "sources": [
    {
      "title": "APEC 2025 Schedule",
      "url": "https://...",
      "contains_table": false,
      "chunk_length": 850,
      "content_preview": "..."
    }
  ],
  "num_sources": 3,
  "detected_language": "vi",
  "response_time": 1.23
}
```

### `POST /suggestions`
Context-aware follow-up suggestions.

**Request**:
```json
{
  "response_content": "APEC 2025 events include...",
  "language": "en"
}
```

**Response**:
```json
{
  "suggestions": [
    "What are the most important meetings?",
    "Who will attend these events?",
    "How to register for participation?"
  ]
}
```

### Other Endpoints
- `GET /` - Health check
- `GET /health` - Detailed system status
- `GET /languages` - Supported languages

## Frontend Features

### Streamlit Interface (`app_api.py`)
- **Multilingual UI**: Vietnamese and English support
- **Auto-suggestions**: Context-aware follow-up questions
- **Source Attribution**: Expandable source documents
- **Language Detection**: Visual language indicators
- **Mobile-responsive**: Custom CSS for mobile devices

### UI Components (`modules/ui_components.py`)
- Chat message rendering
- Source document display
- Auto-suggestion buttons
- Language selection sidebar
- Response metadata (timing, source count)

## Configuration

### Model Settings (`modules/config.py`)
```python
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
LLM_MODEL = "gemini-2.0-flash"
LLM_TEMPERATURE = 0.1
VECTOR_DB_PATH = "./chroma_db_langchain_e5"
DEFAULT_TOP_K = 5
```

### Language Support
```python
SUPPORTED_LANGUAGES = ["vi", "en"]
DEFAULT_LANGUAGE = "vi"
AUTO_DETECT_DEFAULT = True
```

## Development

### Running Development Notebooks
1. **Data Processing**: `backend/Notebook files(for data scraping, processing and embedding)/RAG_Development.ipynb`
2. **Model Integration**: `backend/Notebook files(for data scraping, processing and embedding)/RAG_LLM_Integration.ipynb`
3. **Embedding Testing**: `backend/Notebook files(for data scraping, processing and embedding)/RAG_Test_Embedding.ipynb`
4. **Web Scraping**: `backend/Notebook files(for data scraping, processing and embedding)/Scraper.ipynb`

### Testing API Endpoints
```bash


# Chat test
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "auto_detect": true}'
```

### Direct Loading Alternative
For development and testing:
```bash
python direct\ loading/run_app.py
```
Access at: `http://localhost:8501`

## Performance

### Resource Usage
- **API Backend**: ~2GB RAM (models loaded once)
- **Frontend**: ~50MB RAM per session
- **Vector Database**: ~500MB disk space

### Scalability
- Single backend serves multiple frontends
- Stateless frontend design
- Persistent vector database
- Concurrent request handling

## Deployment

### Production Checklist
- [ ] Set production API keys in `.env`
- [ ] Configure CORS for specific origins
- [ ] Set up reverse proxy (nginx)
- [ ] Enable API rate limiting
- [ ] Configure logging and monitoring
- [ ] Set up database backups

### Environment Variables
```bash
GOOGLE_API_KEY=your_production_api_key
API_BASE_URL=https://your-api-domain.com
```



### Development Setup
1. Clone repository
2. Install dependencies: `pip install -r requirements_api.txt`
3. Set up `.env` file
4. Run data processing notebooks
5. Start development servers

### Code Structure
- **Backend**: FastAPI with async endpoints
- **Frontend**: Streamlit with custom components
- **Models**: LangChain integration with custom prompts
- **Utils**: Language detection and suggestion generation

