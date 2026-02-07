"""
AI Trend Analyzer for EACP
Analyzes AI ecosystem trends and generates insights using LLM
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class AITrendAnalyzer:
    """
    Analyzes AI ecosystem trends using LLM-powered analysis.
    Can process information from various sources and generate structured insights.
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.analysis_history: List[Dict[str, Any]] = []
        self.tracked_topics: Dict[str, List[Dict[str, Any]]] = {}

    def analyze_tool(self, tool_name: str, tool_description: str,
                     context: str = "") -> Dict[str, Any]:
        """
        Use LLM to analyze a new AI tool and generate structured insights.

        Args:
            tool_name: Name of the tool
            tool_description: Description or documentation excerpt
            context: Additional context about the tool

        Returns:
            Structured analysis with pros, cons, use cases, and relevance
        """
        prompt = f"""Analyze the following AI tool for an enterprise AI platform team:

Tool: {tool_name}
Description: {tool_description}
Additional Context: {context}

Our stack includes: LangChain, Ollama, ChromaDB, JIRA/Azure DevOps integrations,
LoRA fine-tuning, multi-agent orchestration, RAG pipelines.

Provide analysis in this exact JSON format:
{{
    "summary": "One-line summary",
    "category": "framework|model|tool|library|platform",
    "strengths": ["strength1", "strength2", "strength3"],
    "weaknesses": ["weakness1", "weakness2"],
    "use_cases": ["use_case1", "use_case2", "use_case3"],
    "integration_difficulty": "low|medium|high",
    "relevance_to_stack": 0.0 to 1.0,
    "recommendation": "adopt|trial|assess|hold",
    "reasoning": "Why this recommendation"
}}"""

        analysis = {
            "tool_name": tool_name,
            "timestamp": datetime.now().isoformat(),
            "raw_input": tool_description,
            "llm_analysis": None,
            "status": "pending"
        }

        if self.llm_client:
            try:
                response = self.llm_client.generate(prompt, max_tokens=1024, temperature=0.3)
                # Try to parse JSON from response
                try:
                    # Find JSON in the response
                    json_start = response.find("{")
                    json_end = response.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        parsed = json.loads(response[json_start:json_end])
                        analysis["llm_analysis"] = parsed
                        analysis["status"] = "completed"
                    else:
                        analysis["llm_analysis"] = {"raw_response": response}
                        analysis["status"] = "completed_unstructured"
                except json.JSONDecodeError:
                    analysis["llm_analysis"] = {"raw_response": response}
                    analysis["status"] = "completed_unstructured"
            except Exception as e:
                logger.error(f"LLM analysis failed: {e}")
                analysis["status"] = "failed"
                analysis["error"] = str(e)
        else:
            # Provide rule-based analysis without LLM
            analysis["llm_analysis"] = self._rule_based_analysis(tool_name, tool_description)
            analysis["status"] = "completed_rule_based"

        self.analysis_history.append(analysis)
        return analysis

    def _rule_based_analysis(self, tool_name: str, description: str) -> Dict[str, Any]:
        """Fallback rule-based analysis when LLM is not available"""
        desc_lower = description.lower()

        # Determine category
        category = "tool"
        if any(kw in desc_lower for kw in ["framework", "library", "sdk"]):
            category = "framework"
        elif any(kw in desc_lower for kw in ["model", "llm", "language model"]):
            category = "model"
        elif any(kw in desc_lower for kw in ["platform", "saas", "cloud"]):
            category = "platform"

        # Determine relevance
        relevance_keywords = ["agent", "rag", "llm", "fine-tun", "vector", "embedding",
                            "orchestrat", "langchain", "multi-agent", "local"]
        relevance = sum(1 for kw in relevance_keywords if kw in desc_lower) / len(relevance_keywords)

        # Determine recommendation
        if relevance > 0.5:
            recommendation = "trial"
        elif relevance > 0.3:
            recommendation = "assess"
        else:
            recommendation = "hold"

        return {
            "summary": f"{tool_name}: {description[:100]}",
            "category": category,
            "strengths": ["Needs further evaluation"],
            "weaknesses": ["Needs further evaluation"],
            "use_cases": ["Needs further evaluation"],
            "integration_difficulty": "medium",
            "relevance_to_stack": round(relevance, 2),
            "recommendation": recommendation,
            "reasoning": f"Rule-based analysis. Relevance score: {relevance:.2f}. Manual evaluation recommended."
        }

    def track_topic(self, topic: str, data_point: Dict[str, Any]):
        """Track a topic over time for trend analysis"""
        if topic not in self.tracked_topics:
            self.tracked_topics[topic] = []

        data_point["tracked_at"] = datetime.now().isoformat()
        self.tracked_topics[topic].append(data_point)
        logger.info(f"Tracked data point for topic: {topic}")

    def get_topic_timeline(self, topic: str) -> List[Dict[str, Any]]:
        """Get timeline of tracked data for a topic"""
        return self.tracked_topics.get(topic, [])

    def generate_weekly_digest(self, discoveries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a weekly digest of AI discoveries.

        Args:
            discoveries: List of newly discovered tools/updates

        Returns:
            Formatted weekly digest
        """
        digest = {
            "title": f"AI Weekly Digest - {datetime.now().strftime('%Y-%m-%d')}",
            "generated_at": datetime.now().isoformat(),
            "sections": []
        }

        # Group discoveries by category
        categories = {}
        for disc in discoveries:
            cat = disc.get("category", "other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(disc)

        for cat, items in categories.items():
            section = {
                "category": cat,
                "count": len(items),
                "highlights": [
                    {
                        "name": item.get("name", "Unknown"),
                        "description": item.get("description", ""),
                        "relevance": item.get("relevance_score", 0)
                    }
                    for item in sorted(items,
                                      key=lambda x: x.get("relevance_score", 0),
                                      reverse=True)[:5]
                ]
            }
            digest["sections"].append(section)

        # Add action items
        digest["action_items"] = [
            f"Evaluate {disc['name']}" for disc in discoveries
            if disc.get("relevance_score", 0) > 0.7
        ]

        return digest

    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get all past analyses"""
        return self.analysis_history

    def export_analyses(self, filepath: str = "trend_analyses.json"):
        """Export all analyses to JSON"""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_analyses": len(self.analysis_history),
            "tracked_topics": list(self.tracked_topics.keys()),
            "analyses": self.analysis_history
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Analyses exported to {filepath}")
        return filepath
