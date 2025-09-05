# Simple Summarizer

A web app for uploading text, PDF, or DOCX files and generating concise summaries using LLM (Mistral via Ollama).

## Features
- Upload `.txt`, `.md`, `.pdf`, or `.docx` files
- Automatic chunking and database storage
- Hierarchical summarization with Mistral (Ollama)
- Simple chat interface (React)

---

## Installation

### 1. Clone the repository
```
git clone <your-repo-url>
cd simpe-summarizer
```

### 2. Backend setup (Python)

#### Requirements
- Python 3.9+
- PostgreSQL
- Ollama (with Mistral model)

#### Install Python dependencies
```
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
# If requirements.txt is missing, install manually:
pip install flask flask-cors psycopg2 PyPDF2 python-docx langchain
```

#### Configure PostgreSQL
- Create a database and table `items` with at least a `content` column (optionally `embedding`)
- Set DB credentials in `backend/config.py`

#### Start Ollama and pull Mistral model
```
ollama serve
ollama pull mistral
```

#### Run backend server
```
python main.py
```

---

### 3. Frontend setup (React)

```
cd ../app
npm install
npm run build
```

---

## Usage
1. Start the backend server (`python main.py` in `backend`)
2. Open your browser at [http://localhost:5000](http://localhost:5000)
3. Upload a file or ask a question in the chat
4. The summary will appear in the chat after processing

---

## Notes
- Only one file is stored/processed at a time (uploading a new file clears previous data)
- Supported file types: `.txt`, `.md`, `.pdf`, `.docx`
- For large files, summarization may take some time

---

## Troubleshooting
- Ensure PostgreSQL and Ollama are running
- Check `backend/config.py` for correct paths and credentials
- Install all required Python packages

---

## License
MIT

