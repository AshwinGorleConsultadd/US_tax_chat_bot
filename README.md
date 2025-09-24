# US Tax Chatbot

An AI-powered chatbot for US tax regulations that can accurately retrieve relevant sections from authoritative tax documents and provide precise, context-aware answers to user queries using semantic search over embeddings stored in a persistent vector database.

## Features

- **PDF Text Extraction**: Robust extraction from PDF documents using multiple libraries (PyPDF2, pdfplumber, PyMuPDF)
- **Semantic Text Chunking**: Intelligent text splitting with RecursiveCharacterTextSplitter
- **OpenAI Embeddings**: Uses text-embedding-3-small for optimal performance and cost
- **Vector Database**: Chroma DB for persistent storage and retrieval
- **Context-Aware Chat**: Maintains conversation history and context
- **Terminal Interface**: User-friendly command-line chat interface

## Project Structure

```
finance_chat_bot/
├── src/                          # Source code modules
│   ├── pdf_extractor.py         # PDF text extraction
│   ├── text_splitter.py         # Text chunking functionality
│   ├── embeddings_generator.py  # OpenAI embeddings generation
│   ├── vector_database.py      # Chroma DB operations
│   ├── retrieval_system.py     # Semantic search and retrieval
│   └── chat_functions.py       # Chat interface functions
├── input/                       # Directory for PDF files
├── chroma_db/                   # Vector database storage
├── upload_documents.py         # Script to upload PDFs to vector DB
├── chat.py                     # Terminal chat interface
├── requirements.txt            # Python dependencies
└── env_example.txt             # Environment variables template
```

## Installation

1. **Clone or download the project**
   ```bash
   cd finance_chat_bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `env_example.txt` to `.env`
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

## Usage

### 1. Upload Documents to Vector Database

1. **Place PDF files in the `input/` directory**
   - Add your tax-related PDF files (IRS publications, tax guides, etc.)

2. **Modify the PDF_FILES array in `upload_documents.py`**
   ```python
   PDF_FILES = [
       "your_tax_document_1.pdf",
       "your_tax_document_2.pdf",
       # Add more PDF files as needed
   ]
   ```

3. **Run the upload script**
   ```bash
   python upload_documents.py
   ```

   This will:
   - Extract text from all PDF files
   - Split text into semantic chunks
   - Generate embeddings using OpenAI
   - Store everything in Chroma DB

### 2. Start Chatting

Run the terminal chat interface:
```bash
python chat.py
```

### Available Commands

- `/help` - Show available commands
- `/reset` - Reset chat history
- `/stats` - Show chat statistics
- `/history` - Show chat history
- `/clear` - Clear screen
- `/quit` or `/exit` - Exit the chat

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (defaults provided)
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHUNK_SIZE=300
CHUNK_OVERLAP=50
MAX_RETRIEVAL_RESULTS=5
```

### Text Processing Settings

- **Chunk Size**: 300 tokens (adjustable in `text_splitter.py`)
- **Chunk Overlap**: 50 tokens (preserves context across boundaries)
- **Retrieval Results**: 5 documents per query (adjustable)

## How It Works

1. **PDF Processing**: Multiple PDF libraries ensure robust text extraction
2. **Text Chunking**: Hierarchical splitting by paragraphs, then by tokens
3. **Embeddings**: OpenAI's text-embedding-3-small converts chunks to vectors
4. **Storage**: Chroma DB stores embeddings with metadata for fast retrieval
5. **Retrieval**: Semantic similarity search finds relevant documents
6. **Generation**: GPT-3.5-turbo generates answers with retrieved context
7. **Context**: Chat history is maintained for conversational continuity

## API Functions

The core functionality is exposed through these functions in `chat_functions.py`:

```python
from src.chat_functions import send_message, reset_chat, get_chat_history, get_chat_stats

# Send a message and get response
response = send_message("What are itemized deductions?")

# Reset chat history
reset_chat()

# Get conversation history
history = get_chat_history()

# Get chat statistics
stats = get_chat_stats()
```

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not set"**
   - Make sure you have a `.env` file with your OpenAI API key

2. **"No documents in database"**
   - Run `upload_documents.py` first to process your PDF files

3. **"Import errors"**
   - Install all dependencies: `pip install -r requirements.txt`

4. **"PDF extraction failed"**
   - Ensure PDF files are not corrupted or password-protected
   - Try different PDF files to test

### Logging

The application provides detailed logging at each step. Check the terminal output for:
- PDF extraction progress
- Text chunking statistics
- Embedding generation status
- Database operations
- Chat interactions

## Development

### Adding New Features

1. **New PDF libraries**: Add to `pdf_extractor.py`
2. **Different chunking strategies**: Modify `text_splitter.py`
3. **Alternative embeddings**: Update `embeddings_generator.py`
4. **Custom retrieval**: Extend `retrieval_system.py`

### Testing

Each module includes a `main()` function for testing:
```bash
python src/pdf_extractor.py
python src/text_splitter.py
python src/embeddings_generator.py
python src/vector_database.py
python src/retrieval_system.py
python src/chat_functions.py
```

## License

This project is for educational and development purposes. Please ensure you comply with OpenAI's usage policies and any applicable terms for the tax documents you use.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the chatbot's functionality and accuracy.
