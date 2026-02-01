"""
Base Agent Class for EACP
Provides common functionality for all agents including memory management,
tool calling, and inter-agent communication.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class AgentMemory:
    """Memory structure for agent context and history"""
    task_history: List[Dict[str, Any]]
    context: Dict[str, Any]
    last_updated: datetime


class BaseAgent(ABC):
    """Base class for all agents in EACP"""
    
    def __init__(self, agent_id: str, llm_client=None, memory: Optional[AgentMemory] = None):
        self.agent_id = agent_id
        self.llm_client = llm_client
        self.memory = memory or AgentMemory(task_history=[], context={}, last_updated=datetime.now())
        self.tools = {}
        self.status = "idle"
    
    def register_tool(self, tool_name: str, tool_func):
        """Register a tool/function that the agent can call"""
        self.tools[tool_name] = tool_func
    
    def update_memory(self, task: Dict[str, Any]):
        """Update agent memory with new task information"""
        self.memory.task_history.append({
            **task,
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id
        })
        self.memory.last_updated = datetime.now()
    
    def get_context(self) -> Dict[str, Any]:
        """Get current agent context from memory"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "recent_tasks": self.memory.task_history[-5:],  # Last 5 tasks
            "context": self.memory.context
        }
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call a registered tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not registered")
        return self.tools[tool_name](**kwargs)
    
    @abstractmethod
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def delegate_to_agent(self, target_agent: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate task to another agent"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize agent state"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "memory": {
                "task_count": len(self.memory.task_history),
                "last_updated": self.memory.last_updated.isoformat()
            }
        }
