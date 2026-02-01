"""
Monitoring module for EACP LLMOps
Tracks inference latency, memory usage, accuracy, and other metrics
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and store performance metrics."""
    
    def __init__(self):
        self.latencies = []
        self.memory_usage = []
        self.accuracy = []
        self.errors = []
        self.timestamps = []
    
    def record_latency(self, latency: float):
        """Record inference latency in seconds."""
        self.latencies.append(latency)
        self.timestamps.append(datetime.now())
    
    def record_memory_usage(self, memory_gb: float):
        """Record memory usage in GB."""
        self.memory_usage.append(memory_gb)
    
    def record_accuracy(self, accuracy: float):
        """Record model accuracy (0-1)."""
        self.accuracy.append(accuracy)
    
    def record_error(self, error: str):
        """Record error."""
        self.errors.append({
            "error": error,
            "timestamp": datetime.now()
        })
    
    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get statistical summary of all metrics."""
        stats = {}
        
        if self.latencies:
            stats["latency"] = {
                "average": sum(self.latencies) / len(self.latencies),
                "min": min(self.latencies),
                "max": max(self.latencies),
                "count": len(self.latencies)
            }
        
        if self.memory_usage:
            stats["memory"] = {
                "average": sum(self.memory_usage) / len(self.memory_usage),
                "min": min(self.memory_usage),
                "max": max(self.memory_usage),
                "count": len(self.memory_usage)
            }
        
        if self.accuracy:
            stats["accuracy"] = {
                "average": sum(self.accuracy) / len(self.accuracy),
                "min": min(self.accuracy),
                "max": max(self.accuracy),
                "count": len(self.accuracy)
            }
        
        return stats
    
    def reset(self):
        """Reset all metrics."""
        self.latencies = []
        self.memory_usage = []
        self.accuracy = []
        self.errors = []
        self.timestamps = []


class PerformanceMonitor:
    """Monitor performance and generate alerts."""
    
    def __init__(self, latency_threshold: float = 0.5, memory_threshold: float = 8.0,
                 accuracy_threshold: float = 0.8):
        """
        Initialize performance monitor.
        
        Args:
            latency_threshold: Latency threshold in seconds
            memory_threshold: Memory threshold in GB
            accuracy_threshold: Accuracy threshold (0-1)
        """
        self.latency_threshold = latency_threshold
        self.memory_threshold = memory_threshold
        self.accuracy_threshold = accuracy_threshold
        self.alerts = []
    
    def check_latency(self, latency: float) -> bool:
        """Check if latency exceeds threshold."""
        if latency > self.latency_threshold:
            self.add_alert(
                alert_type="performance",
                severity="high",
                message=f"Latency {latency:.3f}s exceeds threshold {self.latency_threshold}s",
                metrics={"latency_s": latency}
            )
            return False
        return True
    
    def check_memory(self, memory: float) -> bool:
        """Check if memory exceeds threshold."""
        if memory > self.memory_threshold:
            self.add_alert(
                alert_type="resource",
                severity="critical",
                message=f"Memory {memory:.2f}GB exceeds threshold {self.memory_threshold}GB",
                metrics={"memory_gb": memory}
            )
            return False
        return True
    
    def check_accuracy(self, accuracy: float) -> bool:
        """Check if accuracy is below threshold."""
        if accuracy < self.accuracy_threshold:
            self.add_alert(
                alert_type="model",
                severity="medium",
                message=f"Accuracy {accuracy:.4f} below threshold {self.accuracy_threshold}",
                metrics={"accuracy": accuracy}
            )
            return False
        return True
    
    def add_alert(self, alert_type: str, severity: str, message: str,
                  metrics: Optional[Dict] = None):
        """Add an alert."""
        alert = {
            "type": alert_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics or {}
        }
        self.alerts.append(alert)
        logger.warning(f"[{severity.upper()}] {message}")
    
    def get_alerts(self, severity: Optional[str] = None) -> List[Dict]:
        """Get alerts, optionally filtered by severity."""
        if severity:
            return [a for a in self.alerts if a["severity"] == severity]
        return self.alerts
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts = []
    
    def clear_alerts_by_severity(self, severity: str):
        """Clear alerts of specific severity."""
        self.alerts = [a for a in self.alerts if a["severity"] != severity]


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
