"""
Main orchestrator for Enterprise AI Copilot Platform (EACP)
Coordinates multi-agent system and manages workflow
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from agents import TaskAgent, ResearchAgent, AutomationAgent
from llm import LocalLLMClient, LLMBenchmark, MultiProviderClient
from knowledge import VectorDB, EmbeddingGenerator, HybridSearch, KnowledgeGraph
from integrations import JiraConnector, AzureDevOpsConnector, SAPConnector, CRMConnector
from multi_modal import VisionAgent, AudioAgent, BrowserAutomation
from mlops import Monitoring, TaskLogger, ABTesting, GPUManager
from discovery import AIToolDiscovery, AITrendAnalyzer
from data_pipeline import ETLEngine, DocumentProcessor, DataValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EACPOrchestrator:
    """Main orchestrator for EACP platform"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.agents = {}
        self.llm_client = None
        self.knowledge_base = None
        self.integrations = {}
        self.mlops = {}
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all platform components"""
        logger.info("Initializing EACP components...")
        
        # Initialize LLM
        llm_config = self.config.get("llm", {})
        self.llm_client = LocalLLMClient(
            model_name=llm_config.get("model_name", "llama"),
            backend=llm_config.get("backend", "ollama")
        )
        
        # Initialize Knowledge Base
        self._initialize_knowledge_base()
        
        # Initialize Integrations
        self._initialize_integrations()
        
        # Initialize Agents
        self._initialize_agents()
        
        # Initialize Multi-Modal
        self._initialize_multimodal()
        
        # Initialize LLMOps
        self._initialize_mlops()

        # Initialize LLM Benchmark & Multi-Provider
        self._initialize_benchmark()

        # Initialize AI Discovery
        self._initialize_discovery()

        # Initialize Data Pipeline
        self._initialize_data_pipeline()

        logger.info("EACP initialization complete")
    
    def _initialize_knowledge_base(self):
        """Initialize knowledge management components"""
        # Vector DB
        vector_db_config = self.config.get("vector_db", {})
        vector_db = VectorDB(
            backend=vector_db_config.get("backend", "chroma"),
            **vector_db_config.get("config", {})
        )
        
        # Embedding Generator
        embedding_model = self.config.get("embeddings", {}).get("model_name", 
                                                                "sentence-transformers/all-MiniLM-L6-v2")
        embedding_generator = EmbeddingGenerator(model_name=embedding_model)
        
        # Hybrid Search
        hybrid_search = HybridSearch(vector_db=vector_db)
        
        # Knowledge Graph
        knowledge_graph = KnowledgeGraph()
        
        self.knowledge_base = {
            "vector_db": vector_db,
            "embeddings": embedding_generator,
            "hybrid_search": hybrid_search,
            "knowledge_graph": knowledge_graph
        }
    
    def _initialize_integrations(self):
        """Initialize enterprise integrations"""
        integrations_config = self.config.get("integrations", {})
        
        # JIRA
        if "jira" in integrations_config:
            self.integrations["jira"] = JiraConnector(integrations_config["jira"])
            self.integrations["jira"].authenticate()
        
        # Azure DevOps
        if "azure_devops" in integrations_config:
            self.integrations["azure_devops"] = AzureDevOpsConnector(
                integrations_config["azure_devops"]
            )
            self.integrations["azure_devops"].authenticate()
        
        # SAP
        if "sap" in integrations_config:
            self.integrations["sap"] = SAPConnector(integrations_config["sap"])
            self.integrations["sap"].authenticate()
        
        # CRM
        if "crm" in integrations_config:
            self.integrations["crm"] = CRMConnector(integrations_config["crm"])
            self.integrations["crm"].authenticate()
    
    def _initialize_agents(self):
        """Initialize agents"""
        # Task Agent
        self.agents["task"] = TaskAgent(
            llm_client=self.llm_client,
            integrations=self.integrations
        )
        
        # Research Agent
        self.agents["research"] = ResearchAgent(
            llm_client=self.llm_client,
            knowledge_base=self.knowledge_base,
            vector_db=self.knowledge_base["vector_db"]
        )
        
        # Automation Agent
        browser_automation = BrowserAutomation(headless=True)
        self.agents["automation"] = AutomationAgent(
            llm_client=self.llm_client,
            browser_automation=browser_automation
        )
    
    def _initialize_multimodal(self):
        """Initialize multi-modal agents"""
        self.vision_agent = VisionAgent(llm_client=self.llm_client)
        self.audio_agent = AudioAgent(llm_client=self.llm_client)
        self.browser_automation = BrowserAutomation(headless=True)
    
    def _initialize_mlops(self):
        """Initialize LLMOps components"""
        self.mlops["monitoring"] = Monitoring()
        self.mlops["logging"] = TaskLogger(
            log_file=self.config.get("logging", {}).get("log_file")
        )
        self.mlops["ab_testing"] = ABTesting()
        self.mlops["gpu_manager"] = GPUManager()

    def _initialize_benchmark(self):
        """Initialize LLM Benchmark & multi-provider support"""
        providers_config = self.config.get("llm", {}).get("providers", {})
        if providers_config:
            self.multi_provider = MultiProviderClient({"providers": providers_config})
            self.benchmark = LLMBenchmark(self.multi_provider)
            logger.info("LLM Benchmark engine initialized")
        else:
            self.multi_provider = None
            self.benchmark = None

    def _initialize_discovery(self):
        """Initialize AI Tool Discovery & Reporting"""
        self.discovery = AIToolDiscovery(llm_client=self.llm_client)
        self.trend_analyzer = AITrendAnalyzer(llm_client=self.llm_client)
        logger.info("AI Discovery engine initialized")

    def _initialize_data_pipeline(self):
        """Initialize Data Pipeline & ETL"""
        pipeline_config = self.config.get("data_pipeline", {})
        self.etl_engine = ETLEngine(config=pipeline_config)
        self.document_processor = DocumentProcessor(config=pipeline_config)
        self.data_validator = DataValidator()
        logger.info("Data Pipeline initialized")
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user request
        Expected format:
        {
            "agent": "task" | "research" | "automation",
            "action": "...",
            "data": {...}
        }
        """
        start_time = datetime.now()
        
        try:
            agent_name = request.get("agent", "task")
            agent = self.agents.get(agent_name)
            
            if not agent:
                return {
                    "success": False,
                    "error": f"Unknown agent: {agent_name}"
                }
            
            # Process task
            result = agent.process_task(request)
            
            # Log task
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.mlops["logging"].log_task(
                agent_id=agent_name,
                task=request,
                result=result,
                duration_ms=duration_ms
            )
            
            # Record metrics
            self.mlops["monitoring"].record_inference(
                latency_ms=duration_ms,
                memory_mb=0,  # Would get from system
                accuracy=1.0 if result.get("success") else 0.0
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Request processing error: {str(e)}")
            self.mlops["logging"].log_error(
                agent_id=request.get("agent", "unknown"),
                error=str(e),
                context=request
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get platform status"""
        status = {
            "agents": {name: agent.to_dict() for name, agent in self.agents.items()},
            "llm": self.llm_client.get_model_info() if self.llm_client else {},
            "integrations": list(self.integrations.keys()),
            "mlops": {
                "monitoring": self.mlops["monitoring"].get_statistics(),
                "alerts": len(self.mlops["monitoring"].get_alerts())
            },
            "benchmark": {
                "available_providers": self.multi_provider.get_available_providers() if self.multi_provider else [],
                "total_benchmarks": len(self.benchmark.benchmark_history) if self.benchmark else 0
            },
            "discovery": {
                "catalog_size": len(self.discovery.catalog) if self.discovery else 0,
                "reports_generated": len(self.discovery.reports) if self.discovery else 0
            },
            "data_pipeline": {
                "total_jobs": len(self.etl_engine.jobs) if self.etl_engine else 0,
                "documents_processed": self.document_processor.processed_count if self.document_processor else 0
            }
        }
        return status


def main():
    """Main entry point"""
    # Example configuration
    config = {
        "llm": {
            "model_name": "llama",
            "backend": "ollama"
        },
        "vector_db": {
            "backend": "chroma",
            "config": {
                "collection_name": "eacp_documents"
            }
        },
        "integrations": {
            "jira": {
                "base_url": "https://your-jira-instance.atlassian.net",
                "username": "user@example.com",
                "api_token": "your-api-token"
            }
        }
    }
    
    # Initialize orchestrator
    orchestrator = EACPOrchestrator(config=config)
    
    # Example request
    request = {
        "agent": "task",
        "action": "create_ticket",
        "data": {
            "title": "Test Ticket",
            "description": "This is a test ticket created by EACP",
            "system": "jira"
        }
    }
    
    result = orchestrator.process_request(request)
    print(f"Result: {result}")
    
    # Get status
    status = orchestrator.get_status()
    print(f"Platform Status: {status}")


if __name__ == "__main__":
    main()
