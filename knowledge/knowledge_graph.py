"""
Knowledge Graph implementation for EACP
Manages relationships and context between entities
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """Knowledge graph for managing entity relationships"""
    
    def __init__(self):
        self.nodes = {}  # {node_id: {data, properties}}
        self.edges = {}  # {(source, target): {relationship, properties}}
        self.node_counter = 0
    
    def add_node(self, node_id: Optional[str] = None, 
                node_type: str = "entity", **properties) -> str:
        """Add a node to the knowledge graph"""
        if not node_id:
            node_id = f"node_{self.node_counter}"
            self.node_counter += 1
        
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "properties": properties,
            "created_at": datetime.now().isoformat()
        }
        
        return node_id
    
    def add_edge(self, source_id: str, target_id: str, 
                relationship: str, **properties):
        """Add an edge (relationship) between nodes"""
        if source_id not in self.nodes:
            raise ValueError(f"Source node {source_id} not found")
        if target_id not in self.nodes:
            raise ValueError(f"Target node {target_id} not found")
        
        edge_key = (source_id, target_id)
        self.edges[edge_key] = {
            "source": source_id,
            "target": target_id,
            "relationship": relationship,
            "properties": properties,
            "created_at": datetime.now().isoformat()
        }
    
    def query(self, query: str, max_results: int = 10, 
             node_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query the knowledge graph
        Simple text matching for now - can be enhanced with graph algorithms
        """
        results = []
        query_lower = query.lower()
        
        for node_id, node_data in self.nodes.items():
            # Filter by type if specified
            if node_type and node_data.get("type") != node_type:
                continue
            
            # Simple text matching in properties
            properties = node_data.get("properties", {})
            matches = False
            
            for key, value in properties.items():
                if isinstance(value, str) and query_lower in value.lower():
                    matches = True
                    break
            
            if matches:
                # Get connected nodes
                connected = self._get_connected_nodes(node_id)
                results.append({
                    "node": node_data,
                    "connected_nodes": connected,
                    "relevance_score": 1.0  # Placeholder
                })
        
        return results[:max_results]
    
    def _get_connected_nodes(self, node_id: str) -> List[Dict[str, Any]]:
        """Get nodes connected to the given node"""
        connected = []
        
        for (source, target), edge_data in self.edges.items():
            if source == node_id:
                target_node = self.nodes.get(target)
                if target_node:
                    connected.append({
                        "node": target_node,
                        "relationship": edge_data.get("relationship")
                    })
            elif target == node_id:
                source_node = self.nodes.get(source)
                if source_node:
                    connected.append({
                        "node": source_node,
                        "relationship": edge_data.get("relationship")
                    })
        
        return connected
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific node by ID"""
        return self.nodes.get(node_id)
    
    def get_relationships(self, node_id: str) -> List[Dict[str, Any]]:
        """Get all relationships for a node"""
        relationships = []
        
        for (source, target), edge_data in self.edges.items():
            if source == node_id or target == node_id:
                relationships.append(edge_data)
        
        return relationships
