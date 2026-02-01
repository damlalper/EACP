"""
Logging module for EACP LLMOps
Logs task execution, agent decisions, and system events
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class TaskLogger:
    """Logger for task execution and agent decisions"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.logs = []
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def log_task(self, agent_id: str, task: Dict[str, Any], 
                result: Dict[str, Any], duration_ms: float):
        """Log a task execution"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "task": task,
            "result": result,
            "duration_ms": duration_ms,
            "status": "success" if result.get("success") else "error"
        }
        
        self.logs.append(log_entry)
        logger.info(f"Task logged: {agent_id} - {task.get('action', 'unknown')}")
        
        if self.log_file:
            self._write_to_file(log_entry)
    
    def log_agent_decision(self, agent_id: str, decision: Dict[str, Any]):
        """Log an agent decision"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "agent_decision",
            "agent_id": agent_id,
            "decision": decision
        }
        
        self.logs.append(log_entry)
        logger.info(f"Agent decision logged: {agent_id}")
        
        if self.log_file:
            self._write_to_file(log_entry)
    
    def log_error(self, agent_id: str, error: str, context: Optional[Dict] = None):
        """Log an error"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "agent_id": agent_id,
            "error": error,
            "context": context or {}
        }
        
        self.logs.append(log_entry)
        logger.error(f"Error logged: {agent_id} - {error}")
        
        if self.log_file:
            self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: Dict[str, Any]):
        """Write log entry to file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to write log to file: {str(e)}")
    
    def get_logs(self, agent_id: Optional[str] = None, 
                limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs, optionally filtered by agent"""
        logs = self.logs
        if agent_id:
            logs = [log for log in logs if log.get("agent_id") == agent_id]
        return logs[-limit:]
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs = []
