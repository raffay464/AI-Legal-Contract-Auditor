import os
import sys
from pathlib import Path
from typing import List
from src.pdf_parser import LegalPDFParser
from src.vector_store import VectorStoreManager
from src.rag_pipeline import RAGPipeline
from src.clause_analyzer import ClauseAnalyzer
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, CHROMA_DB_PATH, OLLAMA_MODEL


class LegalContractAuditor:
    
    def __init__(self, persist_directory: str = CHROMA_DB_PATH):
        self.pdf_parser = LegalPDFParser(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        self.vector_store_manager = VectorStoreManager(
            persist_directory=persist_directory,
            embedding_model=EMBEDDING_MODEL
        )
        self.rag_pipeline = None
        self.clause_analyzer = None
    
    def process_contracts(self, pdf_paths: List[str], rebuild_index: bool = False):
        if rebuild_index or not os.path.exists(CHROMA_DB_PATH):
            print("Processing contracts and building vector database...")
            all_documents = []
            
            for pdf_path in pdf_paths:
                print(f"Processing: {pdf_path}")
                documents = self.pdf_parser.process_pdf(pdf_path)
                all_documents.extend(documents)
                print(f"  - Extracted {len(documents)} chunks")
            
            print(f"\nTotal chunks: {len(all_documents)}")
            print("Creating vector store...")
            self.vector_store_manager.create_vector_store(all_documents)
            print("Vector store created successfully!")
        else:
            print("Loading existing vector store...")
            self.vector_store_manager.load_vector_store()
            print("Vector store loaded successfully!")
        
        self.rag_pipeline = RAGPipeline(self.vector_store_manager, llm_model=None)
        self.clause_analyzer = ClauseAnalyzer(self.rag_pipeline, llm_model=None)
    
    def analyze_contract(self, include_redline: bool = False) -> List[dict]:
        if self.clause_analyzer is None:
            raise ValueError("Process contracts first using process_contracts()")
        
        print("\n" + "="*80)
        print("LEGAL CONTRACT ANALYSIS REPORT")
        print("="*80)
        
        results = self.clause_analyzer.analyze_all_clauses()
        
        for result in results:
            print(f"\n{'='*80}")
            print(f"CLAUSE: {result['clause_type']}")
            print(f"{'='*80}")
            
            if result['found']:
                print(f"\n✓ FOUND")
                print(f"\nSUMMARY:")
                print(f"{result['summary']}")
                
                print(f"\nRISK RATING: {result['risk_rating']}")
                print(f"EXPLANATION: {result['risk_explanation']}")
                
                print(f"\nCITATIONS:")
                for idx, citation in enumerate(result['citations'], 1):
                    print(f"  [{idx}] Page {citation['page']}, Section: {citation['section']}")
                    print(f"      Preview: {citation['content_preview']}")
                
                if include_redline and result['risk_rating'] == "HIGH":
                    print(f"\n🔴 HIGH RISK DETECTED - Generating Redline Suggestion...")
                    redline = self.clause_analyzer.generate_redline_suggestion(
                        result['content'], 
                        result['clause_type'], 
                        result['risk_rating']
                    )
                    if redline:
                        print(f"\nREDLINE SUGGESTION:")
                        print(redline)
            else:
                print(f"\n✗ NOT FOUND")
                print(f"Summary: {result['summary']}")
        
        return results
    
    def query_contract(self, question: str) -> dict:
        if self.rag_pipeline is None:
            raise ValueError("Process contracts first using process_contracts()")
        
        print(f"\nQuery: {question}")
        result = self.rag_pipeline.answer_query(question, use_reranking=True)
        
        print(f"\nAnswer: {result['answer']}")
        print(f"Confidence: {result['confidence']}")
        
        if result['sources']:
            print(f"\nSources:")
            for idx, source in enumerate(result['sources'], 1):
                print(f"  [{idx}] Page {source['page']}, Section: {source['section']}")
        
        return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Legal Contract Auditor")
    parser.add_argument("--contracts", nargs="+", required=True, help="Path(s) to contract PDF files")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild vector database")
    parser.add_argument("--redline", action="store_true", help="Include redline suggestions for high-risk clauses")
    parser.add_argument("--query", type=str, help="Ask a specific question about the contract")
    
    args = parser.parse_args()
    
    # This project uses Ollama (local) by default via settings in src/config.py.
    # We intentionally do NOT hard-require an OpenAI API key.
    
    auditor = LegalContractAuditor()
    
    auditor.process_contracts(args.contracts, rebuild_index=args.rebuild)
    
    if args.query:
        auditor.query_contract(args.query)
    else:
        auditor.analyze_contract(include_redline=args.redline)


if __name__ == "__main__":
    main()
