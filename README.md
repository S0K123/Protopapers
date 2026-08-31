# ProtoPapers

ProtoPapers is an early-stage working prototype that converts academic research papers into structured automation workflows. Given a PDF, the system extracts content, analyzes it with AI, and generates executable workflow schemas that can be imported into platforms like n8n.

## Overview

The core problem: academic papers contain detailed methodologies, algorithms, and workflows that are useful but remain locked in static text. ProtoPapers explores how to automatically translate these into structured, executable automation workflows.

This is an active research and development project—the core pipeline works, but the system is still being refined and tested.

## What it currently does

- **PDF Processing**: Reads research papers in PDF format, with automatic fallback to OCR for scanned documents
- **Text Chunking & Vectorization**: Splits paper content into chunks and stores embeddings in ChromaDB for efficient retrieval
- **Workflow Blueprint Generation**: Uses Google Gemini API to analyze paper methodology and extract workflow nodes (Trigger, Data Transformation, AI Processing, Action/Output)
- **n8n Schema Export**: Automatically generates n8n-compatible JSON schemas that can be directly imported as executable workflows
- **Executable Code Generation**: Creates Python code implementations based on the paper's algorithms and data processing logic
- **RAG-based Q&A**: Answer questions about the paper using retrieved context from the vector database

## How it works

```
Research Paper (PDF)
    ↓
PDF Text Extraction (with OCR fallback)
    ↓
Text Chunking & Embedding
    ↓
Vector Storage (ChromaDB)
    ↓
AI Analysis (Google Gemini)
    ↓
Workflow Blueprint Generation
    ↓
n8n Schema & Executable Code Output
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | Python 3 |
| **Web UI** | Streamlit |
| **Vector Database** | ChromaDB (local embeddings) |
| **LLM** | Google Gemini API |
| **PDF Processing** | PyPDF, PyMuPDF (fitz) |
| **OCR** | Tesseract (pytesseract) |
| **Image Processing** | Pillow |
| **Config Management** | python-dotenv |

## Project Structure

```
├── app.py                    # Streamlit web application
├── main.py                   # CLI entry point for batch processing
├── agent.py                  # RAG agent for blueprint & code generation
├── pdf_loader.py             # PDF text extraction with OCR fallback
├── vector_db.py              # ChromaDB vector store manager
├── requirements.txt          # Python dependencies
└── packages.txt              # System dependencies (Tesseract)
```

**Key files:**
- **app.py**: Interactive Streamlit interface—upload papers, view generated workflows, ask questions
- **agent.py**: Core RAG agent using Gemini API to generate workflow blueprints and executable Python code
- **pdf_loader.py**: Handles both native and scanned PDFs
- **vector_db.py**: Manages embedding storage and semantic search

## Running Locally

### Prerequisites
- Python 3.8+
- Google Gemini API key (free tier available)
- Tesseract OCR (for scanned PDF support)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/protopapers.git
cd protopapers
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install system dependencies (for OCR support):
   - **Windows**: Download and install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

5. Set up environment variables:
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

6. Run the Streamlit app:
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

## Live Prototype

Try the live version here: **[https://protopapers.streamlit.app/](https://protopapers.streamlit.app/)**

## Current Status

ProtoPapers is an early-stage working prototype. The core workflow is functional, but the system is still being tested and improved.

**Known limitations:**
- ChromaDB uses in-memory storage (workflows are not persisted between sessions)
- Depends on Gemini API for all AI operations (requires API key and internet connection)
- Workflow quality depends on paper clarity and structure—dense or poorly scanned PDFs may produce incomplete blueprints
- Generated n8n schemas are basic templates and may require manual refinement for production use

## Roadmap

### Completed
- PDF processing with OCR fallback
- Vector embedding and retrieval (ChromaDB)
- Workflow blueprint generation via LLM
- n8n JSON schema export
- Executable Python code generation
- RAG-based paper Q&A
- Streamlit web interface

### In Progress
- Improved paper parsing and context extraction
- Better workflow node validation

### Planned
- Persistent workflow storage
- Workflow refinement UI with human feedback
- Support for additional automation platforms beyond n8n
- Improved accuracy for complex/multi-section papers
- Local LLM option (reduce API dependency)
- Workflow testing and evaluation metrics

## Research Direction

ProtoPapers explores how structured automation workflows can be derived from the methodologies described in academic papers. The current prototype demonstrates feasibility with basic LLM-powered analysis. Future development will focus on improving extraction accuracy, enabling human-in-the-loop refinement, and building evaluation methods to assess workflow quality.

## Development

To contribute or extend the project, install dev dependencies and run tests:

```bash
# Additional setup for development
python main.py sample.pdf  # Test CLI pipeline
```

## License

This project is provided as-is for educational and research purposes.

---

**Status**: Early-stage prototype under active development  
**Last Updated**: 2026  
**Questions?** Check the [Issues](https://github.com/yourusername/protopapers/issues) section
