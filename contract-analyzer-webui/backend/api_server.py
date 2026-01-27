import base64
import json
import os
import tempfile
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Load .env if present
load_dotenv()

from src.main import LegalContractAuditor
from src.pdf_report_generator import LegalContractPDFReport
from src.config import CHROMA_DB_PATH

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


@app.post("/qa")
async def question_answer(
    question: str,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
):
    """Ask questions about the most recently analyzed contract."""
    require_key(x_api_key)
    
    # Load existing vector store
    if not os.path.exists(CHROMA_DB_PATH):
        raise HTTPException(
            status_code=400, 
            detail="No contract has been analyzed yet. Please analyze a contract first."
        )
    
    from src.main import LegalContractAuditor
    
    auditor = LegalContractAuditor()
    auditor.vector_store_manager.load_vector_store()
    
    from src.rag_pipeline import RAGPipeline
    rag_pipeline = RAGPipeline(auditor.vector_store_manager)
    
    result = rag_pipeline.answer_query(question, use_reranking=False)
    
    # Save Q&A to file
    output_dir = "analysis_results"
    os.makedirs(output_dir, exist_ok=True)
    qa_log_path = os.path.join(output_dir, "qa_history.json")
    
    qa_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": result["answer"],
        "confidence": result["confidence"],
        "sources": result["sources"]
    }
    
    # Append to Q&A history
    qa_history = []
    if os.path.exists(qa_log_path):
        with open(qa_log_path, "r", encoding="utf-8") as f:
            qa_history = json.load(f)
    
    qa_history.append(qa_entry)
    
    with open(qa_log_path, "w", encoding="utf-8") as f:
        json.dump(qa_history, f, indent=2, ensure_ascii=False)
    
    print(f"\n💬 Q&A saved to: {qa_log_path}")
    
    return JSONResponse(result)


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

        # Save results to JSON file
        output_dir = "analysis_results"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = file.filename.replace(".pdf", "").replace(" ", "_")[:50]
        json_filename = f"{safe_filename}_{timestamp}.json"
        json_path = os.path.join(output_dir, json_filename)
        
        output_data = {
            "filename": file.filename,
            "analysis_date": datetime.now().isoformat(),
            "results": results
        }
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to: {json_path}")

        return JSONResponse({"filename": file.filename, "results": results, "json_saved_to": json_path})


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

        # Save results to JSON file
        output_dir = "analysis_results"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = file.filename.replace(".pdf", "").replace(" ", "_")[:50]
        json_filename = f"{safe_filename}_{timestamp}.json"
        json_path = os.path.join(output_dir, json_filename)
        
        output_data = {
            "filename": file.filename,
            "analysis_date": datetime.now().isoformat(),
            "results": results
        }
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to: {json_path}")

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
                "json_saved_to": json_path
            }
        )
