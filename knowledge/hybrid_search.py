"""
Hybrid search implementation combining semantic and keyword search
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class HybridSearch:
    """Hybrid search combining semantic and keyword search"""
    
    def __init__(self, vector_db=None, keyword_index=None):
        self.vector_db = vector_db
        self.keyword_index = keyword_index
        self.semantic_weight = 0.7
        self.keyword_weight = 0.3
    
    def search(self, query: str, top_k: int = 10, 
              filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Perform hybrid search
        Returns combined and re-ranked results
        """
        results = []
        
        # Semantic search
        if self.vector_db:
            try:
                semantic_results = self.vector_db.semantic_search(
                    query=query, 
                    top_k=top_k * 2,  # Get more for re-ranking
                    filters=filters
                )
                for result in semantic_results:
                    result["score"] = result.get("score", 0.0) * self.semantic_weight
                    result["source"] = "semantic"
                    results.append(result)
            except Exception as e:
                logger.error(f"Semantic search error: {str(e)}")
        
        # Keyword search
        if self.keyword_index:
            try:
                keyword_results = self.keyword_index.search(
                    query=query,
                    top_k=top_k * 2,
                    filters=filters
                )
                for result in keyword_results:
                    result["score"] = result.get("score", 0.0) * self.keyword_weight
                    result["source"] = "keyword"
                    results.append(result)
            except Exception as e:
                logger.error(f"Keyword search error: {str(e)}")
        
        # Combine and deduplicate
        combined_results = self._combine_results(results)
        
        # Re-rank
        reranked_results = self._rerank(query, combined_results)
        
        return reranked_results[:top_k]
    
    def _combine_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine results from different sources, deduplicate by ID"""
        seen_ids = {}
        
        for result in results:
            result_id = result.get("id")
            if not result_id:
                continue
            
            if result_id not in seen_ids:
                seen_ids[result_id] = result
            else:
                # Merge scores from different sources
                existing = seen_ids[result_id]
                existing["score"] = max(existing.get("score", 0), result.get("score", 0))
                existing["sources"] = existing.get("sources", []) + [result.get("source")]
        
        return list(seen_ids.values())
    
    def _rerank(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-rank results based on combined scores"""
        # Sort by score descending
        sorted_results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
        return sorted_results
    
    def set_weights(self, semantic_weight: float, keyword_weight: float):
        """Set weights for semantic and keyword search"""
        total = semantic_weight + keyword_weight
        self.semantic_weight = semantic_weight / total
        self.keyword_weight = keyword_weight / total
