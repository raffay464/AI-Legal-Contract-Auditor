import os
from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300

USE_OLLAMA = True
OLLAMA_MODEL = "llama3.2"
OLLAMA_BASE_URL = "http://localhost:11434"

USE_OLLAMA_EMBEDDINGS = True
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHROMA_DB_PATH = "./chroma_db"

TARGET_CLAUSES = [
    "IP Ownership Assignment",
    "Price Restrictions",
    "Non-compete, Exclusivity, No-solicit of Customers",
    "Termination for Convenience",
    "Governing Law"
]

RISK_CRITERIA = {
    "IP Ownership Assignment": {
        "high_risk_keywords": ["assigns all rights", "exclusive ownership", "perpetual", "irrevocable", "waives all rights"],
        "low_risk_keywords": ["joint ownership", "limited license", "retains rights", "shared ownership"]
    },
    "Price Restrictions": {
        "high_risk_keywords": ["no increase allowed", "fixed price", "price ceiling", "cannot adjust", "locked price"],
        "low_risk_keywords": ["annual adjustment", "CPI indexed", "market rate", "negotiable"]
    },
    "Non-compete, Exclusivity, No-solicit of Customers": {
        "high_risk_keywords": ["indefinite", "worldwide", "all industries", "perpetual", "unlimited scope"],
        "low_risk_keywords": ["limited duration", "specific geography", "narrow scope", "reasonable restrictions"]
    },
    "Termination for Convenience": {
        "high_risk_keywords": ["no termination right", "cannot terminate", "irrevocable", "no exit clause"],
        "low_risk_keywords": ["30 days notice", "60 days notice", "mutual termination", "either party may terminate"]
    },
    "Governing Law": {
        "high_risk_keywords": ["foreign jurisdiction", "arbitration mandatory", "waives jury trial", "exclusive venue"],
        "low_risk_keywords": ["mutual jurisdiction", "local courts", "mediation first", "negotiable venue"]
    }
}
