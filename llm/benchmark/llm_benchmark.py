"""
LLM Benchmark & Comparison Engine for EACP
Runs standardized benchmarks across multiple LLM providers and generates comparison reports
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json
import time
import statistics

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Single benchmark result for one provider on one prompt"""
    provider: str
    model: str
    prompt_category: str
    prompt: str
    response: str
    latency_ms: float
    tokens_used: int
    prompt_tokens: int
    completion_tokens: int
    estimated_cost: float
    quality_scores: Dict[str, float] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: bool = False


# Standard benchmark prompt suite covering different capabilities
BENCHMARK_PROMPTS = {
    "reasoning": [
        "A farmer has 17 sheep. All but 9 die. How many sheep are left? Explain your reasoning step by step.",
        "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets? Show your work.",
    ],
    "coding": [
        "Write a Python function that finds the longest common subsequence of two strings. Include type hints and a brief docstring.",
        "Write a SQL query to find the top 3 customers by total order value from tables 'customers' and 'orders', joined on customer_id.",
    ],
    "summarization": [
        "Summarize the concept of transformer architecture in neural networks in 3 bullet points for a non-technical audience.",
        "Explain the difference between supervised and unsupervised learning in exactly 2 sentences.",
    ],
    "creativity": [
        "Write a haiku about artificial intelligence.",
        "Come up with 3 creative product names for an AI-powered code review tool.",
    ],
    "instruction_following": [
        "List exactly 5 programming languages created after 2010. Format each as: '- Name (Year)'. Do not include any other text.",
        "Translate 'Hello, how are you?' into French, German, and Japanese. Format: Language: Translation",
    ],
    "knowledge": [
        "What are the SOLID principles in software engineering? List each with a one-line explanation.",
        "Explain the CAP theorem in distributed systems and give a real-world example for each trade-off.",
    ]
}


