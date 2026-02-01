"""
Embedding generation for EACP
Supports sentence-transformers and domain-specific embeddings
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text data"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model initialized: {self.model_name}")
        except ImportError:
            logger.warning("Sentence-transformers not installed, using mock")
            self.model = "mock"
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {str(e)}")
            self.model = "mock"
    
    def generate(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if self.model == "mock":
            # Return mock embedding
            return [0.0] * 384  # Typical embedding dimension
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation error: {str(e)}")
            return [0.0] * 384
    
    def generate_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        if self.model == "mock":
            return [[0.0] * 384 for _ in texts]
        
        try:
            embeddings = self.model.encode(texts, batch_size=batch_size, 
                                         convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Batch embedding generation error: {str(e)}")
            return [[0.0] * 384 for _ in texts]
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        if self.model == "mock":
            return 384
        return self.model.get_sentence_embedding_dimension()
