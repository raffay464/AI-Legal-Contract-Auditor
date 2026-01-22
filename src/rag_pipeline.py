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
        self.llm = Ollama(model=llm_model, base_url=OLLAMA_BASE_URL, temperature=0)
    
    def retrieve_relevant_context(self, query: str, k: int = 5, use_mmr: bool = True) -> List[Document]:
        if use_mmr:
            documents = self.vector_store_manager.mmr_search(query, k=k, fetch_k=k*4)
        else:
            documents = self.vector_store_manager.similarity_search(query, k=k)
        
        return documents
    
    def retrieve_with_reranking(self, query: str, initial_k: int = 10, final_k: int = 5) -> List[Document]:
        initial_docs = self.vector_store_manager.similarity_search_with_score(query, k=initial_k)
        
        rerank_prompt = """You are a legal document relevance scorer. 

Query: {query}

Document: {document}

On a scale of 0-10, how relevant is this document to the query? 
Consider:
- Direct mention of the topic
- Contextual relevance
- Legal specificity

Respond with ONLY a number between 0 and 10."""
        
        scored_docs = []
        for doc, similarity_score in initial_docs:
            try:
                prompt_text = rerank_prompt.format(query=query, document=doc.page_content)
                response = self.llm.invoke(prompt_text)
                relevance_score = float(response.strip())
                combined_score = (similarity_score + relevance_score) / 2
                scored_docs.append((doc, combined_score))
            except:
                scored_docs.append((doc, similarity_score))
        
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs[:final_k]]
    
    def answer_query(self, query: str, use_reranking: bool = False) -> Dict:
        if use_reranking:
            relevant_docs = self.retrieve_with_reranking(query, initial_k=10, final_k=5)
        else:
            relevant_docs = self.retrieve_relevant_context(query, k=5)
        
        if not relevant_docs:
            return {
                "answer": "I don't know. I could not find relevant information in the contract to answer this query.",
                "sources": [],
                "confidence": "none"
            }
        
        context = self._format_context(relevant_docs)
        
        qa_prompt = """You are a legal contract analysis AI assistant. Answer the question based ONLY on the provided context from the contract.

Context from contract:
{context}

Question: {question}

Instructions:
1. If the context contains the answer, provide a clear and precise response
2. If the context does NOT contain enough information to answer, respond with: "I don't know. The provided contract sections do not contain sufficient information to answer this question."
3. Cite specific sections or page numbers when possible
4. Be concise but thorough

Answer:"""
        
        prompt_text = qa_prompt.format(context=context, question=query)
        response = self.llm.invoke(prompt_text)
        
        answer = response.strip()
        
        confidence = "high" if "I don't know" not in answer else "none"
        if any(word in answer.lower() for word in ["may", "possibly", "unclear", "ambiguous"]):
            confidence = "medium"
        
        sources = [
            {
                "page": doc.metadata.get("page_number", "Unknown"),
                "section": doc.metadata.get("section_header", "Unknown"),
                "content_preview": doc.page_content[:200] + "..."
            }
            for doc in relevant_docs
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence
        }
    
    def _format_context(self, documents: List[Document]) -> str:
        context_parts = []
        for idx, doc in enumerate(documents, 1):
            page = doc.metadata.get("page_number", "Unknown")
            section = doc.metadata.get("section_header", "Unknown")
            context_parts.append(
                f"[Source {idx} - Page {page}, Section: {section}]\n{doc.page_content}\n"
            )
        return "\n".join(context_parts)
