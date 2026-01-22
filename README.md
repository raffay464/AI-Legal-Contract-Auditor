# AI Legal Contract Auditor

An AI-powered system that analyzes complex legal contracts and identifies key contractual clauses using **Retrieval-Augmented Generation (RAG)**. The system extracts specific clauses, summarizes them in plain English, assesses legal risk, and provides precise citations.

---

## Problem Statement

Legal contracts are lengthy, complex, and difficult to review manually. This project builds a prototype **AI Legal Contract Auditor** capable of understanding legal context and extracting critical clauses while minimizing hallucinations. The system is designed to support legal professionals by automating clause extraction, summarization, and risk assessment.

---

## Scope of Clause Analysis

The system focuses on identifying and analyzing the following clauses from legal agreements:

- **IP Ownership Assignment**  
- **Price Restrictions**  
- **Non-compete, Exclusivity, and No-solicit of Customers**  
- **Termination for Convenience**  
- **Governing Law**  

---

## Dataset

This project uses a subset of the **CUAD (Contract Understanding Atticus Dataset)**:  
[https://www.atticusprojectai.org/cuad](https://www.atticusprojectai.org/cuad)  

- Selected agreements cover the targeted clause types.  
- Contracts are primarily in **PDF format**, requiring robust preprocessing due to inconsistent formatting, multi-page clauses, and dense legal language.

---

## System Overview

### 1. Document Ingestion
- PDF/Text parsing using **PyPDF2** and **pdfplumber**  
- Removal of headers, footers, and noisy artifacts  
- Preservation of section headers for accurate citation  

### 2. Chunking & Embeddings
- **Semantic Chunking with Context Preservation**  
  - RecursiveCharacterTextSplitter with:
    - Chunk size = 1000 characters  
    - Overlap = 200 characters (ensures clauses spanning multiple chunks are fully captured)  
    - Hierarchical separators: paragraphs → lines → sentences → words → characters  
  - Preserves clause integrity and legal meaning  
- Metadata: document source, page number, section header, chunk index  
- Vectorization using **MiniLM-L6-v2 embeddings**  
- Storage in **ChromaDB** for local, persistent, and fast retrieval  


### 3. Retrieval-Augmented Generation (RAG)
- Clause-specific retrieval for targeted queries  
- Context-aware question answering  
- Long-context handling via hierarchical retrieval, **reranking**, and optional LLM-based scoring  

### 4. Clause Analysis
- Summarization in plain English  
- Risk scoring (Low / Medium / High) based on vendor- or customer-friendliness  
- Citation of exact location (page number or section header)  
- Optional **redline suggestions** are generated automatically for High-Risk clauses using LLM-based rephrasing  

---

## Tech Stack

- **Language**: Python  
- **LLM**: Llama 3.2 (via Ollama, 3B parameters)  
  - Local deployment, data privacy, zero operational cost, strong legal comprehension  
  - Inference latency: ~5–30 seconds per query  
- **Embeddings**: MiniLM-L6-v2  
- **Vector Database**: ChromaDB  
- **Frameworks & Libraries**: LangChain, Ollama SDK, PyPDF2, pdfplumber  

> ⚡ Note: The codebase was developed using Python with the support of GPT and Gemini for guidance and best practices. All core logic is original and implemented by the team.

---

## Risk Scoring Methodology

Risk is evaluated based on how vendor-friendly or customer-friendly the clause language is:

- **Low Risk**: Balanced or industry-standard language  
- **Medium Risk**: Mildly one-sided obligations  
- **High Risk**: Strongly unfavorable or restrictive terms  

---

## Hallucination Mitigation Strategy

To ensure reliability and safety in a real-world legal environment:

- Responses are grounded **only in retrieved document chunks**  
- Explicit instruction to respond with "**I don’t know**" if the clause or answer is absent  
- **Citation enforcement**: Every output includes page number, section header, and content snippet  
- Multi-layer retrieval quality controls:
  - Vector similarity search  
  - Maximal Marginal Relevance (MMR) for source diversity  
  - Optional LLM-based reranking  
- Human-in-the-loop for high-risk clauses and medium-confidence outputs  
- All analyses logged for traceability and auditability  
- Tested on CUAD contracts with **low hallucination rates**  

---

## License

This project is a prototype for research and educational purposes.

> **Note**: This tool is designed to assist with contract review but **does not replace professional legal counsel**. Always consult qualified legal professionals for important contractual decisions.


## Dependencies

The project uses Python packages listed in `requirements.txt` for installation.  

- **Core dependencies** include LangChain, ChromaDB, PyPDF, OpenAI SDK, and Sentence Transformers.  
- A separate `constraints.txt` is provided to **pin specific versions** and resolve dependency conflicts between LangChain modules, OpenAI SDK, and LangChain community packages.  

**Installation Example:**

```bash
# Install with pip using the constraints file
pip install -r requirements.txt -c constraints.txt

