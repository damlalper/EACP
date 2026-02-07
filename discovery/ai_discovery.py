"""
AI Tool Discovery Engine for EACP
Researches, catalogs, and reports on new AI tools, frameworks, and models
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class AITool:
    """Represents a discovered AI tool/framework/model"""
    name: str
    category: str  # framework, model, tool, library, platform
    description: str
    url: str = ""
    github_url: str = ""
    stars: int = 0
    license: str = ""
    language: str = ""
    tags: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    pricing: str = ""  # free, freemium, paid, open-source
    maturity: str = ""  # experimental, beta, stable, production
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    relevance_score: float = 0.0  # 0-1 how relevant to our stack
    evaluated: bool = False
    evaluation_notes: str = ""


@dataclass
class DiscoveryReport:
    """Weekly/periodic AI discovery report"""
    report_id: str
    period_start: str
    period_end: str
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    new_tools: List[Dict[str, Any]] = field(default_factory=list)
    new_models: List[Dict[str, Any]] = field(default_factory=list)
    trending_topics: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""


# Built-in AI ecosystem knowledge base
AI_ECOSYSTEM_CATALOG = {
    "agent_frameworks": [
        {
            "name": "CrewAI",
            "category": "framework",
            "description": "Framework for orchestrating role-playing autonomous AI agents",
            "language": "Python",
            "tags": ["multi-agent", "orchestration", "roles"],
            "use_cases": ["Multi-agent workflows", "Task delegation", "Role-based agents"],
            "pricing": "open-source",
            "maturity": "stable"
        },
        {
            "name": "LangGraph",
            "category": "framework",
            "description": "Library for building stateful, multi-actor applications with LLMs using graph-based workflows",
            "language": "Python",
            "tags": ["graph", "stateful", "multi-agent", "langchain"],
            "use_cases": ["Complex workflows", "Stateful conversations", "Agent coordination"],
            "pricing": "open-source",
            "maturity": "stable"
        },
        {
            "name": "AutoGen",
            "category": "framework",
            "description": "Microsoft's framework for multi-agent conversational AI systems",
            "language": "Python",
            "tags": ["multi-agent", "conversation", "microsoft"],
            "use_cases": ["Conversational agents", "Code generation", "Group chat agents"],
            "pricing": "open-source",
            "maturity": "stable"
        },
        {
            "name": "Semantic Kernel",
            "category": "framework",
            "description": "Microsoft's SDK for integrating LLMs into applications with plugin architecture",
            "language": "Python/C#",
            "tags": ["sdk", "plugins", "microsoft", "enterprise"],
            "use_cases": ["Enterprise AI", "Plugin-based agents", ".NET integration"],
            "pricing": "open-source",
            "maturity": "production"
        },
        {
            "name": "Haystack",
            "category": "framework",
            "description": "End-to-end NLP framework for building search and RAG pipelines",
            "language": "Python",
            "tags": ["rag", "search", "pipeline", "nlp"],
            "use_cases": ["RAG pipelines", "Semantic search", "Question answering"],
            "pricing": "open-source",
            "maturity": "production"
        },
        {
            "name": "Claude Agent SDK",
            "category": "framework",
            "description": "Anthropic's official SDK for building custom AI agents with Claude",
            "language": "Python",
            "tags": ["agent", "anthropic", "claude", "sdk"],
            "use_cases": ["Custom agents", "Tool use", "Agentic workflows"],
            "pricing": "open-source",
            "maturity": "stable"
        }
    ],
    "llm_models": [
        {
            "name": "LLaMA 3",
            "category": "model",
            "description": "Meta's open-source large language model family",
            "tags": ["open-source", "meta", "local"],
            "use_cases": ["Local deployment", "Fine-tuning", "Research"],
            "pricing": "open-source",
            "maturity": "production"
        },
        {
            "name": "Mistral / Mixtral",
            "category": "model",
            "description": "High-performance open-source models with MoE architecture",
            "tags": ["open-source", "moe", "efficient"],
            "use_cases": ["Local deployment", "Cost-effective inference", "Coding"],
            "pricing": "open-source",
            "maturity": "production"
        },
        {
            "name": "Qwen 2.5",
            "category": "model",
            "description": "Alibaba's multilingual model family with strong coding capabilities",
            "tags": ["open-source", "multilingual", "coding"],
            "use_cases": ["Multilingual tasks", "Coding", "Local deployment"],
            "pricing": "open-source",
            "maturity": "stable"
        },
        {
            "name": "DeepSeek V3 / R1",
            "category": "model",
            "description": "DeepSeek's reasoning-focused models with strong math and coding",
            "tags": ["reasoning", "coding", "math", "open-source"],
            "use_cases": ["Complex reasoning", "Math", "Code generation"],
            "pricing": "open-source",
            "maturity": "stable"
        },
        {
            "name": "Phi-3 / Phi-4",
            "category": "model",
            "description": "Microsoft's small but capable language models for edge/mobile deployment",
            "tags": ["small", "efficient", "microsoft", "edge"],
            "use_cases": ["Edge deployment", "Mobile AI", "Resource-constrained environments"],
            "pricing": "open-source",
            "maturity": "stable"
        }
    ],
    "dev_tools": [
        {
            "name": "Claude Code",
            "category": "tool",
            "description": "Anthropic's agentic CLI for software engineering with Claude",
            "tags": ["cli", "coding", "anthropic", "agent"],
            "use_cases": ["Code generation", "Debugging", "Refactoring", "Vibe coding"],
            "pricing": "paid",
            "maturity": "production"
        },
        {
            "name": "Cursor",
            "category": "tool",
            "description": "AI-first code editor with built-in LLM integration and rules/subagents",
            "tags": ["ide", "coding", "ai-editor"],
            "use_cases": ["AI-assisted coding", "Code completion", "Refactoring"],
            "pricing": "freemium",
            "maturity": "production"
        },
        {
            "name": "Ollama",
            "category": "tool",
            "description": "Run open-source LLMs locally with a simple CLI",
            "tags": ["local", "cli", "model-serving"],
            "use_cases": ["Local LLM deployment", "Development", "Privacy-first AI"],
            "pricing": "open-source",
            "maturity": "production"
        },
        {
            "name": "LM Studio",
            "category": "tool",
            "description": "Desktop app for discovering, downloading, and running local LLMs",
            "tags": ["local", "desktop", "gui", "model-serving"],
            "use_cases": ["Local model management", "Easy model testing", "Chat interface"],
            "pricing": "free",
            "maturity": "stable"
        },
        {
            "name": "Hugging Face TGI",
            "category": "tool",
            "description": "Text Generation Inference server for high-throughput LLM serving",
            "tags": ["inference", "server", "production"],
            "use_cases": ["Production LLM serving", "High throughput", "Batch inference"],
            "pricing": "open-source",
            "maturity": "production"
        }
    ],
    "rag_and_data": [
        {
            "name": "LlamaIndex",
            "category": "framework",
            "description": "Data framework for connecting custom data sources to LLMs",
            "tags": ["rag", "data", "indexing", "retrieval"],
            "use_cases": ["RAG pipelines", "Data ingestion", "Document QA"],
            "pricing": "open-source",
            "maturity": "production"
        },
        {
            "name": "Unstructured",
            "category": "library",
            "description": "ETL library for preprocessing documents (PDF, HTML, DOCX) for LLMs",
            "tags": ["etl", "document-processing", "preprocessing"],
            "use_cases": ["Document parsing", "RAG data prep", "Multi-format ingestion"],
            "pricing": "open-source",
            "maturity": "stable"
        },
        {
            "name": "Docling",
            "category": "library",
            "description": "IBM's document parsing library for extracting structured data from documents",
            "tags": ["document-parsing", "ibm", "structured-data"],
            "use_cases": ["PDF extraction", "Document understanding", "Data pipeline"],
            "pricing": "open-source",
            "maturity": "stable"
        }
    ]
}

# Categories for classification
TOOL_CATEGORIES = [
    "agent_frameworks", "llm_models", "dev_tools", "rag_and_data",
    "vector_databases", "fine_tuning", "evaluation", "deployment",
    "monitoring", "security", "multimodal", "code_generation"
]


class AIToolDiscovery:
    """
    AI Tool Discovery Engine.
    Maintains a catalog of AI tools and generates periodic reports.
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.catalog: Dict[str, AITool] = {}
        self.reports: List[DiscoveryReport] = []
        self.watch_list: List[str] = []  # Tools/topics to watch
        self._load_ecosystem_catalog()

    def _load_ecosystem_catalog(self):
        """Load built-in AI ecosystem knowledge"""
        for category, tools in AI_ECOSYSTEM_CATALOG.items():
            for tool_data in tools:
                tool = AITool(
                    name=tool_data["name"],
                    category=tool_data.get("category", "tool"),
                    description=tool_data.get("description", ""),
                    language=tool_data.get("language", ""),
                    tags=tool_data.get("tags", []),
                    use_cases=tool_data.get("use_cases", []),
                    pricing=tool_data.get("pricing", ""),
                    maturity=tool_data.get("maturity", "")
                )
                self.catalog[tool.name] = tool

        logger.info(f"Loaded {len(self.catalog)} tools from ecosystem catalog")

    def add_tool(self, tool: AITool) -> AITool:
        """Add a new tool to the catalog"""
        tool.discovered_at = datetime.now().isoformat()
        self.catalog[tool.name] = tool
        logger.info(f"Added tool to catalog: {tool.name}")
        return tool

    def search_catalog(self, query: str = "", category: str = "",
                       tags: Optional[List[str]] = None,
                       pricing: str = "") -> List[AITool]:
        """Search the tool catalog with filters"""
        results = list(self.catalog.values())

        if query:
            query_lower = query.lower()
            results = [t for t in results if
                      query_lower in t.name.lower() or
                      query_lower in t.description.lower() or
                      any(query_lower in tag for tag in t.tags)]

        if category:
            results = [t for t in results if t.category == category]

        if tags:
            results = [t for t in results if any(tag in t.tags for tag in tags)]

        if pricing:
            results = [t for t in results if t.pricing == pricing]

        return results

    def evaluate_tool(self, tool_name: str, evaluation_notes: str,
                      relevance_score: float) -> Optional[AITool]:
        """Evaluate a tool's relevance to our stack"""
        tool = self.catalog.get(tool_name)
        if not tool:
            logger.warning(f"Tool not found: {tool_name}")
            return None

        tool.evaluated = True
        tool.evaluation_notes = evaluation_notes
        tool.relevance_score = max(0.0, min(1.0, relevance_score))
        logger.info(f"Evaluated tool {tool_name}: relevance={relevance_score}")
        return tool

    def compare_tools(self, tool_names: List[str]) -> Dict[str, Any]:
        """Compare multiple tools side by side"""
        tools = [self.catalog.get(name) for name in tool_names if name in self.catalog]

        if len(tools) < 2:
            return {"error": "Need at least 2 tools to compare"}

        comparison = {
            "tools": [],
            "comparison_matrix": {}
        }

        for tool in tools:
            comparison["tools"].append({
                "name": tool.name,
                "category": tool.category,
                "description": tool.description,
                "pricing": tool.pricing,
                "maturity": tool.maturity,
                "tags": tool.tags,
                "use_cases": tool.use_cases,
                "pros": tool.pros,
                "cons": tool.cons,
                "relevance_score": tool.relevance_score
            })

        # Build comparison matrix
        attributes = ["pricing", "maturity", "category"]
        for attr in attributes:
            comparison["comparison_matrix"][attr] = {
                t.name: getattr(t, attr) for t in tools
            }

        return comparison

    def generate_report(self, period_days: int = 7,
                        focus_areas: Optional[List[str]] = None) -> DiscoveryReport:
        """
        Generate a periodic AI discovery report.

        Args:
            period_days: How many days back to cover
            focus_areas: Specific areas to focus on (e.g., ["agent_frameworks", "llm_models"])
        """
        now = datetime.now()
        period_start = (now - timedelta(days=period_days)).isoformat()
        period_end = now.isoformat()
        report_id = f"report_{now.strftime('%Y%m%d_%H%M%S')}"

        # Gather new tools discovered in the period
        new_tools = [
            self._tool_to_dict(t) for t in self.catalog.values()
            if t.discovered_at >= period_start
        ]

        # Filter by focus areas if specified
        if focus_areas:
            new_tools = [t for t in new_tools
                        if t.get("category") in focus_areas or
                        any(tag in focus_areas for tag in t.get("tags", []))]

        # Separate models from tools
        new_models = [t for t in new_tools if t.get("category") == "model"]
        new_tools_only = [t for t in new_tools if t.get("category") != "model"]

        # Generate trending topics
        trending = self._analyze_trends(focus_areas)

        # Generate recommendations
        recommendations = self._generate_recommendations(focus_areas)

        # Build summary
        summary = self._build_report_summary(new_tools_only, new_models, trending, recommendations)

        report = DiscoveryReport(
            report_id=report_id,
            period_start=period_start,
            period_end=period_end,
            new_tools=new_tools_only,
            new_models=new_models,
            trending_topics=trending,
            recommendations=recommendations,
            summary=summary
        )

        self.reports.append(report)
        logger.info(f"Generated discovery report: {report_id}")
        return report

    def _analyze_trends(self, focus_areas: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Analyze current AI trends from catalog data"""
        trends = [
            {
                "topic": "Multi-Agent Systems",
                "description": "Growing adoption of multi-agent orchestration frameworks (CrewAI, LangGraph, AutoGen) for complex task automation",
                "relevance": "high",
                "tools": ["CrewAI", "LangGraph", "AutoGen", "Claude Agent SDK"]
            },
            {
                "topic": "Local LLM Deployment",
                "description": "Increasing demand for on-premise and edge deployment of open-source models for privacy and cost control",
                "relevance": "high",
                "tools": ["Ollama", "LM Studio", "Hugging Face TGI"]
            },
            {
                "topic": "Reasoning Models",
                "description": "New generation of reasoning-focused models (DeepSeek R1, o1/o3) showing breakthrough performance on complex tasks",
                "relevance": "high",
                "tools": ["DeepSeek V3 / R1"]
            },
            {
                "topic": "Vibe Coding & AI-First Development",
                "description": "Enterprise adoption of AI coding tools moving beyond autocomplete to full agentic development (Claude Code, Cursor)",
                "relevance": "high",
                "tools": ["Claude Code", "Cursor"]
            },
            {
                "topic": "RAG Pipeline Optimization",
                "description": "Advanced retrieval strategies combining hybrid search, reranking, and knowledge graphs for better RAG performance",
                "relevance": "medium",
                "tools": ["LlamaIndex", "Unstructured", "Docling"]
            },
            {
                "topic": "Small Language Models (SLMs)",
                "description": "Efficient small models (Phi-3/4, Gemma) enabling AI on resource-constrained devices",
                "relevance": "medium",
                "tools": ["Phi-3 / Phi-4"]
            }
        ]

        if focus_areas:
            # Boost relevance for focused areas
            for trend in trends:
                if any(area in str(trend.get("tools", [])).lower() for area in focus_areas):
                    trend["relevance"] = "high"

        return trends

    def _generate_recommendations(self, focus_areas: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Generate actionable recommendations for the team"""
        recommendations = [
            {
                "priority": "high",
                "title": "Integrate Anthropic Claude API",
                "description": "Add Claude API support alongside OpenAI for model diversity and comparison. Claude excels at coding and instruction following.",
                "effort": "medium",
                "impact": "high",
                "related_tools": ["Claude Agent SDK"]
            },
            {
                "priority": "high",
                "title": "Evaluate LangGraph for complex workflows",
                "description": "LangGraph's graph-based approach offers more control over agent workflows than basic LangChain agents. Consider migration for complex orchestration.",
                "effort": "high",
                "impact": "high",
                "related_tools": ["LangGraph"]
            },
            {
                "priority": "medium",
                "title": "Test DeepSeek R1 for reasoning tasks",
                "description": "DeepSeek R1 shows strong reasoning capabilities at lower cost. Test on our reasoning and coding benchmarks.",
                "effort": "low",
                "impact": "medium",
                "related_tools": ["DeepSeek V3 / R1"]
            },
            {
                "priority": "medium",
                "title": "Add Unstructured for document ETL",
                "description": "Replace manual document processing with Unstructured library for better RAG data preparation.",
                "effort": "medium",
                "impact": "medium",
                "related_tools": ["Unstructured", "Docling"]
            },
            {
                "priority": "low",
                "title": "Explore Phi-4 for edge deployment",
                "description": "Microsoft's Phi-4 offers strong performance in a small package. Good for on-device inference use cases.",
                "effort": "low",
                "impact": "low",
                "related_tools": ["Phi-3 / Phi-4"]
            }
        ]

        return recommendations

    def _build_report_summary(self, tools: List, models: List,
                               trends: List, recommendations: List) -> str:
        """Build a human-readable report summary"""
        summary_parts = [
            f"AI Discovery Report - {datetime.now().strftime('%Y-%m-%d')}",
            f"=" * 50,
            f"",
            f"Catalog Size: {len(self.catalog)} tools/models tracked",
            f"New Tools This Period: {len(tools)}",
            f"New Models This Period: {len(models)}",
            f"Trending Topics: {len(trends)}",
            f"Recommendations: {len(recommendations)}",
            f"",
            f"Top Trends:",
        ]

        for i, trend in enumerate(trends[:3], 1):
            summary_parts.append(f"  {i}. {trend['topic']} ({trend['relevance']} relevance)")

        summary_parts.extend(["", "Top Recommendations:"])
        for i, rec in enumerate(recommendations[:3], 1):
            summary_parts.append(f"  {i}. [{rec['priority'].upper()}] {rec['title']}")

        return "\n".join(summary_parts)

    def _tool_to_dict(self, tool: AITool) -> Dict[str, Any]:
        """Convert AITool to dictionary"""
        return {
            "name": tool.name,
            "category": tool.category,
            "description": tool.description,
            "url": tool.url,
            "github_url": tool.github_url,
            "tags": tool.tags,
            "use_cases": tool.use_cases,
            "pricing": tool.pricing,
            "maturity": tool.maturity,
            "relevance_score": tool.relevance_score,
            "evaluated": tool.evaluated,
            "discovered_at": tool.discovered_at
        }

    def add_to_watchlist(self, topic: str):
        """Add a topic to the watch list for future monitoring"""
        if topic not in self.watch_list:
            self.watch_list.append(topic)
            logger.info(f"Added to watchlist: {topic}")

    def get_watchlist(self) -> List[str]:
        """Get current watch list"""
        return self.watch_list

    def export_catalog(self, filepath: str = "ai_catalog.json"):
        """Export the full tool catalog to JSON"""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_tools": len(self.catalog),
            "tools": {name: self._tool_to_dict(tool) for name, tool in self.catalog.items()}
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Catalog exported to {filepath}")
        return filepath
