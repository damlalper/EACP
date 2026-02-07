"""
LLM Benchmark & Comparison Example
Demonstrates how to compare multiple LLM providers (OpenAI, Claude, Gemini, Ollama)
on standardized prompts and generate a comparison report.
"""

import json
from llm.benchmark import LLMBenchmark, MultiProviderClient


def main():
    # =========================================================
    # 1. Configure providers
    # =========================================================
    provider_config = {
        "providers": {
            "openai": {
                "enabled": True,
                "api_key": "YOUR_OPENAI_API_KEY",  # Replace with your key
                "model": "gpt-4o"
            },
            "anthropic": {
                "enabled": True,
                "api_key": "YOUR_ANTHROPIC_API_KEY",  # Replace with your key
                "model": "claude-sonnet-4-5-20250929"
            },
            "gemini": {
                "enabled": True,
                "api_key": "YOUR_GOOGLE_AI_API_KEY",  # Replace with your key
                "model": "gemini-pro"
            },
            "ollama": {
                "enabled": True,
                "model": "llama3"  # Requires Ollama running locally
            }
        }
    }

    # Initialize multi-provider client
    client = MultiProviderClient(provider_config)
    print(f"Available providers: {client.get_available_providers()}")
    print(f"Provider info: {json.dumps(client.get_all_info(), indent=2)}")

    # =========================================================
    # 2. Quick single-prompt comparison
    # =========================================================
    print("\n--- Quick Comparison ---")
    result = LLMBenchmark(client).compare_on_prompt(
        "What are the 3 most important principles of clean code? Be concise."
    )

    for provider, data in result["results"].items():
        print(f"\n[{provider}]")
        print(f"  Latency: {data['latency_ms']:.0f}ms")
        print(f"  Tokens: {data['tokens_used']}")
        print(f"  Cost: ${data['estimated_cost']:.6f}")
        print(f"  Response: {data['response'][:100]}...")

    # =========================================================
    # 3. Full benchmark suite
    # =========================================================
    print("\n--- Full Benchmark ---")
    benchmark = LLMBenchmark(client)

    report = benchmark.run_benchmark(
        prompt_categories=["reasoning", "coding", "summarization"],
        max_tokens=512,
        temperature=0.7
    )

    # Print provider summary
    print("\n=== Provider Summary ===")
    for provider, summary in report.get("provider_summary", {}).items():
        if "error" not in summary:
            print(f"\n{provider} ({summary['model']}):")
            print(f"  Avg Latency:  {summary['avg_latency_ms']:.0f}ms")
            print(f"  Avg Quality:  {summary['avg_quality_score']:.3f}")
            print(f"  Total Cost:   ${summary['total_cost']:.6f}")
            print(f"  Error Rate:   {summary['error_rate']:.1%}")

    # Print rankings
    print("\n=== Rankings ===")
    rankings = report.get("rankings", {})
    if rankings:
        print(f"  Fastest:        {' > '.join(rankings.get('fastest', []))}")
        print(f"  Cheapest:       {' > '.join(rankings.get('cheapest', []))}")
        print(f"  Highest Quality:{' > '.join(rankings.get('highest_quality', []))}")
        print(f"  Best Value:     {' > '.join(rankings.get('best_value', []))}")

    # Print cost analysis
    print("\n=== Cost Analysis ===")
    for provider, costs in report.get("cost_analysis", {}).items():
        print(f"  {provider}: ${costs['cost_per_1k_queries']:.4f}/1K queries, "
              f"${costs['monthly_estimate_10k_queries']:.2f}/month (10K queries)")

    # =========================================================
    # 4. Export results
    # =========================================================
    benchmark.export_results("benchmark_results.json")
    print("\nResults exported to benchmark_results.json")


if __name__ == "__main__":
    main()
