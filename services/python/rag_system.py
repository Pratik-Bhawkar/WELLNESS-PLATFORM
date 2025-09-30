"""
RAG (Retrieval-Augmented Generation) System with FAISS
Provides intelligent document retrieval for mental wellness conversations
"""

import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import faiss
from sentence_transformers import SentenceTransformer
import PyPDF2
import docx
import markdown
from pathlib import Path
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Represents a chunk of document content with metadata"""
    content: str
    source: str
    chunk_id: int
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None

class DocumentProcessor:
    """Processes different document types and extracts text content"""
    
    def __init__(self):
        self.supported_formats = {'.pdf', '.txt', '.md', '.docx'}
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX files"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading TXT {file_path}: {e}")
            return ""
    
    def extract_text_from_md(self, file_path: str) -> str:
        """Extract text from Markdown files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
                # Convert markdown to plain text (removing formatting)
                html = markdown.markdown(md_content)
                # Simple HTML tag removal (for basic extraction)
                import re
                text = re.sub('<[^<]+?>', '', html)
                return text
        except Exception as e:
            logger.error(f"Error reading MD {file_path}: {e}")
            return ""
    
    def process_document(self, file_path: str) -> str:
        """Process a document and extract text based on file type"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension not in self.supported_formats:
            logger.warning(f"Unsupported file format: {extension}")
            return ""
        
        if extension == '.pdf':
            return self.extract_text_from_pdf(str(file_path))
        elif extension == '.docx':
            return self.extract_text_from_docx(str(file_path))
        elif extension == '.txt':
            return self.extract_text_from_txt(str(file_path))
        elif extension == '.md':
            return self.extract_text_from_md(str(file_path))
        
        return ""

class TextChunker:
    """Splits text into manageable chunks for embedding and retrieval"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, source: str) -> List[DocumentChunk]:
        """Split text into overlapping chunks"""
        chunks = []
        sentences = text.split('.')
        
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                # Create chunk
                chunks.append(DocumentChunk(
                    content=current_chunk.strip(),
                    source=source,
                    chunk_id=chunk_id,
                    metadata={
                        'length': len(current_chunk),
                        'type': 'content_chunk'
                    }
                ))
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.overlap:] if len(current_chunk) > self.overlap else current_chunk
                current_chunk = overlap_text + " " + sentence + "."
                chunk_id += 1
            else:
                current_chunk += " " + sentence + "."
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                source=source,
                chunk_id=chunk_id,
                metadata={
                    'length': len(current_chunk),
                    'type': 'content_chunk'
                }
            ))
        
        return chunks

