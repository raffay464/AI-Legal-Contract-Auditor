import base64
import os
import tempfile
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Load .env if present
load_dotenv()

from src.main import LegalContractAuditor
from src.pdf_report_generator import LegalContractPDFReport

app = FastAPI(title="Contract Analyzer API", version="1.0.0")

# CORS for local dev (Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("CONTRACT_API_KEY", "").strip()


def require_key(x_api_key: Optional[str]):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Server misconfigured: CONTRACT_API_KEY not set.")
    if not x_api_key or x_api_key.strip() != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key.")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    rebuild: bool = True,
    redline: bool = False,
):
    require_key(x_api_key)

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = os.path.join(tmp, file.filename)
        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        auditor = LegalContractAuditor()
        auditor.process_contracts([pdf_path], rebuild_index=rebuild)
        results = auditor.analyze_contract(include_redline=redline)

        return JSONResponse({"filename": file.filename, "results": results})


@app.post("/report")
async def report(
    file: UploadFile = File(...),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    rebuild: bool = True,
    redline: bool = False,
):
    require_key(x_api_key)

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = os.path.join(tmp, file.filename)
        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        auditor = LegalContractAuditor()
        auditor.process_contracts([pdf_path], rebuild_index=rebuild)
        results = auditor.analyze_contract(include_redline=redline)

        out_path = os.path.join(tmp, f"{os.path.splitext(file.filename)[0]}_analysis_report.pdf")
        rpt = LegalContractPDFReport(out_path)
        rpt.add_title_page(file.filename)
        rpt.add_executive_summary(results)
        for r in results:
            rpt.add_clause_analysis(r, include_redline=redline)
        rpt.generate()

        with open(out_path, "rb") as f:
            pdf_bytes = f.read()

        return JSONResponse(
            {
                "filename": file.filename,
                "results": results,
                "report_pdf_base64": base64.b64encode(pdf_bytes).decode("utf-8"),
            }
        )
