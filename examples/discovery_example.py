"""
AI Tool Discovery & Reporting Example
Demonstrates how to use the AI ecosystem catalog, evaluate tools,
analyze trends, and generate weekly reports.
"""

import json
from discovery import AIToolDiscovery, AITrendAnalyzer
from discovery.ai_discovery import AITool


def main():
    # =========================================================
    # 1. Initialize discovery engine
    # =========================================================
    discovery = AIToolDiscovery()
    print(f"Catalog loaded: {len(discovery.catalog)} tools tracked")

    # =========================================================
    # 2. Search the ecosystem catalog
    # =========================================================
    print("\n--- Search: Agent Frameworks ---")
    agents = discovery.search_catalog(tags=["multi-agent"])
    for tool in agents:
        print(f"  {tool.name}: {tool.description[:80]}...")

    print("\n--- Search: Open-Source Tools ---")
    opensource = discovery.search_catalog(pricing="open-source")
    for tool in opensource[:5]:
        print(f"  {tool.name} ({tool.category}): {tool.maturity}")

    # =========================================================
    # 3. Add a new tool to the catalog
    # =========================================================
    print("\n--- Add New Tool ---")
    new_tool = AITool(
        name="DSPy",
        category="framework",
        description="Framework for programming with foundation models using declarative signatures",
        language="Python",
        tags=["prompt-optimization", "llm-programming", "declarative"],
        use_cases=["Prompt optimization", "LLM pipeline programming", "Automatic prompt tuning"],
        pricing="open-source",
        maturity="stable"
    )
    discovery.add_tool(new_tool)
    print(f"Added: {new_tool.name}")

    # =========================================================
    # 4. Evaluate tools
    # =========================================================
    print("\n--- Evaluate Tools ---")
    discovery.evaluate_tool(
        "CrewAI",
        "Excellent fit for our multi-agent orchestration needs. Active community.",
        relevance_score=0.9
    )
    discovery.evaluate_tool(
        "LangGraph",
        "Better for complex stateful workflows. Consider for v2 migration.",
        relevance_score=0.85
    )
    discovery.evaluate_tool(
        "DSPy",
        "Interesting approach but different paradigm from our current stack.",
        relevance_score=0.6
    )

    # =========================================================
    # 5. Compare tools
    # =========================================================
    print("\n--- Compare: CrewAI vs LangGraph vs AutoGen ---")
    comparison = discovery.compare_tools(["CrewAI", "LangGraph", "AutoGen"])
    for tool in comparison.get("tools", []):
        print(f"\n  {tool['name']}:")
        print(f"    Category: {tool['category']}")
        print(f"    Pricing: {tool['pricing']}")
        print(f"    Maturity: {tool['maturity']}")
        print(f"    Use cases: {', '.join(tool['use_cases'][:3])}")

    # =========================================================
    # 6. Generate weekly report
    # =========================================================
    print("\n--- Weekly Report ---")
    report = discovery.generate_report(
        period_days=7,
        focus_areas=["agent_frameworks", "llm_models"]
    )
    print(report.summary)

    # =========================================================
    # 7. Trend analysis
    # =========================================================
    print("\n--- Trend Analysis ---")
    analyzer = AITrendAnalyzer()

    # Analyze a tool (rule-based without LLM)
    analysis = analyzer.analyze_tool(
        "Qwen 2.5 Coder",
        "Alibaba's code-specialized model with 32B parameters, strong at code generation and completion, supports 90+ languages"
    )
    print(f"\nAnalysis of {analysis['tool_name']}:")
    llm_result = analysis.get("llm_analysis", {})
    print(f"  Category: {llm_result.get('category', 'N/A')}")
    print(f"  Relevance: {llm_result.get('relevance_to_stack', 'N/A')}")
    print(f"  Recommendation: {llm_result.get('recommendation', 'N/A')}")

    # Track a topic over time
    analyzer.track_topic("local_llm_adoption", {
        "event": "Qwen 2.5 Coder released",
        "impact": "New option for local code generation"
    })

    # =========================================================
    # 8. Export catalog
    # =========================================================
    discovery.export_catalog("ai_catalog.json")
    print("\nCatalog exported to ai_catalog.json")


if __name__ == "__main__":
    main()
