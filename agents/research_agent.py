"""
Research Agent - Handles literature review, trend analysis, and information retrieval
Uses vector DB and knowledge graph for enterprise knowledge management
"""

from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent, AgentMemory
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Agent responsible for research, information retrieval, and knowledge management"""
    
    def __init__(self, llm_client=None, knowledge_base=None, vector_db=None):
        super().__init__("research_agent", llm_client)
        self.knowledge_base = knowledge_base
        self.vector_db = vector_db
        
        # Register default tools
        self.register_tool("semantic_search", self._semantic_search)
        self.register_tool("keyword_search", self._keyword_search)
        self.register_tool("hybrid_search", self._hybrid_search)
        self.register_tool("knowledge_graph_query", self._knowledge_graph_query)
        self.register_tool("generate_report", self._generate_report)
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a research task
        Expected task format:
        {
            "query": "search query",
            "type": "semantic" | "keyword" | "hybrid" | "knowledge_graph",
            "filters": {...},
            "max_results": 10
        }
        """
        try:
            self.status = "processing"
            query = task.get("query", "")
            search_type = task.get("type", "hybrid")
            max_results = task.get("max_results", 10)
            
            logger.info(f"ResearchAgent processing query: {query[:50]}...")
            
            # Update memory
            self.update_memory({
                "query": query,
                "type": search_type,
                "status": "processing"
            })
            
            # Perform search based on type
            if search_type == "semantic":
                results = self._semantic_search(query=query, max_results=max_results)
            elif search_type == "keyword":
                results = self._keyword_search(query=query, max_results=max_results)
            elif search_type == "knowledge_graph":
                results = self._knowledge_graph_query(query=query, max_results=max_results)
            else:  # hybrid
                results = self._hybrid_search(query=query, max_results=max_results)
            
            # Generate summary/report if requested
            if task.get("generate_report", False):
                report = self._generate_report(query=query, results=results)
                results["report"] = report
            
            self.status = "idle"
            return {
                "success": True,
                "agent": "research_agent",
                "query": query,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"ResearchAgent error: {str(e)}")
            self.status = "error"
            return {
                "success": False,
                "error": str(e),
                "agent": "research_agent"
            }
    
    def _semantic_search(self, query: str, max_results: int = 10, **kwargs) -> Dict[str, Any]:
        """Perform semantic search using vector DB"""
        if not self.vector_db:
            return {"error": "Vector DB not configured"}
        
        try:
            results = self.vector_db.semantic_search(query=query, top_k=max_results, **kwargs)
            return {
                "type": "semantic",
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return {"error": str(e)}
    
    def _keyword_search(self, query: str, max_results: int = 10, **kwargs) -> Dict[str, Any]:
        """Perform keyword search"""
        if not self.knowledge_base:
            return {"error": "Knowledge base not configured"}
        
        try:
            results = self.knowledge_base.keyword_search(query=query, max_results=max_results, **kwargs)
            return {
                "type": "keyword",
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Keyword search error: {str(e)}")
            return {"error": str(e)}
    
    def _hybrid_search(self, query: str, max_results: int = 10, **kwargs) -> Dict[str, Any]:
        """Perform hybrid search (semantic + keyword)"""
        semantic_results = self._semantic_search(query=query, max_results=max_results)
        keyword_results = self._keyword_search(query=query, max_results=max_results)
        
        # Combine and deduplicate results
        combined_results = []
        seen_ids = set()
        
        for result in semantic_results.get("results", []):
            result_id = result.get("id")
            if result_id and result_id not in seen_ids:
                combined_results.append({**result, "source": "semantic"})
                seen_ids.add(result_id)
        
        for result in keyword_results.get("results", []):
            result_id = result.get("id")
            if result_id and result_id not in seen_ids:
                combined_results.append({**result, "source": "keyword"})
                seen_ids.add(result_id)
        
        # Re-rank if LLM available
        if self.llm_client and len(combined_results) > 0:
            combined_results = self._rerank_results(query, combined_results)
        
        return {
            "type": "hybrid",
            "query": query,
            "results": combined_results[:max_results],
            "count": len(combined_results)
        }
    
    def _knowledge_graph_query(self, query: str, max_results: int = 10, **kwargs) -> Dict[str, Any]:
        """Query knowledge graph for relationships and context"""
        if not self.knowledge_base or not hasattr(self.knowledge_base, 'knowledge_graph'):
            return {"error": "Knowledge graph not configured"}
        
        try:
            results = self.knowledge_base.knowledge_graph.query(query=query, max_results=max_results, **kwargs)
            return {
                "type": "knowledge_graph",
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Knowledge graph query error: {str(e)}")
            return {"error": str(e)}
    
    def _rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-rank search results using LLM"""
        # Simple re-ranking - can be enhanced with LLM-based scoring
        # For now, return as-is
        return results
    
    def _generate_report(self, query: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a research report from search results"""
        if not self.llm_client:
            return {"error": "LLM client not available for report generation"}
        
        try:
            # Format results for LLM
            formatted_results = "\n\n".join([
                f"Result {i+1}:\n{result.get('content', result.get('text', ''))}"
                for i, result in enumerate(results.get("results", [])[:5])
            ])
            
            prompt = f"""
            Based on the following search results for the query "{query}",
            generate a comprehensive research report.
            
            Search Results:
            {formatted_results}
            
            Please provide:
            1. Executive summary
            2. Key findings
            3. Recommendations
            """
            
            report = self.llm_client.generate(prompt=prompt)
            
            return {
                "query": query,
                "report": report,
                "sources_count": len(results.get("results", [])),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Report generation error: {str(e)}")
            return {"error": str(e)}
    
    def delegate_to_agent(self, target_agent: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate task to another agent"""
        logger.info(f"ResearchAgent delegating to {target_agent}")
        
        self.update_memory({
            "action": "delegate",
            "target_agent": target_agent,
            "task": task
        })
        
        return {
            "delegated": True,
            "from": "research_agent",
            "to": target_agent,
            "task": task
        }
