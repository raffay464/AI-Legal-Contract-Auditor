# Contract Analyzer Web UI (Fancy)

This project turns your existing Python contract analyzer into a **local web API** + a **fancy web UI**.

## What’s included
- **Backend (FastAPI)**
  - `POST /analyze` → returns JSON clause analysis
  - `POST /report` → returns JSON + `report_pdf_base64`
  - API key header: `X-API-Key`
- **Frontend (React + Vite + Tailwind)**
  - Upload PDF
  - Search / filter results
  - “Analyze + Report” downloads the PDF

---

## Prereqs
- Python 3.10+
- Node 18+
- Ollama running locally (default base url is in `backend/src/config.py`)

If you use the default model, pull it:
```bash
ollama pull llama3.2
```

---

## Run backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set CONTRACT_API_KEY

uvicorn api_server:app --host 0.0.0.0 --port 8000
```
Check:
- `GET http://localhost:8000/health`

## Run frontend
```bash
cd frontend
npm install
npm run dev
```
Open:
- `http://localhost:5173`

Set:
- API Base URL = `http://localhost:8000`
- API Key = same value as `backend/.env`
