from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb
from chromadb.config import Settings
from src.config import USE_OLLAMA_EMBEDDINGS, OLLAMA_EMBEDDING_MODEL, OLLAMA_BASE_URL


class VectorStoreManager:
    
    def __init__(self, persist_directory: str, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2", use_ollama: bool = USE_OLLAMA_EMBEDDINGS):
        self.persist_directory = persist_directory
        
        if use_ollama:
            self.embeddings = OllamaEmbeddings(
                model=OLLAMA_EMBEDDING_MODEL,
                base_url=OLLAMA_BASE_URL
            )
        else:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        self.vector_store = None
    
    def create_vector_store(self, documents: List[Document]) -> Chroma:
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="legal_contracts"
        )
        return self.vector_store
    
    def load_vector_store(self) -> Chroma:
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="legal_contracts"
        )
        return self.vector_store
    
    def add_documents(self, documents: List[Document]):
        if self.vector_store is None:
            self.vector_store = self.create_vector_store(documents)
        else:
            self.vector_store.add_documents(documents)
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Load or create a vector store first.")
        return self.vector_store.similarity_search(query, k=k)
    
    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Load or create a vector store first.")
        return self.vector_store.similarity_search_with_score(query, k=k)
    
    ## Disabled due to performance issues
    def mmr_search(self, query: str, k: int = 5, fetch_k: int = 20) -> List[Document]:
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Load or create a vector store first.")
        return self.vector_store.max_marginal_relevance_search(
            query, k=k, fetch_k=fetch_k
        )
