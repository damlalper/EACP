"""
LangChain-based Agent Template for EACP
Provides a production-ready agent with tool-calling, memory, and chain orchestration.
"""

from typing import Any, Dict, List, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_community.chat_models import ChatOpenAI
import logging

logger = logging.getLogger(__name__)


class LangChainEACPAgent:
    """LangChain-based EACP agent with function calling and memory management."""

    def __init__(self, model_name: str = "gpt-4", integrations: Optional[Dict[str, Any]] = None):
        """Initialize LangChain agent.
        
        Args:
            model_name: OpenAI model name (e.g., "gpt-4", "gpt-3.5-turbo")
            integrations: Dictionary of connector instances (jira, azure_devops, crm, sap)
        """
        self.integrations = integrations or {}
        self.llm = ChatOpenAI(model_name=model_name, temperature=0)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.tools = self._build_tools()
        self.agent_executor = self._build_executor()

    def _build_tools(self) -> List[Any]:
        """Define tool functions for the agent."""

        @tool
        def create_jira_ticket(title: str, description: str, project_key: str = "PROJ") -> str:
            """Create a JIRA ticket.
            
            Args:
                title: Ticket title
                description: Ticket description
                project_key: JIRA project key
            """
            try:
                connector = self.integrations.get("jira")
                if not connector:
                    return "JIRA connector not configured"
                result = connector.create_ticket(
                    title=title, 
                    description=description, 
                    project_key=project_key
                )
                return f"Created JIRA ticket: {result.get('key', result.get('id'))}"
            except Exception as e:
                return f"Error creating JIRA ticket: {str(e)}"

        @tool
        def create_azure_devops_work_item(title: str, description: str, work_item_type: str = "Task") -> str:
            """Create an Azure DevOps work item.
            
            Args:
                title: Work item title
                description: Work item description
                work_item_type: Type of work item (Task, Bug, User Story)
            """
            try:
                connector = self.integrations.get("azure_devops")
                if not connector:
                    return "Azure DevOps connector not configured"
                result = connector.create_work_item(
                    title=title,
                    description=description,
                    work_item_type=work_item_type
                )
                return f"Created Azure DevOps item: {result.get('id')}"
            except Exception as e:
                return f"Error creating work item: {str(e)}"

        @tool
        def create_crm_contact(name: str, email: str) -> str:
            """Create a CRM contact.
            
            Args:
                name: Contact name
                email: Contact email
            """
            try:
                connector = self.integrations.get("crm")
                if not connector:
                    return "CRM connector not configured"
                result = connector.create_contact(name=name, email=email)
                return f"Created CRM contact: {result.get('id')}"
            except Exception as e:
                return f"Error creating contact: {str(e)}"

        @tool
        def assign_jira_task(task_id: str, assignee: str) -> str:
            """Assign a JIRA task to a user.
            
            Args:
                task_id: Task ID
                assignee: Assignee account ID
            """
            try:
                connector = self.integrations.get("jira")
                if not connector:
                    return "JIRA connector not configured"
                result = connector.assign_task(task_id=task_id, assignee=assignee)
                return f"Assigned task {task_id} to {assignee}"
            except Exception as e:
                return f"Error assigning task: {str(e)}"

        return [
            create_jira_ticket,
            create_azure_devops_work_item,
            create_crm_contact,
            assign_jira_task
        ]

    def _build_executor(self) -> AgentExecutor:
        """Build the agent executor."""
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=None  # Uses default prompt; can customize
        )
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=5
        )

    def process_request(self, user_input: str) -> Dict[str, Any]:
        """Process a natural language request and execute tools as needed.
        
        Args:
            user_input: Natural language user request
            
        Returns:
            Result of agent execution
        """
        try:
            logger.info(f"Processing request: {user_input}")
            result = self.agent_executor.invoke({"input": user_input})
            return {
                "success": True,
                "output": result.get("output"),
                "agent": "langchain"
            }
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": "langchain"
            }

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history from memory."""
        return self.memory.buffer_as_messages if hasattr(self.memory, "buffer_as_messages") else []
