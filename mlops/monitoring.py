"""
Monitoring module for EACP LLMOps
Tracks inference latency, memory usage, accuracy, and other metrics
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)


class Monitoring:
    """Monitoring system for LLM operations"""
    
    def __init__(self):
        self.metrics = {
            "inference_latency": [],
            "memory_usage": [],
            "accuracy_scores": [],
            "error_count": 0,
            "total_requests": 0
        }
        self.alerts = []
    
    def record_inference(self, latency_ms: float, memory_mb: float, 
                       accuracy: Optional[float] = None):
        """Record inference metrics"""
        timestamp = datetime.now().isoformat()
        
        self.metrics["inference_latency"].append({
            "timestamp": timestamp,
            "latency_ms": latency_ms
        })
        
        self.metrics["memory_usage"].append({
            "timestamp": timestamp,
            "memory_mb": memory_mb
        })
        
        if accuracy is not None:
            self.metrics["accuracy_scores"].append({
                "timestamp": timestamp,
                "accuracy": accuracy
            })
        
        self.metrics["total_requests"] += 1
        
        # Check thresholds
        self._check_thresholds(latency_ms, memory_mb)
    
    def _check_thresholds(self, latency_ms: float, memory_mb: float):
        """Check if metrics exceed thresholds and generate alerts"""
        if latency_ms > 500:  # 500ms threshold
            self._add_alert("high_latency", f"Latency {latency_ms}ms exceeds threshold")
        
        if memory_mb > 8000:  # 8GB threshold
            self._add_alert("high_memory", f"Memory {memory_mb}MB exceeds threshold")
    
    def _add_alert(self, alert_type: str, message: str):
        """Add an alert"""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.alerts.append(alert)
        logger.warning(f"Alert: {message}")
    
    def get_metrics(self, metric_type: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics, optionally filtered by type"""
        if metric_type:
            return {metric_type: self.metrics.get(metric_type, [])}
        return self.metrics
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistical summary of metrics"""
        latencies = [m["latency_ms"] for m in self.metrics["inference_latency"]]
        memories = [m["memory_mb"] for m in self.metrics["memory_usage"]]
        accuracies = [m["accuracy"] for m in self.metrics["accuracy_scores"]]
        
        stats = {
            "total_requests": self.metrics["total_requests"],
            "error_count": self.metrics["error_count"],
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) if latencies else 0,
            "avg_memory_mb": sum(memories) / len(memories) if memories else 0,
            "avg_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0
        }
        
        return stats
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get all alerts"""
        return self.alerts
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
