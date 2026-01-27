import re
from typing import List, Dict, Tuple
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class LegalPDFParser:
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Parent chunks (large, for context)
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size * 2,  # 3000 chars for parents
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Child chunks (small, for retrieval)
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size // 2,  # 750 chars for children
            chunk_overlap=chunk_overlap // 2,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, Dict]:
        reader = PdfReader(pdf_path)
        full_text = ""
        metadata = {
            "source": pdf_path,
            "total_pages": len(reader.pages),
            "page_texts": {}
        }
        
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            page_text = self._clean_text(page_text)
            metadata["page_texts"][page_num] = page_text
            full_text += f"\n--- Page {page_num} ---\n{page_text}"
        
        return full_text, metadata
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        text = text.strip()
        return text
    
    def _extract_section_headers(self, text: str) -> List[str]:
        patterns = [
            r'^[A-Z\s]{3,}$',
            r'^\d+\.\s+[A-Z][a-zA-Z\s]+',
            r'^Article\s+\d+',
            r'^Section\s+\d+',
        ]
        
        headers = []
        for line in text.split('\n'):
            line = line.strip()
            for pattern in patterns:
                if re.match(pattern, line):
                    headers.append(line)
                    break
        return headers
    
    def semantic_chunk_with_context(self, text: str, metadata: Dict) -> List[Document]:
        # Create parent chunks (large)
        parent_chunks = self.parent_splitter.split_text(text)
        
        documents = []
        parent_id = 0
        
        for parent_chunk in parent_chunks:
            # Create child chunks from each parent
            child_chunks = self.child_splitter.split_text(parent_chunk)
            
            for child_idx, child_chunk in enumerate(child_chunks):
                page_num = self._find_page_number(child_chunk, metadata)
                section_header = self._find_nearest_section(child_chunk, text)
                
                doc_metadata = {
                    "source": metadata["source"],
                    "chunk_id": f"{parent_id}_{child_idx}",
                    "parent_id": parent_id,
                    "page_number": page_num,
                    "section_header": section_header,
                    "parent_content": parent_chunk,  # Store full parent for context
                    "is_parent_retrieval": True
                }
                
                # Store child chunk for retrieval, but include parent in metadata
                documents.append(Document(page_content=child_chunk, metadata=doc_metadata))
            
            parent_id += 1
        
        return documents
    
    def _find_page_number(self, chunk: str, metadata: Dict) -> int:
        page_match = re.search(r'--- Page (\d+) ---', chunk)
        if page_match:
            return int(page_match.group(1))
        
        for page_num, page_text in metadata["page_texts"].items():
            if chunk[:100] in page_text:
                return page_num
        
        return 1
    
    def _find_nearest_section(self, chunk: str, full_text: str) -> str:
        chunk_start = full_text.find(chunk[:50])
        if chunk_start == -1:
            return "Unknown Section"
        
        text_before = full_text[:chunk_start]
        lines = text_before.split('\n')
        
        for line in reversed(lines):
            line = line.strip()
            if re.match(r'^[A-Z\s]{3,}$|^\d+\.\s+[A-Z]|^Article\s+\d+|^Section\s+\d+', line):
                return line
        
        return "Unknown Section"
    
    def process_pdf(self, pdf_path: str) -> List[Document]:
        full_text, metadata = self.extract_text_from_pdf(pdf_path)
        documents = self.semantic_chunk_with_context(full_text, metadata)
        return documents
