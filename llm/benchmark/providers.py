"""
Multi-Provider LLM Client for EACP
Unified interface for OpenAI, Anthropic, Google Gemini, and local models
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)


class LLMProvider:
    """Base class for LLM providers"""

    def __init__(self, provider_name: str, config: Dict[str, Any]):
        self.provider_name = provider_name
        self.config = config
        self.client = None
        self._initialize()

    def _initialize(self):
        raise NotImplementedError

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "model": self.config.get("model", "unknown"),
            "available": self.client is not None
        }


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider (GPT-4, GPT-4o, GPT-3.5-turbo)"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("openai", config)

    def _initialize(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.config.get("api_key"))
            self.model = self.config.get("model", "gpt-4")
            logger.info(f"OpenAI provider initialized: {self.model}")
        except ImportError:
            logger.warning("openai package not installed")
            self.client = None
        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}")
            self.client = None

    def generate(self, prompt: str, max_tokens: int = 512,
                 temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        if not self.client:
            return {"text": "[OpenAI not available]", "tokens_used": 0, "error": True}

        try:
            start = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            latency = (time.time() - start) * 1000

            return {
                "text": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "latency_ms": latency,
                "model": self.model,
                "provider": "openai",
                "error": False
            }
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return {"text": f"Error: {e}", "tokens_used": 0, "error": True}


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider (Claude 4.5 Sonnet, Claude Opus 4.6)"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("anthropic", config)

    def _initialize(self):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.config.get("api_key"))
            self.model = self.config.get("model", "claude-sonnet-4-5-20250929")
            logger.info(f"Anthropic provider initialized: {self.model}")
        except ImportError:
            logger.warning("anthropic package not installed")
            self.client = None
        except Exception as e:
            logger.error(f"Anthropic initialization failed: {e}")
            self.client = None

    def generate(self, prompt: str, max_tokens: int = 512,
                 temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        if not self.client:
            return {"text": "[Anthropic not available]", "tokens_used": 0, "error": True}

        try:
            start = time.time()
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            latency = (time.time() - start) * 1000

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            return {
                "text": response.content[0].text,
                "tokens_used": input_tokens + output_tokens,
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "latency_ms": latency,
                "model": self.model,
                "provider": "anthropic",
                "error": False
            }
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            return {"text": f"Error: {e}", "tokens_used": 0, "error": True}


class GeminiProvider(LLMProvider):
    """Google Gemini provider (Gemini Pro, Gemini Ultra)"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("gemini", config)

    def _initialize(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.config.get("api_key"))
            self.model_name = self.config.get("model", "gemini-pro")
            self.client = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini provider initialized: {self.model_name}")
        except ImportError:
            logger.warning("google-generativeai package not installed")
            self.client = None
        except Exception as e:
            logger.error(f"Gemini initialization failed: {e}")
            self.client = None

    def generate(self, prompt: str, max_tokens: int = 512,
                 temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        if not self.client:
            return {"text": "[Gemini not available]", "tokens_used": 0, "error": True}

        try:
            start = time.time()
            response = self.client.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": temperature
                }
            )
            latency = (time.time() - start) * 1000

            # Gemini token counting
            tokens_used = 0
            if hasattr(response, 'usage_metadata'):
                tokens_used = (response.usage_metadata.prompt_token_count +
                             response.usage_metadata.candidates_token_count)

            return {
                "text": response.text,
                "tokens_used": tokens_used,
                "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                "latency_ms": latency,
                "model": self.model_name,
                "provider": "gemini",
                "error": False
            }
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return {"text": f"Error: {e}", "tokens_used": 0, "error": True}


class OllamaProvider(LLMProvider):
    """Local Ollama provider for open-source models"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("ollama", config)

    def _initialize(self):
        try:
            import ollama
            self.client = ollama
            self.model = self.config.get("model", "llama3")
            logger.info(f"Ollama provider initialized: {self.model}")
        except ImportError:
            logger.warning("ollama package not installed")
            self.client = None
        except Exception as e:
            logger.error(f"Ollama initialization failed: {e}")
            self.client = None

    def generate(self, prompt: str, max_tokens: int = 512,
                 temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        if not self.client:
            return {"text": "[Ollama not available]", "tokens_used": 0, "error": True}

        try:
            start = time.time()
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": temperature, "num_predict": max_tokens}
            )
            latency = (time.time() - start) * 1000

            return {
                "text": response.get("response", ""),
                "tokens_used": response.get("eval_count", 0) + response.get("prompt_eval_count", 0),
                "prompt_tokens": response.get("prompt_eval_count", 0),
                "completion_tokens": response.get("eval_count", 0),
                "latency_ms": latency,
                "model": self.model,
                "provider": "ollama",
                "error": False
            }
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return {"text": f"Error: {e}", "tokens_used": 0, "error": True}


# Pricing per 1M tokens (input/output) - approximate as of 2025
PROVIDER_PRICING = {
    "openai": {
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-4o": {"input": 2.50, "output": 10.0},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    },
    "anthropic": {
        "claude-opus-4-6": {"input": 15.0, "output": 75.0},
        "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
        "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.0},
    },
    "gemini": {
        "gemini-pro": {"input": 0.50, "output": 1.50},
        "gemini-ultra": {"input": 7.0, "output": 21.0},
    },
    "ollama": {
        "default": {"input": 0.0, "output": 0.0},  # Local = free
    }
}


class MultiProviderClient:
    """Unified client for managing multiple LLM providers"""

    def __init__(self, config: Dict[str, Any]):
        self.providers: Dict[str, LLMProvider] = {}
        self.config = config
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all configured providers"""
        provider_map = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "gemini": GeminiProvider,
            "ollama": OllamaProvider
        }

        for provider_name, provider_config in self.config.get("providers", {}).items():
            if provider_name in provider_map and provider_config.get("enabled", True):
                try:
                    self.providers[provider_name] = provider_map[provider_name](provider_config)
                    logger.info(f"Provider {provider_name} registered")
                except Exception as e:
                    logger.error(f"Failed to register provider {provider_name}: {e}")

    def generate(self, provider_name: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using a specific provider"""
        provider = self.providers.get(provider_name)
        if not provider:
            return {"text": f"Provider {provider_name} not available", "error": True}
        return provider.generate(prompt, **kwargs)

    def generate_all(self, prompt: str, **kwargs) -> Dict[str, Dict[str, Any]]:
        """Generate text using all available providers"""
        results = {}
        for name, provider in self.providers.items():
            results[name] = provider.generate(prompt, **kwargs)
        return results

    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [name for name, p in self.providers.items() if p.client is not None]

    def estimate_cost(self, provider: str, model: str,
                      prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost for a given provider/model/token count"""
        pricing = PROVIDER_PRICING.get(provider, {}).get(model,
                  PROVIDER_PRICING.get(provider, {}).get("default", {"input": 0, "output": 0}))

        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def get_all_info(self) -> Dict[str, Any]:
        """Get info for all providers"""
        return {name: p.get_info() for name, p in self.providers.items()}