class LLMBenchmark:
    """
    Benchmarks multiple LLM providers on standardized prompt suites.
    Measures latency, token usage, cost, and response quality.
    """

    def __init__(self, multi_provider_client):
        self.client = multi_provider_client
        self.results: List[BenchmarkResult] = []
        self.benchmark_history: List[Dict[str, Any]] = []

    def run_benchmark(self, prompt_categories: Optional[List[str]] = None,
                      providers: Optional[List[str]] = None,
                      custom_prompts: Optional[Dict[str, List[str]]] = None,
                      max_tokens: int = 512,
                      temperature: float = 0.7,
                      runs_per_prompt: int = 1) -> Dict[str, Any]:
        """
        Run a full benchmark across providers and prompt categories.

        Args:
            prompt_categories: Which categories to test (default: all)
            providers: Which providers to test (default: all available)
            custom_prompts: Additional custom prompts to include
            max_tokens: Max tokens per response
            temperature: Temperature setting
            runs_per_prompt: How many times to run each prompt (for latency averaging)

        Returns:
            Comprehensive benchmark report
        """
        benchmark_id = f"bench_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Starting benchmark: {benchmark_id}")

        # Determine prompts to use
        prompts = {}
        if prompt_categories:
            prompts = {k: v for k, v in BENCHMARK_PROMPTS.items() if k in prompt_categories}
        else:
            prompts = dict(BENCHMARK_PROMPTS)

        if custom_prompts:
            prompts.update(custom_prompts)

        # Determine providers
        available = providers or self.client.get_available_providers()
        if not available:
            logger.warning("No providers available for benchmarking")
            return {"error": "No providers available", "benchmark_id": benchmark_id}

        logger.info(f"Benchmarking providers: {available}")
        logger.info(f"Categories: {list(prompts.keys())}")

        # Run benchmarks
        benchmark_results = []
        total_prompts = sum(len(p) for p in prompts.values()) * len(available) * runs_per_prompt
        completed = 0

        for category, prompt_list in prompts.items():
            for prompt in prompt_list:
                for provider_name in available:
                    for run in range(runs_per_prompt):
                        result = self._run_single_benchmark(
                            provider_name, category, prompt,
                            max_tokens=max_tokens, temperature=temperature
                        )
                        benchmark_results.append(result)
                        self.results.append(result)
                        completed += 1

                        if completed % 5 == 0:
                            logger.info(f"Progress: {completed}/{total_prompts}")

        # Generate report
        report = self._generate_report(benchmark_id, benchmark_results, available)
        self.benchmark_history.append(report)

        logger.info(f"Benchmark complete: {benchmark_id}")
        return report

    def _run_single_benchmark(self, provider_name: str, category: str,
                               prompt: str, **kwargs) -> BenchmarkResult:
        """Run a single benchmark for one provider on one prompt"""
        try:
            response = self.client.generate(provider_name, prompt, **kwargs)

            provider = self.client.providers.get(provider_name)
            model = provider.config.get("model", "unknown") if provider else "unknown"

            # Estimate cost
            cost = self.client.estimate_cost(
                provider_name, model,
                response.get("prompt_tokens", 0),
                response.get("completion_tokens", 0)
            )

            # Calculate quality scores
            quality = self._evaluate_response_quality(prompt, response.get("text", ""), category)

            return BenchmarkResult(
                provider=provider_name,
                model=response.get("model", model),
                prompt_category=category,
                prompt=prompt,
                response=response.get("text", ""),
                latency_ms=response.get("latency_ms", 0),
                tokens_used=response.get("tokens_used", 0),
                prompt_tokens=response.get("prompt_tokens", 0),
                completion_tokens=response.get("completion_tokens", 0),
                estimated_cost=cost,
                quality_scores=quality,
                error=response.get("error", False)
            )
        except Exception as e:
            logger.error(f"Benchmark error for {provider_name}: {e}")
            return BenchmarkResult(
                provider=provider_name, model="unknown",
                prompt_category=category, prompt=prompt,
                response=f"Error: {e}", latency_ms=0,
                tokens_used=0, prompt_tokens=0, completion_tokens=0,
                estimated_cost=0, error=True
            )

    def _evaluate_response_quality(self, prompt: str, response: str,
                                    category: str) -> Dict[str, float]:
        """
        Evaluate response quality with multiple metrics.
        Returns scores from 0.0 to 1.0 for each metric.
        """
        scores = {}

        if not response or response.startswith("Error:") or response.startswith("["):
            return {"completeness": 0.0, "relevance": 0.0, "conciseness": 0.0}

        # 1. Completeness - Did it actually produce a substantial response?
        response_len = len(response.split())
        if response_len > 50:
            scores["completeness"] = 1.0
        elif response_len > 20:
            scores["completeness"] = 0.7
        elif response_len > 5:
            scores["completeness"] = 0.4
        else:
            scores["completeness"] = 0.1

        # 2. Relevance - Does response contain key terms from prompt?
        prompt_keywords = set(prompt.lower().split()) - {
            "a", "the", "is", "are", "in", "of", "to", "and", "or", "for",
            "what", "how", "why", "your", "write", "explain", "list"
        }
        response_lower = response.lower()
        keyword_hits = sum(1 for kw in prompt_keywords if kw in response_lower)
        scores["relevance"] = min(1.0, keyword_hits / max(len(prompt_keywords), 1))

        # 3. Conciseness - Response efficiency (tokens per meaningful word)
        if response_len > 0:
            # Penalize very short or very long responses
            ideal_length = {"reasoning": 100, "coding": 80, "summarization": 50,
                          "creativity": 40, "instruction_following": 60, "knowledge": 100}
            ideal = ideal_length.get(category, 80)
            ratio = response_len / ideal
            if 0.5 <= ratio <= 2.0:
                scores["conciseness"] = 1.0
            elif 0.25 <= ratio <= 3.0:
                scores["conciseness"] = 0.6
            else:
                scores["conciseness"] = 0.3
        else:
            scores["conciseness"] = 0.0

        # 4. Format compliance - Did it follow formatting instructions?
        format_score = 1.0
        if "list" in prompt.lower() or "format" in prompt.lower():
            if "-" in response or "1." in response or "•" in response:
                format_score = 1.0
            else:
                format_score = 0.5
        if "exactly" in prompt.lower():
            # Check if it tried to be precise
            format_score *= 0.8 if len(response) > 10 else 0.3
        scores["format_compliance"] = format_score

        # 5. Composite quality score
        weights = {"completeness": 0.3, "relevance": 0.3, "conciseness": 0.2, "format_compliance": 0.2}
        scores["composite"] = sum(scores[k] * weights[k] for k in weights)

        return scores

    def _generate_report(self, benchmark_id: str, results: List[BenchmarkResult],
                          providers: List[str]) -> Dict[str, Any]:
        """Generate comprehensive benchmark comparison report"""
        report = {
            "benchmark_id": benchmark_id,
            "timestamp": datetime.now().isoformat(),
            "providers_tested": providers,
            "total_prompts": len(results),
            "provider_summary": {},
            "category_breakdown": {},
            "rankings": {},
            "cost_analysis": {},
            "detailed_results": []
        }

        # Per-provider aggregation
        for provider in providers:
            provider_results = [r for r in results if r.provider == provider and not r.error]
            if not provider_results:
                report["provider_summary"][provider] = {"error": "No successful results"}
                continue

            latencies = [r.latency_ms for r in provider_results]
            tokens = [r.tokens_used for r in provider_results]
            costs = [r.estimated_cost for r in provider_results]
            composites = [r.quality_scores.get("composite", 0) for r in provider_results]

            report["provider_summary"][provider] = {
                "model": provider_results[0].model,
                "total_requests": len(provider_results),
                "avg_latency_ms": round(statistics.mean(latencies), 2),
                "median_latency_ms": round(statistics.median(latencies), 2),
                "p95_latency_ms": round(sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[0], 2),
                "min_latency_ms": round(min(latencies), 2),
                "max_latency_ms": round(max(latencies), 2),
                "avg_tokens": round(statistics.mean(tokens), 1),
                "total_cost": round(sum(costs), 6),
                "avg_cost_per_query": round(statistics.mean(costs), 6),
                "avg_quality_score": round(statistics.mean(composites), 3),
                "error_rate": round(
                    len([r for r in results if r.provider == provider and r.error]) /
                    len([r for r in results if r.provider == provider]), 3
                )
            }

        # Category breakdown
        categories = set(r.prompt_category for r in results)
        for category in categories:
            report["category_breakdown"][category] = {}
            for provider in providers:
                cat_results = [r for r in results
                              if r.provider == provider and r.prompt_category == category and not r.error]
                if cat_results:
                    report["category_breakdown"][category][provider] = {
                        "avg_latency_ms": round(statistics.mean([r.latency_ms for r in cat_results]), 2),
                        "avg_quality": round(statistics.mean([r.quality_scores.get("composite", 0) for r in cat_results]), 3),
                        "avg_cost": round(statistics.mean([r.estimated_cost for r in cat_results]), 6)
                    }

        # Rankings
        valid_summaries = {k: v for k, v in report["provider_summary"].items() if "error" not in v}

        if valid_summaries:
            report["rankings"] = {
                "fastest": sorted(valid_summaries.keys(), key=lambda p: valid_summaries[p]["avg_latency_ms"]),
                "cheapest": sorted(valid_summaries.keys(), key=lambda p: valid_summaries[p]["total_cost"]),
                "highest_quality": sorted(valid_summaries.keys(), key=lambda p: valid_summaries[p]["avg_quality_score"], reverse=True),
                "most_reliable": sorted(valid_summaries.keys(), key=lambda p: valid_summaries[p]["error_rate"]),
                "best_value": sorted(valid_summaries.keys(),
                    key=lambda p: valid_summaries[p]["avg_quality_score"] / max(valid_summaries[p]["avg_cost_per_query"], 0.000001),
                    reverse=True
                )
            }

        # Cost analysis
        report["cost_analysis"] = {
            provider: {
                "cost_per_1k_queries": round(summary.get("avg_cost_per_query", 0) * 1000, 4),
                "monthly_estimate_10k_queries": round(summary.get("avg_cost_per_query", 0) * 10000, 2)
            }
            for provider, summary in valid_summaries.items()
        }

        # Detailed results (limited for report size)
        report["detailed_results"] = [
            {
                "provider": r.provider, "model": r.model,
                "category": r.prompt_category,
                "prompt_preview": r.prompt[:80] + "..." if len(r.prompt) > 80 else r.prompt,
                "response_preview": r.response[:150] + "..." if len(r.response) > 150 else r.response,
                "latency_ms": round(r.latency_ms, 2),
                "tokens_used": r.tokens_used,
                "cost": round(r.estimated_cost, 6),
                "quality": round(r.quality_scores.get("composite", 0), 3)
            }
            for r in results[:50]  # Limit to first 50 for report size
        ]

        return report

    def compare_on_prompt(self, prompt: str, providers: Optional[List[str]] = None,
                          **kwargs) -> Dict[str, Any]:
        """Quick comparison: run a single prompt across all providers"""
        available = providers or self.client.get_available_providers()
        results = {}

        for provider_name in available:
            response = self.client.generate(provider_name, prompt, **kwargs)
            cost = self.client.estimate_cost(
                provider_name,
                response.get("model", "default"),
                response.get("prompt_tokens", 0),
                response.get("completion_tokens", 0)
            )
            results[provider_name] = {
                "response": response.get("text", ""),
                "latency_ms": round(response.get("latency_ms", 0), 2),
                "tokens_used": response.get("tokens_used", 0),
                "estimated_cost": round(cost, 6),
                "error": response.get("error", False)
            }

        return {
            "prompt": prompt,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }

    def export_results(self, filepath: str = "benchmark_results.json"):
        """Export all benchmark results to JSON file"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_benchmarks": len(self.benchmark_history),
            "total_results": len(self.results),
            "benchmarks": self.benchmark_history,
            "all_results": [
                {
                    "provider": r.provider, "model": r.model,
                    "category": r.prompt_category, "prompt": r.prompt,
                    "response": r.response, "latency_ms": r.latency_ms,
                    "tokens_used": r.tokens_used, "cost": r.estimated_cost,
                    "quality_scores": r.quality_scores, "error": r.error,
                    "timestamp": r.timestamp
                }
                for r in self.results
            ]
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Benchmark results exported to {filepath}")
        return filepath
