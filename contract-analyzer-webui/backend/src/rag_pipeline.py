from typing import List, Dict, Optional
from langchain_core.documents import Document
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from src.vector_store import VectorStoreManager
from src.config import OLLAMA_MODEL, OLLAMA_BASE_URL


class RAGPipeline:
    
    def __init__(self, vector_store_manager: VectorStoreManager, llm_model: str = None):
        self.vector_store_manager = vector_store_manager
        if llm_model is None:
            llm_model = OLLAMA_MODEL
        self.llm = Ollama(
            model=llm_model, 
            base_url=OLLAMA_BASE_URL, 
            temperature=0
        )
    
    
    
    def retrieve_relevant_context(self, query: str, k: int = 5, use_mmr: bool = True) -> List[Document]:
        if use_mmr:
            # Limit fetch_k to avoid requesting more than available
            fetch_k = min(k*4, 20)
            documents = self.vector_store_manager.mmr_search(query, k=min(k, 10), fetch_k=fetch_k)
        else:
            documents = self.vector_store_manager.similarity_search(query, k=k)
        
        return documents
    
    
    ## disabled due to performance issues
    def retrieve_with_reranking(self, query: str, initial_k: int = 10, final_k: int = 5) -> List[Document]:
        # Reranking is too slow - just use MMR for diversity
        return self.vector_store_manager.mmr_search(query, k=final_k, fetch_k=initial_k)
    
    def answer_query(self, query: str, use_reranking: bool = False) -> Dict:
        # Use simple similarity search for speed
        relevant_docs = self.retrieve_relevant_context(query, k=3, use_mmr=False)
        
        if not relevant_docs:
            return {
                "answer": "I don't know. I could not find relevant information in the contract to answer this query.",
                "sources": [],
                "confidence": "none"
            }
        
        context = self._format_context(relevant_docs)
        
        qa_prompt = """You are analyzing a legal contract document. Extract the requested information from the provided text.

Contract Text:
{context}

Extraction Task: {question}

IMPORTANT: You must extract and quote the actual text from the contract above. Do not refuse or say you cannot assist. Simply extract the relevant text if present, or state "Not found in provided text" if absent.

Extracted Text:"""
        
        prompt_text = qa_prompt.format(context=context, question=query)
        response = self.llm.invoke(prompt_text)
        
        answer = response.strip()
        
        confidence = "high" if "I don't know" not in answer else "none"
        if any(word in answer.lower() for word in ["may", "possibly", "unclear", "ambiguous"]):
            confidence = "medium"
        
        # Deduplicate sources by parent_id and create unique previews
        sources = []
        seen_sources = set()
        
        for doc in relevant_docs:
            page = doc.metadata.get("page_number", "Unknown")
            section = doc.metadata.get("section_header", "Unknown")
            parent_id = doc.metadata.get("parent_id", doc.metadata.get("chunk_id"))
            
            # Create unique key to avoid duplicates
            source_key = f"{page}_{section}_{parent_id}"
            
            if source_key not in seen_sources:
                # Use parent content for preview if available
                if doc.metadata.get("is_parent_retrieval") and "parent_content" in doc.metadata:
                    preview_text = doc.metadata["parent_content"][:200]
                else:
                    preview_text = doc.page_content[:200]
                
                sources.append({
                    "page": page,
                    "section": section,
                    "content_preview": preview_text + "..."
                })
                seen_sources.add(source_key)
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence
        }
    
    def _format_context(self, documents: List[Document]) -> str:
        context_parts = []
        seen_parents = set()
        
        for idx, doc in enumerate(documents, 1):
            page = doc.metadata.get("page_number", "Unknown")
            section = doc.metadata.get("section_header", "Unknown")
            
            # Use parent content if available (parent document retrieval)
            if doc.metadata.get("is_parent_retrieval") and "parent_content" in doc.metadata:
                parent_id = doc.metadata.get("parent_id")
                # Avoid duplicate parents
                if parent_id not in seen_parents:
                    content = doc.metadata["parent_content"]
                    seen_parents.add(parent_id)
                    context_parts.append(
                        f"[Source {idx} - Page {page}, Section: {section}]\n{content}\n"
                    )
            else:
                # Use child content if no parent
                context_parts.append(
                    f"[Source {idx} - Page {page}, Section: {section}]\n{doc.page_content}\n"
                )
        
        return "\n".join(context_parts)