class RAGVectorStore:
    """FAISS-based vector store for document retrieval"""
    
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the vector store with embedding model"""
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
        self.document_chunks: List[DocumentChunk] = []
        self.document_processor = DocumentProcessor()
        self.text_chunker = TextChunker()
        
        logger.info(f"Initialized RAG Vector Store with {embedding_model_name}")
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def add_documents(self, documents_dir: str) -> int:
        """Add all documents from a directory to the vector store"""
        documents_path = Path(documents_dir)
        if not documents_path.exists():
            logger.error(f"Documents directory not found: {documents_dir}")
            return 0
        
        added_count = 0
        
        for file_path in documents_path.iterdir():
            if file_path.is_file():
                logger.info(f"Processing document: {file_path.name}")
                
                # Extract text from document
                text_content = self.document_processor.process_document(str(file_path))
                
                if not text_content or len(text_content.strip()) < 50:
                    logger.warning(f"Insufficient content in {file_path.name}, skipping")
                    continue
                
                # Split into chunks
                chunks = self.text_chunker.chunk_text(text_content, file_path.name)
                
                if not chunks:
                    logger.warning(f"No chunks created for {file_path.name}")
                    continue
                
                # Generate embeddings for chunks
                embeddings = self._generate_embeddings([chunk.content for chunk in chunks])
                
                # Add embeddings to chunks and store
                for chunk, embedding in zip(chunks, embeddings):
                    chunk.embedding = embedding
                    self.document_chunks.append(chunk)
                
                # Add to FAISS index
                self.index.add(np.array(embeddings).astype('float32'))
                
                added_count += len(chunks)
                logger.info(f"Added {len(chunks)} chunks from {file_path.name}")
        
        logger.info(f"Total documents processed: {added_count} chunks from {len(list(documents_path.iterdir()))} files")
        return added_count
    
    def _generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for a list of texts"""
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            # Normalize embeddings for cosine similarity
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            # Convert to list of arrays if it's a single array
            if len(texts) == 1:
                return [embeddings[0]]
            else:
                return list(embeddings)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    def search(self, query: str, k: int = 5, score_threshold: float = 0.1) -> List[Tuple[DocumentChunk, float]]:
        """Search for relevant document chunks"""
        if self.index.ntotal == 0:
            logger.warning("No documents in vector store")
            return []
        
        try:
            logger.debug(f"Starting search for query: '{query[:50]}...'")
            
            # Generate query embedding
            query_embeddings = self._generate_embeddings([query])
            if not query_embeddings or len(query_embeddings) == 0:
                logger.error("Failed to generate query embedding")
                return []
            
            logger.debug("Generated query embedding successfully")
            query_embedding = query_embeddings[0]
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            
            # Search FAISS index
            logger.debug("Searching FAISS index...")
            scores, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
            logger.debug(f"FAISS search completed. Got {len(scores[0])} results")
            
            # Debug: Log all scores (safely convert numpy types)
            try:
                all_scores = [(float(score), int(idx)) for score, idx in zip(scores[0], indices[0])]
                logger.info(f"Query: '{query[:50]}...' | Top scores: {all_scores[:3]}")
            except Exception as e:
                logger.warning(f"Error logging scores: {e}")
            
            # Filter results by score threshold
            results = []
            try:
                for i in range(len(scores[0])):
                    score_float = float(scores[0][i])  # Explicit index access
                    idx_int = int(indices[0][i])       # Explicit index access
                    
                    if score_float >= score_threshold and idx_int < len(self.document_chunks):
                        chunk = self.document_chunks[idx_int]
                        results.append((chunk, score_float))
            except Exception as e:
                logger.error(f"Error filtering results: {e}")
                return []
            
            # If no results with threshold, return top result anyway (with very low threshold)
            if not results and len(scores[0]) > 0:
                try:
                    logger.info(f"No results above threshold {score_threshold}, returning top result")
                    top_idx = int(indices[0][0])
                    top_score = float(scores[0][0])
                    if top_idx < len(self.document_chunks):
                        chunk = self.document_chunks[top_idx]
                        results.append((chunk, top_score))
                except Exception as e:
                    logger.error(f"Error getting top result: {e}")
                    return []
            
            logger.info(f"Found {len(results)} relevant chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    def save_index(self, save_path: str):
        """Save the FAISS index and document chunks"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, f"{save_path}/faiss_index.bin")
            
            # Save document chunks
            with open(f"{save_path}/document_chunks.pkl", 'wb') as f:
                pickle.dump(self.document_chunks, f)
            
            # Save metadata
            metadata = {
                'embedding_model': self.embedding_model,
                'embedding_dim': self.embedding_dim,
                'total_chunks': len(self.document_chunks)
            }
            
            with open(f"{save_path}/metadata.json", 'w') as f:
                json.dump({k: v for k, v in metadata.items() if k != 'embedding_model'}, f, indent=2)
            
            logger.info(f"Saved vector store to {save_path}")
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def load_index(self, load_path: str) -> bool:
        """Load a saved FAISS index and document chunks"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{load_path}/faiss_index.bin")
            
            # Load document chunks
            with open(f"{load_path}/document_chunks.pkl", 'rb') as f:
                self.document_chunks = pickle.load(f)
            
            logger.info(f"Loaded vector store from {load_path}")
            logger.info(f"Loaded {len(self.document_chunks)} document chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        source_counts = {}
        for chunk in self.document_chunks:
            source = chunk.source
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return {
            'total_chunks': len(self.document_chunks),
            'embedding_dimension': self.embedding_dim,
            'index_size': self.index.ntotal,
            'documents_by_source': source_counts
        }

class MentalWellnessRAG:
    """Mental Wellness specific RAG system"""
    
    def __init__(self, documents_dir: str, vector_store_path: str = None):
        self.vector_store = RAGVectorStore()
        self.documents_dir = documents_dir
        self.vector_store_path = vector_store_path or os.path.join(documents_dir, "../data/vector_store")
        
        # Mental wellness specific keywords for context enhancement
        self.wellness_keywords = {
            'anxiety': ['anxious', 'worry', 'panic', 'nervous', 'fear', 'stress'],
            'depression': ['sad', 'hopeless', 'depressed', 'down', 'empty', 'worthless'],
            'stress': ['overwhelmed', 'pressure', 'tension', 'burden', 'exhausted'],
            'trauma': ['ptsd', 'flashback', 'traumatic', 'trigger', 'abuse'],
            'therapy': ['cbt', 'counseling', 'treatment', 'therapeutic', 'mindfulness'],
            'crisis': ['suicide', 'self-harm', 'crisis', 'emergency', 'help']
        }
    
    def initialize(self) -> bool:
        """Initialize the RAG system"""
        try:
            # Try to load existing index
            if os.path.exists(self.vector_store_path):
                logger.info("Loading existing vector store...")
                if self.vector_store.load_index(self.vector_store_path):
                    logger.info("Successfully loaded existing vector store")
                    return True
            
            # Create new index from documents
            logger.info("Creating new vector store from documents...")
            os.makedirs(self.vector_store_path, exist_ok=True)
            
            added_count = self.vector_store.add_documents(self.documents_dir)
            
            if added_count > 0:
                self.vector_store.save_index(self.vector_store_path)
                logger.info(f"Created vector store with {added_count} chunks")
                return True
            else:
                logger.error("No documents were processed successfully")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
            return False
    
    def enhance_query(self, query: str, context_type: str = None) -> str:
        """Enhance query with wellness-specific context"""
        enhanced_query = query.lower()
        
        # Add relevant keywords based on detected context
        if context_type:
            context_keywords = self.wellness_keywords.get(context_type.lower(), [])
            for keyword in context_keywords[:2]:  # Add top 2 related keywords
                if keyword not in enhanced_query:
                    enhanced_query += f" {keyword}"
        
        return enhanced_query
    
    def retrieve_context(self, query: str, context_type: str = None, k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant context for a query"""
        # Enhance query with wellness context
        enhanced_query = self.enhance_query(query, context_type)
        
        # Search vector store
        results = self.vector_store.search(enhanced_query, k=k, score_threshold=0.05)
        
        # Format results
        context_chunks = []
        for chunk, score in results:
            context_chunks.append({
                'content': chunk.content,
                'source': chunk.source,
                'relevance_score': score,
                'metadata': chunk.metadata
            })
        
        return context_chunks
    
    def get_rag_response_context(self, query: str, context_type: str = None) -> str:
        """Get formatted context for RAG-enhanced responses"""
        context_chunks = self.retrieve_context(query, context_type, k=3)
        
        if not context_chunks:
            return ""
        
        # Format context for the AI model
        context_text = "Relevant information from mental wellness resources:\n\n"
        
        for i, chunk in enumerate(context_chunks, 1):
            context_text += f"{i}. From {chunk['source']} (relevance: {chunk['relevance_score']:.2f}):\n"
            context_text += f"{chunk['content'][:300]}...\n\n"
        
        return context_text
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        return self.vector_store.get_stats()

# Example usage and testing
def main():
    """Test the RAG system"""
    documents_dir = "../../documents"
    
    # Initialize RAG system
    rag = MentalWellnessRAG(documents_dir)
    
    if rag.initialize():
        print("✅ RAG System initialized successfully!")
        
        # Show statistics
        stats = rag.get_statistics()
        print(f"\n📊 Vector Store Statistics:")
        print(f"Total chunks: {stats['total_chunks']}")
        print(f"Embedding dimension: {stats['embedding_dimension']}")
        print(f"Documents: {len(stats['documents_by_source'])}")
        
        # Test queries
        test_queries = [
            ("I'm feeling very anxious about work", "anxiety"),
            ("I can't sleep and feel hopeless", "depression"),
            ("What are some mindfulness techniques?", "therapy"),
            ("I'm having panic attacks", "anxiety")
        ]
        
        print(f"\n🔍 Testing RAG retrieval:")
        for query, context_type in test_queries:
            print(f"\nQuery: {query}")
            print(f"Context Type: {context_type}")
            
            context = rag.get_rag_response_context(query, context_type)
            if context:
                print(f"Retrieved context: {len(context)} characters")
                print(f"Preview: {context[:200]}...")
            else:
                print("No relevant context found")
    else:
        print("❌ Failed to initialize RAG system")

if __name__ == "__main__":
    main()