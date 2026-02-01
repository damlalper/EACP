# Enterprise AI Copilot Platform (EACP)

A production-ready multi-agent AI platform for enterprise systems integration, local LLM deployment, RAG pipelines, and MLOps orchestration.

## Features

### 🤖 Agent Framework
- **Task Agent**: Manages project workflows (JIRA, Azure DevOps, CRM)
- **Research Agent**: Knowledge retrieval and semantic search
- **Automation Agent**: Browser automation and workflow execution
- **LangChain Integration**: Function-calling, tool use, conversation memory
- **Multi-Agent Orchestration**: AutoGen/CrewAI-compatible task coordination

### 🔌 Enterprise Integrations
- **JIRA**: Create tickets, assign tasks, update status (API token auth)
- **Azure DevOps**: Work items, project management (PAT auth)
- **HubSpot CRM**: Contact and deal management (free tier available)
- **SAP**: HTTP/OData function execution (enterprise gateway)

### 🧠 Knowledge & RAG
- **Vector Databases**: Pinecone, Chroma, Weaviate, Qdrant
- **Embeddings Pipeline**: Sentence-transformers, chunking optimization
- **Hybrid Search**: Semantic + keyword search orchestration
- **Knowledge Graph**: Entity relationships and context

### 🚀 Local LLM & Optimization
- **Local Deployment**: Ollama, vLLM, llama.cpp backends
- **Model Fine-tuning**: LoRA, QLoRA, PEFT support
- **Prompt Engineering**: Optimization and evaluation framework
- **Cost Optimization**: Model selection and inference benchmarking

### 📊 MLOps & Infrastructure
- **Monitoring & Logging**: Real-time metrics, performance tracking
- **A/B Testing**: Model comparison and evaluation
- **API Gateway**: Rate limiting, request validation
- **GPU Management**: Resource allocation and optimization
- **Docker & Kubernetes**: Containerization and orchestration

### 🎬 Multi-Modal AI
- **Vision**: Image analysis, OCR, document processing
- **Audio**: Speech-to-text, meeting transcription
- **Browser Automation**: Web scraping, interaction automation

---

## Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd EACP
pip install -r requirements.txt
```

### 2. Configuration

Copy and edit the configuration file:

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml` with your credentials:

```yaml
integrations:
  jira:
    base_url: "https://your-domain.atlassian.net"
    username: "your-email@example.com"
    api_token: "YOUR_API_TOKEN"  # Get from: https://id.atlassian.com/manage-profile/security/api-tokens
```

### 3. Running Smoke Tests

Validate your integrations:

```bash
python scripts/integration_smoketest.py
```

### 4. Run Main Orchestrator

```bash
python main.py
```

---

## API Keys & Credentials

### Free Tier / Trial Services

| Service | Free Tier | Where to Get | Notes |
|---------|-----------|--------------|-------|
| **JIRA** | ✓ (Cloud) | [Atlassian](https://id.atlassian.com/manage-profile/security/api-tokens) | API token auth |
| **Azure DevOps** | ✓ | [dev.azure.com](https://dev.azure.com) | Personal Access Token (PAT) |
| **HubSpot** | ✓ | [hubspot.com/developers](https://developers.hubspot.com) | Free CRM + Private App |
| **Pinecone** | ✓ (Starter) | [pinecone.io](https://www.pinecone.io) | Free serverless index |
| **Qdrant** | ✓ (Cloud trial) | [qdrant.tech](https://qdrant.tech) | Managed or self-hosted |
| **Ollama** | ✓ (Local) | [ollama.ai](https://ollama.ai) | Local LLM, no API key needed |
| **SAP** | ❌ | Enterprise gateway | Requires company access |

## Project Structure

```
EACP/
├── agents/              # Agent implementations
│   ├── base_agent.py
│   ├── task_agent.py
│   ├── research_agent.py
│   └── automation_agent.py
├── llm/                 # LLM modules
│   ├── local_model/
│   └── fine_tune/
├── knowledge/           # Knowledge management
│   ├── vector_db.py
│   ├── embeddings.py
│   ├── hybrid_search.py
│   └── knowledge_graph.py
├── integrations/        # Enterprise connectors
│   ├── jira_connector.py
│   ├── azure_devops_connector.py
│   ├── sap_connector.py
│   └── crm_connector.py
├── mlops/              # LLMOps infrastructure
│   ├── monitoring.py
│   ├── logging.py
│   ├── ab_testing.py
│   └── gpu_manager.py
├── multi_modal/        # Multi-modal agents
│   ├── vision_agent.py
│   ├── audio_agent.py
│   └── browser_automation.py
├── prompts/            # Prompt templates
│   ├── agent_prompts/
│   └── fine_tuning_prompts/
├── main.py             # Main orchestrator
├── config.yaml.example # Configuration template
└── requirements.txt   # Dependencies
```

## Configuration

See `config.yaml.example` for detailed configuration options. Key settings include:

- **LLM**: Model selection and backend configuration
- **Vector DB**: Database backend and connection settings
- **Integrations**: Enterprise system credentials
- **LLMOps**: Monitoring thresholds and logging configuration

## Usage Examples

### Task Management
```python
# Create a JIRA ticket
request = {
    "agent": "task",
    "action": "create_ticket",
    "data": {
        "title": "Bug Fix",
        "description": "Fix authentication issue",
        "system": "jira",
        "priority": "high"
    }
}
result = orchestrator.process_request(request)
```

### Research & Knowledge Retrieval
```python
# Search enterprise knowledge base
request = {
    "agent": "research",
    "query": "authentication best practices",
    "type": "hybrid",
    "max_results": 10
}
result = orchestrator.process_request(request)
```

### Automation
```python
# Scrape data from website
request = {
    "agent": "automation",
    "action": "scrape",
    "url": "https://example.com",
    "data": {
        "selectors": {
            "title": "h1",
            "content": ".content"
        }
    }
}
result = orchestrator.process_request(request)
```

## Success Metrics

- Task automation accuracy ≥ 90%
- Knowledge retrieval latency ≤ 300ms
- Multi-agent orchestration success ≥ 95%
- Local LLM inference latency ≤ 500ms
- Cost reduction in AI ops ≥ 20%

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
flake8 .
```

## Architecture

EACP follows a modular, agent-based architecture:

1. **Orchestrator**: Coordinates multi-agent workflows
2. **Agents**: Specialized AI agents for different tasks
3. **LLM Layer**: Local model deployment and fine-tuning
4. **Knowledge Layer**: Vector DB and knowledge graph
5. **Integration Layer**: Enterprise system connectors
6. **LLMOps Layer**: Monitoring, logging, and optimization

## Contributing

Contributions are welcome! Please see the contributing guidelines for details.

## License

[Specify your license here]

## Author

DAMLA ALPER - 2026

## References

- PRD: See `PRD.MD` for detailed product requirements
- Task Flow: See `TASK_FLOW.MD` for implementation flow
