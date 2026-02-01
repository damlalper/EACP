"""
Task Agent - Handles project management, ticket assignment, and task tracking
Integrates with JIRA, Azure DevOps, and CRM systems
"""

from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent, AgentMemory
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TaskAgent(BaseAgent):
    """Agent responsible for task management and workflow orchestration"""
    
    def __init__(self, llm_client=None, integrations=None):
        super().__init__("task_agent", llm_client)
        self.integrations = integrations or {}
        self.active_tasks = {}
        
        # Register default tools
        self.register_tool("create_ticket", self._create_ticket)
        self.register_tool("assign_task", self._assign_task)
        self.register_tool("update_task_status", self._update_task_status)
        self.register_tool("get_task_summary", self._get_task_summary)
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task request
        Expected task format:
        {
            "action": "create_ticket" | "assign_task" | "get_summary",
            "data": {...},
            "priority": "high" | "medium" | "low"
        }
        """
        try:
            self.status = "processing"
            action = task.get("action", "unknown")
            task_data = task.get("data", {})
            
            logger.info(f"TaskAgent processing action: {action}")
            
            # Update memory
            self.update_memory({
                "action": action,
                "data": task_data,
                "status": "processing"
            })
            
            # Route to appropriate handler
            if action == "create_ticket":
                result = self._create_ticket(**task_data)
            elif action == "assign_task":
                result = self._assign_task(**task_data)
            elif action == "get_summary":
                result = self._get_task_summary(**task_data)
            else:
                result = {"error": f"Unknown action: {action}"}
            
            # Store active task
            task_id = result.get("task_id") or task_data.get("task_id")
            if task_id:
                self.active_tasks[task_id] = {
                    **task,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            
            self.status = "idle"
            return {
                "success": True,
                "agent": "task_agent",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"TaskAgent error: {str(e)}")
            self.status = "error"
            return {
                "success": False,
                "error": str(e),
                "agent": "task_agent"
            }
    
    def _create_ticket(self, title: str, description: str, 
                      system: str = "jira", **kwargs) -> Dict[str, Any]:
        """Create a ticket in the specified system"""
        connector = self.integrations.get(system)
        if not connector:
            return {"error": f"No connector for system: {system}"}
        
        try:
            ticket = connector.create_ticket(title=title, description=description, **kwargs)
            return {
                "task_id": ticket.get("id"),
                "status": "created",
                "system": system,
                "ticket": ticket
            }
        except Exception as e:
            logger.error(f"Failed to create ticket: {str(e)}")
            return {"error": str(e)}
    
    def _assign_task(self, task_id: str, assignee: str, 
                    system: str = "jira", **kwargs) -> Dict[str, Any]:
        """Assign a task to a user"""
        connector = self.integrations.get(system)
        if not connector:
            return {"error": f"No connector for system: {system}"}
        
        try:
            result = connector.assign_task(task_id=task_id, assignee=assignee, **kwargs)
            return {
                "task_id": task_id,
                "assignee": assignee,
                "status": "assigned",
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to assign task: {str(e)}")
            return {"error": str(e)}
    
    def _update_task_status(self, task_id: str, status: str, 
                           system: str = "jira", **kwargs) -> Dict[str, Any]:
        """Update task status"""
        connector = self.integrations.get(system)
        if not connector:
            return {"error": f"No connector for system: {system}"}
        
        try:
            result = connector.update_status(task_id=task_id, status=status, **kwargs)
            return {
                "task_id": task_id,
                "status": status,
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to update task status: {str(e)}")
            return {"error": str(e)}
    
    def _get_task_summary(self, task_id: Optional[str] = None, 
                         filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Get summary of tasks"""
        if task_id:
            task = self.active_tasks.get(task_id)
            if task:
                return {
                    "task_id": task_id,
                    "summary": task.get("result", {}),
                    "status": task.get("status", "unknown")
                }
        
        # Get summary from memory
        recent_tasks = self.memory.task_history[-10:]
        return {
            "total_tasks": len(self.active_tasks),
            "recent_tasks": recent_tasks,
            "filters": filters or {}
        }
    
    def delegate_to_agent(self, target_agent: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate task to another agent (e.g., Research Agent for information needs)"""
        logger.info(f"TaskAgent delegating to {target_agent}")
        
        # Store delegation in memory
        self.update_memory({
            "action": "delegate",
            "target_agent": target_agent,
            "task": task
        })
        
        return {
            "delegated": True,
            "from": "task_agent",
            "to": target_agent,
            "task": task
        }
