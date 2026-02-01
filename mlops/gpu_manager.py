"""
GPU Resource Manager for EACP
Manages GPU allocation, optimization, and cost-aware model selection
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GPUManager:
    """GPU resource manager for LLM inference"""
    
    def __init__(self):
        self.gpu_resources = {}
        self.model_allocations = {}
        self.cost_tracking = {}
    
    def register_gpu(self, gpu_id: str, specs: Dict[str, Any]):
        """Register a GPU resource"""
        self.gpu_resources[gpu_id] = {
            **specs,
            "allocated": False,
            "current_model": None,
            "memory_used_mb": 0
        }
        logger.info(f"Registered GPU: {gpu_id}")
    
    def allocate_model(self, model_name: str, gpu_id: Optional[str] = None) -> str:
        """Allocate GPU for a model"""
        if gpu_id:
            if gpu_id not in self.gpu_resources:
                raise ValueError(f"GPU {gpu_id} not found")
            target_gpu = gpu_id
        else:
            # Find available GPU
            target_gpu = self._find_available_gpu()
            if not target_gpu:
                raise RuntimeError("No available GPU")
        
        self.gpu_resources[target_gpu]["allocated"] = True
        self.gpu_resources[target_gpu]["current_model"] = model_name
        self.model_allocations[model_name] = target_gpu
        
        logger.info(f"Allocated GPU {target_gpu} for model {model_name}")
        return target_gpu
    
    def _find_available_gpu(self) -> Optional[str]:
        """Find an available GPU"""
        for gpu_id, gpu_info in self.gpu_resources.items():
            if not gpu_info["allocated"]:
                return gpu_id
        return None
    
    def deallocate_model(self, model_name: str):
        """Deallocate GPU from a model"""
        gpu_id = self.model_allocations.get(model_name)
        if gpu_id:
            self.gpu_resources[gpu_id]["allocated"] = False
            self.gpu_resources[gpu_id]["current_model"] = None
            del self.model_allocations[model_name]
            logger.info(f"Deallocated GPU {gpu_id} from model {model_name}")
    
    def get_gpu_status(self, gpu_id: Optional[str] = None) -> Dict[str, Any]:
        """Get GPU status"""
        if gpu_id:
            return self.gpu_resources.get(gpu_id, {})
        return self.gpu_resources
    
    def optimize_allocation(self) -> Dict[str, Any]:
        """Optimize GPU allocation based on usage"""
        # Placeholder for optimization logic
        logger.info("GPU allocation optimization (placeholder)")
        return {
            "optimized": True,
            "recommendations": []
        }
    
    def track_cost(self, model_name: str, inference_time_ms: float, 
                  cost_per_ms: float = 0.001):
        """Track inference cost"""
        cost = inference_time_ms * cost_per_ms
        
        if model_name not in self.cost_tracking:
            self.cost_tracking[model_name] = {
                "total_cost": 0,
                "inference_count": 0
            }
        
        self.cost_tracking[model_name]["total_cost"] += cost
        self.cost_tracking[model_name]["inference_count"] += 1
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary"""
        total_cost = sum(t["total_cost"] for t in self.cost_tracking.values())
        return {
            "total_cost": total_cost,
            "by_model": self.cost_tracking
        }
