"""
A/B Testing module for EACP LLMOps
Enables model versioning and A/B testing
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import random

logger = logging.getLogger(__name__)


class ABTesting:
    """A/B testing system for model versions"""
    
    def __init__(self):
        self.experiments = {}
        self.results = []
    
    def create_experiment(self, experiment_id: str, variants: List[Dict[str, Any]], 
                         traffic_split: Optional[Dict[str, float]] = None):
        """Create an A/B test experiment"""
        if traffic_split is None:
            # Equal split by default
            split = 1.0 / len(variants)
            traffic_split = {v["id"]: split for v in variants}
        
        experiment = {
            "id": experiment_id,
            "variants": variants,
            "traffic_split": traffic_split,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.experiments[experiment_id] = experiment
        logger.info(f"Created A/B test experiment: {experiment_id}")
        return experiment
    
    def select_variant(self, experiment_id: str, user_id: Optional[str] = None) -> str:
        """Select a variant for a user/request"""
        experiment = self.experiments.get(experiment_id)
        if not experiment or experiment["status"] != "active":
            return "default"
        
        # Use consistent hashing for user_id if provided
        if user_id:
            hash_value = hash(user_id + experiment_id) % 100
            cumulative = 0
            for variant_id, split in experiment["traffic_split"].items():
                cumulative += split * 100
                if hash_value < cumulative:
                    return variant_id
        
        # Random selection
        rand = random.random()
        cumulative = 0
        for variant_id, split in experiment["traffic_split"].items():
            cumulative += split
            if rand < cumulative:
                return variant_id
        
        return experiment["variants"][0]["id"]
    
    def record_result(self, experiment_id: str, variant_id: str, 
                     metrics: Dict[str, Any]):
        """Record A/B test result"""
        result = {
            "experiment_id": experiment_id,
            "variant_id": variant_id,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results.append(result)
        logger.info(f"Recorded A/B test result: {experiment_id}/{variant_id}")
    
    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get aggregated results for an experiment"""
        experiment_results = [r for r in self.results 
                             if r["experiment_id"] == experiment_id]
        
        variant_stats = {}
        for result in experiment_results:
            variant_id = result["variant_id"]
            if variant_id not in variant_stats:
                variant_stats[variant_id] = {
                    "count": 0,
                    "metrics": {}
                }
            
            variant_stats[variant_id]["count"] += 1
            for key, value in result["metrics"].items():
                if key not in variant_stats[variant_id]["metrics"]:
                    variant_stats[variant_id]["metrics"][key] = []
                variant_stats[variant_id]["metrics"][key].append(value)
        
        # Calculate averages
        for variant_id, stats in variant_stats.items():
            for metric, values in stats["metrics"].items():
                if isinstance(values[0], (int, float)):
                    stats["metrics"][metric] = {
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "count": len(values)
                    }
        
        return variant_stats
    
    def stop_experiment(self, experiment_id: str):
        """Stop an A/B test experiment"""
        if experiment_id in self.experiments:
            self.experiments[experiment_id]["status"] = "stopped"
            logger.info(f"Stopped A/B test experiment: {experiment_id}")
