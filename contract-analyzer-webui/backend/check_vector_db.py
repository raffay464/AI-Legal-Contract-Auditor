"""
Check what's actually in the vector database
"""
from src.vector_store import VectorStoreManager

print("="*80)
print("VECTOR DATABASE INSPECTION")
print("="*80)

# Initialize vector store
print("\n[1] Loading vector database...")
from src.config import CHROMA_DB_PATH
vector_store = VectorStoreManager(persist_directory=CHROMA_DB_PATH)

# Check collection stats
print("\n[2] Checking collection contents...")
try:
    # Get collection
    collection = vector_store.vector_store._collection
    
    # Count documents
    count = collection.count()
    print(f"\nTotal documents in database: {count}")
    
    # Get sample documents
    print("\n[3] Sampling documents from database...")
    results = collection.get(limit=10, include=['metadatas', 'documents'])
    
    print(f"\nShowing first 10 documents:")
    print("-"*80)
    
    for idx, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas']), 1):
        source = metadata.get('source', 'Unknown')
        page = metadata.get('page_number', 'Unknown')
        section = metadata.get('section_header', 'Unknown')
        
        print(f"\n[{idx}] Document:")
        print(f"    Source: {source}")
        print(f"    Page: {page}")
        print(f"    Section: {section}")
        print(f"    Content: {doc[:150]}...")
    
    # Check unique sources
    print("\n" + "="*80)
    print("UNIQUE CONTRACTS IN DATABASE")
    print("="*80)
    
    all_results = collection.get(include=['metadatas'])
    sources = set()
    for metadata in all_results['metadatas']:
        source = metadata.get('source', 'Unknown')
        if source != 'Unknown':
            # Extract just filename
            import os
            filename = os.path.basename(source)
            sources.add(filename)
    
    print(f"\nNumber of unique contracts: {len(sources)}")
    print("\nContracts in database:")
    for idx, source in enumerate(sorted(sources), 1):
        print(f"  [{idx}] {source}")
    
    if len(sources) > 1:
        print("\n⚠️  WARNING: Multiple contracts in database!")
        print("   This can cause retrieval to return wrong documents.")
        print("   Solution: Rebuild with --rebuild flag for each new contract")
    elif len(sources) == 1:
        print("\n✓ Only one contract in database (correct)")
    else:
        print("\n✗ No contracts found in database!")
        
except Exception as e:
    print(f"\n❌ Error inspecting database: {e}")
    print("\nTrying alternative method...")
    
    # Try similarity search
    test_query = "termination"
    docs = vector_store.similarity_search(test_query, k=5)
    
    print(f"\nTest search for '{test_query}' returned {len(docs)} documents:")
    for idx, doc in enumerate(docs, 1):
        print(f"\n[{idx}] Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"    Page: {doc.metadata.get('page_number', 'Unknown')}")
        print(f"    Content: {doc.page_content[:150]}...")

print("\n" + "="*80)
