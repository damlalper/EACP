"""
AutoGen / CrewAI-compatible Agent Template for EACP
Provides a multi-agent orchestration pattern for complex workflows.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent roles in the multi-agent system."""
    COORDINATOR = "coordinator"
    TASK_EXECUTOR = "task_executor"
    RESEARCH = "research"
    REVIEWER = "reviewer"


@dataclass
class AgentTask:
    """Definition of a task for an agent."""
    id: str
    description: str
    expected_output: str
    assigned_to: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"


class MultiAgentOrchestrator:
    """Multi-agent orchestrator compatible with AutoGen/CrewAI patterns."""

    def __init__(self, agents: Dict[str, Any], integrations: Optional[Dict[str, Any]] = None):
        """Initialize multi-agent orchestrator.
        
        Args:
            agents: Dictionary of agent instances by name
            integrations: Dictionary of connector instances
        """
        self.agents = agents
        self.integrations = integrations or {}
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: Dict[str, Any] = {}

    def register_task(self, task: AgentTask, assigned_agent: str) -> bool:
        """Register a task for an agent to execute.
        
        Args:
            task: Task to execute
            assigned_agent: Name of agent to execute task
            
        Returns:
            True if task registered successfully
        """
        if assigned_agent not in self.agents:
            logger.error(f"Agent {assigned_agent} not found")
            return False
        
        task.assigned_to = assigned_agent
        self.task_queue.append(task)
        logger.info(f"Task {task.id} registered for agent {assigned_agent}")
        return True

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a single task.
        
        Args:
            task: Task to execute
            
        Returns:
            Execution result
        """
        agent = self.agents.get(task.assigned_to)
        if not agent:
            return {"success": False, "error": f"Agent {task.assigned_to} not found"}

        try:
            logger.info(f"Executing task {task.id} with agent {task.assigned_to}")
            task.status = "in_progress"
            
            # Agent-specific execution (compatibility layer)
            if hasattr(agent, "process_task"):
                result = agent.process_task({
                    "description": task.description,
                    "expected_output": task.expected_output
                })
            elif hasattr(agent, "run"):
                result = agent.run(task.description)
            else:
                result = {"error": "Agent has no execution method"}
            
            task.status = "completed"
            self.completed_tasks[task.id] = result
            return {"success": True, "task_id": task.id, "result": result}
            
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            task.status = "failed"
            return {"success": False, "error": str(e)}

    def execute_workflow(self, workflow_description: str) -> Dict[str, Any]:
        """Execute a workflow (orchestrate multiple agents and tasks).
        
        Args:
            workflow_description: High-level workflow description
            
        Returns:
            Workflow execution result
        """
        logger.info(f"Starting workflow execution: {workflow_description}")
        results = []
        
        # Process tasks in order
        while self.task_queue:
            task = self.task_queue.pop(0)
            result = self.execute_task(task)
            results.append(result)
            
            if not result.get("success"):
                logger.warning(f"Task {task.id} failed, continuing with remaining tasks")
        
        return {
            "success": len([r for r in results if r.get("success")]) == len(results),
            "workflow": workflow_description,
            "completed_tasks": len(self.completed_tasks),
            "results": results
        }

    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get current status of an agent."""
        agent = self.agents.get(agent_name)
        if not agent:
            return {"error": f"Agent {agent_name} not found"}
        
        if hasattr(agent, "to_dict"):
            return agent.to_dict()
        elif hasattr(agent, "get_status"):
            return agent.get_status()
        else:
            return {"agent": agent_name, "status": "unknown"}

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get overall orchestrator status."""
        return {
            "agents": {name: self.get_agent_status(name) for name in self.agents.keys()},
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "integrations": list(self.integrations.keys())
        }
