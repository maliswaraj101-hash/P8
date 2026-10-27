import chromadb
import ollama
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import json
import os

class RAGEngine:
    def __init__(self, config_path="config.yaml"):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path="./data/knowledge_base/embeddings")
        
        # Create or get collections - FIXED: Consistent naming
        self.schedule3_knowledge = self.chroma_client.get_or_create_collection(
            name="schedule3_knowledge",
            metadata={"description": "Schedule III regulations and examples"}
        )
        
        self.audit_cases = self.chroma_client.get_or_create_collection(
            name="audit_cases",
            metadata={"description": "Previous audit findings and patterns"}
        )
        
        # Ollama client for local mistral
        self.llama_model = "mistral"
    
    def add_documents_to_knowledge_base(self, documents: List[Dict], collection_name: str = "schedule3_knowledge"):
        """Add documents to the RAG knowledge base"""
        # FIXED: Use consistent collection access
        if collection_name == "schedule3_knowledge":
            collection = self.schedule3_knowledge
        elif collection_name == "audit_cases":
            collection = self.audit_cases
        else:
            raise ValueError(f"Unknown collection: {collection_name}")
        
        texts = []
        metadatas = []
        ids = []
        
        for i, doc in enumerate(documents):
            texts.append(doc['content'])
            metadatas.append({
                'source': doc.get('source', 'unknown'),
                'type': doc.get('type', 'regulation'),
                'section': doc.get('section', 'general')
            })
            ids.append(f"{collection_name}_{i}")
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(documents)} documents to {collection_name}")
    
    def retrieve_relevant_context(self, query: str, n_results: int = 5) -> List[Dict]:
        """Retrieve relevant documents for a query"""
        query_embedding = self.embedding_model.encode([query]).tolist()[0]
        
        # FIXED: Use correct collection references
        try:
            # Search in Schedule III collection
            schedule3_results = self.schedule3_knowledge.query(
                query_embeddings=[query_embedding],
                n_results=max(1, n_results//2)
            )
            
            # Search in audit cases collection
            audit_results = self.audit_cases.query(
                query_embeddings=[query_embedding],
                n_results=max(1, n_results//2)
            )
        except Exception as e:
            print(f"Warning: Error querying collections: {e}")
            return []
        
        # Combine and format results
        relevant_docs = []
        
        # Process Schedule III results
        if schedule3_results['documents'] and schedule3_results['documents'][0]:
            for i, doc in enumerate(schedule3_results['documents'][0]):
                relevant_docs.append({
                    'content': doc,
                    'source': schedule3_results['metadatas'][0][i]['source'],
                    'type': schedule3_results['metadatas'][0][i]['type'],
                    'distance': schedule3_results['distances'][0][i]
                })
        
        # Process audit results
        if audit_results['documents'] and audit_results['documents'][0]:
            for i, doc in enumerate(audit_results['documents'][0]):
                relevant_docs.append({
                    'content': doc,
                    'source': audit_results['metadatas'][0][i]['source'],
                    'type': audit_results['metadatas'][0][i]['type'],
                    'distance': audit_results['distances'][0][i]
                })
        
        # Sort by relevance (lower distance = more relevant)
        relevant_docs.sort(key=lambda x: x['distance'])
        
        return relevant_docs[:n_results]
    
    def generate_rag_response(self, query: str, document_data: Dict = None) -> Dict:
        """Generate response using RAG with mistral"""
        
        # Retrieve relevant context
        relevant_context = self.retrieve_relevant_context(query)
        
        # Build context string
        context_string = "\n\n".join([
            f"Source: {doc['source']}\nContent: {doc['content']}"
            for doc in relevant_context
        ])
        
        # Include current document data if provided
        document_context = ""
        if document_data:
            document_context = f"\nCurrent Document Analysis:\n{json.dumps(document_data, indent=2)}\n"
        
        # Create enhanced prompt
        enhanced_prompt = f"""
        You are an expert financial auditor specializing in Schedule III compliance under the Companies Act.
        
        RELEVANT REGULATIONS AND PRECEDENTS:
        {context_string}
        
        {document_context}
        
        QUERY: {query}
        
        Based on the above regulations and precedents, provide a detailed analysis that includes:
        1. Specific regulatory requirements
        2. Compliance assessment
        3. Any violations or issues found
        4. Recommendations for correction
        5. References to specific sections/sources
        
        Ensure your response is grounded in the provided regulatory context.
        """
        
        try:
            response = ollama.chat(
                model=self.llama_model,
                messages=[{'role': 'user', 'content': enhanced_prompt}]
            )
            
            return {
                'analysis': response['message']['content'],
                'sources_used': [doc['source'] for doc in relevant_context],
                'context_documents': len(relevant_context),
                'query': query
            }
            
        except Exception as e:
            return {
                'error': f"RAG analysis failed: {str(e)}",
                'analysis': "Unable to perform RAG-enhanced analysis",
                'sources_used': [],
                'context_documents': 0,
                'query': query
            }
