"""
Local LLM Client for EACP
Supports LLaMA, Ollama, and vLLM models
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LocalLLMClient:
    """Client for local LLM inference"""
    
    def __init__(self, model_name: str = "llama", model_path: Optional[str] = None, 
                 backend: str = "ollama"):
        self.model_name = model_name
        self.model_path = model_path
        self.backend = backend
        self.model = None
        self.tokenizer = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the local LLM model"""
        try:
            if self.backend == "ollama":
                self._init_ollama()
            elif self.backend == "vllm":
                self._init_vllm()
            elif self.backend == "llama":
                self._init_llama()
            else:
                logger.warning(f"Unknown backend: {self.backend}, using mock")
                self._init_mock()
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            logger.warning("Falling back to mock model")
            self._init_mock()
    
    def _init_ollama(self):
        """Initialize Ollama backend"""
        try:
            import ollama
            self.model = ollama
            logger.info(f"Ollama initialized with model: {self.model_name}")
        except ImportError:
            logger.warning("Ollama not installed, using mock")
            self._init_mock()
    
    def _init_vllm(self):
        """Initialize vLLM backend"""
        try:
            from vllm import LLM
            self.model = LLM(model=self.model_path or self.model_name)
            logger.info(f"vLLM initialized with model: {self.model_name}")
        except ImportError:
            logger.warning("vLLM not installed, using mock")
            self._init_mock()
    
    def _init_llama(self):
        """Initialize LLaMA backend"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            model_path = self.model_path or self.model_name
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
            logger.info(f"LLaMA initialized with model: {model_path}")
        except ImportError:
            logger.warning("Transformers not installed, using mock")
            self._init_mock()
    
    def _init_mock(self):
        """Initialize mock model for development"""
        self.model = "mock"
        logger.info("Using mock LLM model")
    
    def generate(self, prompt: str, max_tokens: int = 512, 
                temperature: float = 0.7, **kwargs) -> str:
        """Generate text from prompt"""
        try:
            if self.backend == "ollama" and self.model != "mock":
                response = self.model.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                )
                return response.get("response", "")
            
            elif self.backend == "vllm" and self.model != "mock":
                outputs = self.model.generate(prompt, max_tokens=max_tokens, 
                                             temperature=temperature, **kwargs)
                return outputs[0].outputs[0].text
            
            elif self.backend == "llama" and self.model != "mock":
                inputs = self.tokenizer(prompt, return_tensors="pt")
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            else:
                # Mock response
                return f"[Mock LLM Response for: {prompt[:50]}...]"
                
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def generate_stream(self, prompt: str, max_tokens: int = 512, 
                       temperature: float = 0.7, **kwargs):
        """Generate text stream from prompt"""
        # Placeholder for streaming generation
        response = self.generate(prompt, max_tokens, temperature, **kwargs)
        for chunk in response.split():
            yield chunk + " "
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "backend": self.backend,
            "model_path": self.model_path,
            "is_mock": self.model == "mock"
        }
