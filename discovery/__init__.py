"""
EACP AI Tool Discovery & Reporting Module
Researches new AI tools, frameworks, and models, then generates team reports
"""

from discovery.ai_discovery import AIToolDiscovery, DiscoveryReport
from discovery.trend_analyzer import AITrendAnalyzer

__all__ = [
    "AIToolDiscovery",
    "DiscoveryReport",
    "AITrendAnalyzer"
]
