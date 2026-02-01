"""
Automation Agent - Handles browser automation, repetitive tasks, and data scraping
"""

from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent, AgentMemory
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AutomationAgent(BaseAgent):
    """Agent responsible for automation tasks, browser operations, and data scraping"""
    
    def __init__(self, llm_client=None, browser_automation=None):
        super().__init__("automation_agent", llm_client)
        self.browser_automation = browser_automation
        
        # Register default tools
        self.register_tool("scrape_data", self._scrape_data)
        self.register_tool("extract_table", self._extract_table)
        self.register_tool("fill_form", self._fill_form)
        self.register_tool("click_element", self._click_element)
        self.register_tool("generate_summary", self._generate_summary)
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an automation task
        Expected task format:
        {
            "action": "scrape" | "extract_table" | "fill_form" | "click",
            "url": "https://...",
            "data": {...}
        }
        """
        try:
            self.status = "processing"
            action = task.get("action", "unknown")
            url = task.get("url", "")
            task_data = task.get("data", {})
            
            logger.info(f"AutomationAgent processing action: {action} for {url}")
            
            # Update memory
            self.update_memory({
                "action": action,
                "url": url,
                "status": "processing"
            })
            
            # Route to appropriate handler
            if action == "scrape":
                result = self._scrape_data(url=url, **task_data)
            elif action == "extract_table":
                result = self._extract_table(url=url, **task_data)
            elif action == "fill_form":
                result = self._fill_form(url=url, **task_data)
            elif action == "click":
                result = self._click_element(url=url, **task_data)
            else:
                result = {"error": f"Unknown action: {action}"}
            
            self.status = "idle"
            return {
                "success": True,
                "agent": "automation_agent",
                "action": action,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AutomationAgent error: {str(e)}")
            self.status = "error"
            return {
                "success": False,
                "error": str(e),
                "agent": "automation_agent"
            }
    
    def _scrape_data(self, url: str, selectors: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Scrape data from a webpage"""
        if not self.browser_automation:
            return {"error": "Browser automation not configured"}
        
        try:
            data = self.browser_automation.scrape(url=url, selectors=selectors, **kwargs)
            return {
                "url": url,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Scraping error: {str(e)}")
            return {"error": str(e)}
    
    def _extract_table(self, url: str, table_selector: Optional[str] = None, 
                      format: str = "csv", **kwargs) -> Dict[str, Any]:
        """Extract table data from webpage"""
        if not self.browser_automation:
            return {"error": "Browser automation not configured"}
        
        try:
            table_data = self.browser_automation.extract_table(
                url=url, 
                selector=table_selector,
                format=format,
                **kwargs
            )
            return {
                "url": url,
                "table_data": table_data,
                "format": format,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Table extraction error: {str(e)}")
            return {"error": str(e)}
    
    def _fill_form(self, url: str, form_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Fill and submit a form"""
        if not self.browser_automation:
            return {"error": "Browser automation not configured"}
        
        try:
            result = self.browser_automation.fill_form(url=url, form_data=form_data, **kwargs)
            return {
                "url": url,
                "form_data": form_data,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Form filling error: {str(e)}")
            return {"error": str(e)}
    
    def _click_element(self, url: str, selector: str, **kwargs) -> Dict[str, Any]:
        """Click an element on a webpage"""
        if not self.browser_automation:
            return {"error": "Browser automation not configured"}
        
        try:
            result = self.browser_automation.click_element(url=url, selector=selector, **kwargs)
            return {
                "url": url,
                "selector": selector,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Click element error: {str(e)}")
            return {"error": str(e)}
    
    def _generate_summary(self, data: Any, summary_type: str = "general") -> Dict[str, Any]:
        """Generate summary of scraped data or meeting notes"""
        if not self.llm_client:
            return {"error": "LLM client not available for summary generation"}
        
        try:
            # Format data for LLM
            if isinstance(data, dict):
                formatted_data = str(data)
            elif isinstance(data, list):
                formatted_data = "\n".join([str(item) for item in data])
            else:
                formatted_data = str(data)
            
            prompt = f"""
            Generate a {summary_type} summary of the following data:
            
            {formatted_data}
            
            Please provide:
            1. Key points
            2. Important information
            3. Action items (if any)
            """
            
            summary = self.llm_client.generate(prompt=prompt)
            
            return {
                "summary_type": summary_type,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Summary generation error: {str(e)}")
            return {"error": str(e)}
    
    def delegate_to_agent(self, target_agent: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate task to another agent"""
        logger.info(f"AutomationAgent delegating to {target_agent}")
        
        self.update_memory({
            "action": "delegate",
            "target_agent": target_agent,
            "task": task
        })
        
        return {
            "delegated": True,
            "from": "automation_agent",
            "to": target_agent,
            "task": task
        }
