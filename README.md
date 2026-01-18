# AI Legal Contract Auditor

An AI-powered system that analyzes complex legal contracts and identifies key contractual clauses using Retrieval-Augmented Generation (RAG). The system extracts specific clauses, summarizes them in plain English, assesses legal risk, and provides precise citations.

## Problem Statement

Legal contracts are lengthy, complex, and difficult to review manually. This project builds a prototype AI Legal Contract Auditor capable of understanding legal context and extracting critical clauses while minimizing hallucinations.

## Scope of Clause Analysis

The system focuses on identifying and analyzing the following clauses from legal agreements:

- IP Ownership Assignment  
- Price Restrictions  
- Non-compete, Exclusivity, and No-solicit of Customers  
- Termination for Convenience  
- Governing Law  

## Dataset

This project uses a subset of the **CUAD (Contract Understanding Atticus Dataset)**:  
https://www.atticusprojectai.org/cuad

Selected agreements are used to ensure coverage of the targeted clause types.

## System Overview

The pipeline consists of the following stages:

1. **Document Ingestion**
   - PDF/Text parsing
   - Removal of headers, footers, and noisy artifacts
   - Preservation of section headers for citation

2. **Chunking & Embeddings**
   - Parent-child chunking strategy for long legal documents
   - Vectorization using embedding models
   - Storage in a vector database

3. **Retrieval-Augmented Generation (RAG)**
   - Clause-specific retrieval
   - Context-aware question answering
   - Long-context handling via hierarchical retrieval and reranking

4. **Clause Analysis**
   - Plain English summarization
   - Risk scoring (Low / Medium / High)
   - Exact citation (page number or section header)

## Tech Stack

- **Language**: Python  
- **LLM**:   
- **Embeddings**:  
- **Vector Database**:   
- **Framework**:   

## Risk Scoring Methodology

Risk is evaluated based on how vendor-friendly or customer-friendly the clause language is:

- **Low Risk**: Balanced or industry-standard language  
- **Medium Risk**: Mildly one-sided obligations  
- **High Risk**: Strongly unfavorable or restrictive terms  

## Hallucination Mitigation Strategy

- Strict Retrieval-Augmented Generation (RAG)
- Answers grounded only in retrieved context
- Citation enforcement for every output
- Fallback to “Not Found in Contract” when data is missing

## License

This project is a prototype for research and educational purposes.

---

**Note**: This tool is designed to assist with contract review but should not replace professional legal counsel. Always consult with qualified legal professionals for important contractual decisions.
