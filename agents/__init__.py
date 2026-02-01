"""
EACP Agents Module
"""

from agents.base_agent import BaseAgent, AgentMemory
from agents.task_agent import TaskAgent
from agents.research_agent import ResearchAgent
from agents.automation_agent import AutomationAgent

__all__ = [
    "BaseAgent",
    "AgentMemory",
    "TaskAgent",
    "ResearchAgent",
    "AutomationAgent"
]
