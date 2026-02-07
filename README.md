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

### 🏆 LLM Benchmark & Comparison
- **Multi-Provider Support**: OpenAI GPT-4, Anthropic Claude, Google Gemini, Ollama (local)
- **Standardized Benchmarks**: Reasoning, coding, summarization, creativity, instruction following, knowledge
- **Metrics**: Latency, token usage, cost estimation, quality scoring (completeness, relevance, conciseness)
- **Comparison Reports**: Provider rankings by speed, quality, cost, and best-value
- **Cost Analysis**: Per-query cost tracking, monthly projections per provider

### 🔍 AI Tool Discovery & Reporting
- **AI Ecosystem Catalog**: Tracks 20+ agent frameworks, LLM models, dev tools, and RAG libraries
- **Tool Evaluation**: LLM-powered analysis with relevance scoring and recommendations (adopt/trial/assess/hold)
- **Trend Analysis**: Multi-agent systems, local LLMs, reasoning models, vibe coding trends
- **Periodic Reports**: Weekly AI discovery digests with actionable recommendations
- **Tool Comparison**: Side-by-side comparison of tools by pricing, maturity, and use cases

### 📦 Data Pipeline & ETL
- **Multi-Format Ingestion**: PDF, DOCX, HTML, CSV, JSON, JSONL, Markdown, plain text
- **RAG Data Preparation**: Automatic chunking with overlap, metadata enrichment
- **Fine-Tuning Dataset Prep**: Alpaca, ShareGPT, and OpenAI chat format conversion
- **Data Validation**: Schema checks, quality scoring, duplicate detection
- **URL & API Extraction**: Web scraping and REST API data ingestion
- **Job Management**: Tracking, status monitoring, and error reporting

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
| **OpenAI** | ✓ (Free credits) | [platform.openai.com](https://platform.openai.com/api-keys) | GPT-4, GPT-4o, GPT-3.5-turbo |
| **Anthropic** | ✓ (Free credits) | [console.anthropic.com](https://console.anthropic.com) | Claude Sonnet 4.5, Claude Opus 4.6 |
| **Google Gemini** | ✓ (Free tier) | [aistudio.google.com](https://aistudio.google.com) | Gemini Pro, Gemini Ultra |
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
│   ├── local_model/     # Ollama, vLLM, LLaMA backends
│   ├── fine_tune/       # LoRA/QLoRA fine-tuning
│   └── benchmark/       # LLM Benchmark & Comparison
│       ├── providers.py       # Multi-provider client (OpenAI, Claude, Gemini, Ollama)
│       └── llm_benchmark.py   # Benchmark engine & reporting
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
├── discovery/           # AI Tool Discovery & Reporting
│   ├── ai_discovery.py        # Tool catalog & ecosystem tracking
│   └── trend_analyzer.py      # AI trend analysis & weekly digests
├── data_pipeline/       # Data Pipeline & ETL
│   ├── etl_engine.py          # Extract-Transform-Load pipeline
│   ├── document_processor.py  # Multi-format document processing
│   └── data_validator.py      # Data quality validation
├── prompts/            # Prompt templates
│   ├── agent_prompts/
│   └── fine_tuning_prompts/
├── examples/           # Usage examples
│   ├── benchmark_example.py       # LLM comparison demo
│   ├── discovery_example.py       # AI tool discovery demo
│   └── data_pipeline_example.py   # ETL pipeline demo
├── main.py             # Main orchestrator
├── config.yaml.example # Configuration template
└── requirements.txt   # Dependencies
```

## Configuration

See `config.yaml.example` for detailed configuration options. Key settings include:

- **LLM**: Model selection, backend configuration, and multi-provider API keys
- **Vector DB**: Database backend and connection settings
- **Integrations**: Enterprise system credentials
- **LLMOps**: Monitoring thresholds and logging configuration
- **Data Pipeline**: Chunk size, output directory, supported formats
- **Discovery**: Report frequency and focus areas

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

### LLM Benchmark & Comparison
```python
from llm.benchmark import LLMBenchmark, MultiProviderClient

# Initialize multi-provider client
client = MultiProviderClient({"providers": {
    "openai": {"api_key": "...", "model": "gpt-4o"},
    "anthropic": {"api_key": "...", "model": "claude-sonnet-4-5-20250929"},
    "gemini": {"api_key": "...", "model": "gemini-pro"},
    "ollama": {"model": "llama3"}
}})

# Run full benchmark across all providers
benchmark = LLMBenchmark(client)
report = benchmark.run_benchmark(prompt_categories=["reasoning", "coding"])
print(report["rankings"])  # Rankings by speed, quality, cost

# Quick single-prompt comparison
result = benchmark.compare_on_prompt("Explain the CAP theorem in 3 sentences.")
```

### AI Tool Discovery & Reporting
```python
from discovery import AIToolDiscovery, AITrendAnalyzer

# Initialize discovery engine
discovery = AIToolDiscovery()

# Search the AI ecosystem catalog
results = discovery.search_catalog(query="agent", pricing="open-source")

# Evaluate a tool's relevance
discovery.evaluate_tool("CrewAI", "Excellent for multi-agent orchestration", relevance_score=0.9)

# Generate weekly AI report
report = discovery.generate_report(period_days=7, focus_areas=["agent_frameworks"])
print(report.summary)

# Analyze a new tool with LLM
analyzer = AITrendAnalyzer(llm_client=llm)
analysis = analyzer.analyze_tool("NewFramework", "A new agent orchestration library")
```

### Data Pipeline & ETL
```python
from data_pipeline import ETLEngine, DocumentProcessor, DataValidator

# Process documents for RAG
etl = ETLEngine(config={"output_dir": "data/processed"})
job = etl.create_job(
    name="Ingest company docs",
    source_type="directory",
    source_config={"path": "documents/", "extensions": [".pdf", ".docx"]},
    target="rag"
)
result = etl.run_job(job.job_id)

# Prepare fine-tuning dataset
job = etl.create_job(
    name="Prepare training data",
    source_type="jsonl",
    source_config={"path": "data/training.jsonl", "format": "alpaca"},
    target="fine_tuning"
)
result = etl.run_job(job.job_id)

# Validate data quality
validator = DataValidator()
validation = validator.validate_rag_documents(documents)
print(f"Valid: {validation['valid']}, Invalid: {validation['invalid']}")
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
3. **LLM Layer**: Local model deployment, fine-tuning, and multi-provider benchmark
4. **Knowledge Layer**: Vector DB and knowledge graph
5. **Integration Layer**: Enterprise system connectors
6. **LLMOps Layer**: Monitoring, logging, and optimization
7. **Discovery Layer**: AI tool tracking, trend analysis, and team reporting
8. **Data Pipeline Layer**: ETL for RAG ingestion and fine-tuning dataset preparation

## Contributing

Contributions are welcome! Please see the contributing guidelines for details.


## Author

DAMLA ALPER - 2026

## References

- PRD: See `PRD.MD` for detailed product requirements
- Task Flow: See `TASK_FLOW.MD` for implementation flow
