"""
Local LLM Deployment Example
Shows how to use local LLMs with EACP (Ollama, vLLM, llama.cpp)
"""
from llm.local_model.llm_client import LocalLLMClient
import json


def example_ollama():
    """Example: Using Ollama for local inference."""
    print("=" * 60)
    print("Example 1: Ollama Backend")
    print("=" * 60)
    print("""
    Prerequisites:
    1. Install Ollama: https://ollama.ai
    2. Run: ollama serve
    3. Pull a model: ollama pull llama2
    
    Then run this code:
    """)
    
    try:
        client = LocalLLMClient(
            model_name="llama2",
            backend="ollama"
        )
        
        prompt = "Explain quantum computing in simple terms."
        response = client.generate(prompt, max_tokens=256, temperature=0.7)
        
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("(Make sure Ollama is running: ollama serve)")


def example_vllm():
    """Example: Using vLLM for fast inference."""
    print("\n" + "=" * 60)
    print("Example 2: vLLM Backend")
    print("=" * 60)
    print("""
    Prerequisites:
    1. Install vLLM: pip install vllm
    2. Start vLLM server:
       python -m vllm.entrypoints.openai_api_server \\
         --model meta-llama/Llama-2-7b-hf \\
         --gpu-memory-utilization 0.8
    """)
    
    try:
        client = LocalLLMClient(
            model_name="meta-llama/Llama-2-7b-hf",
            backend="vllm"
        )
        
        prompt = "Write a haiku about AI:"
        response = client.generate(prompt, max_tokens=64, temperature=0.8)
        
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("(Make sure vLLM server is running)")


def example_local_transformers():
    """Example: Using transformers for local inference."""
    print("\n" + "=" * 60)
    print("Example 3: Local Transformers Backend")
    print("=" * 60)
    print("""
    Prerequisites:
    1. Install transformers: pip install transformers torch
    2. Have a model downloaded or use Hugging Face auto-download
    
    Models you can use:
    - distilgpt2 (small, fast)
    - gpt2 (medium)
    - meta-llama/Llama-2-7b (requires Hugging Face token)
    """)
    
    try:
        client = LocalLLMClient(
            model_name="distilgpt2",  # Small model for demo
            backend="llama"
        )
        
        prompt = "The future of AI is"
        response = client.generate(prompt, max_tokens=128, temperature=0.9)
        
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        print(f"Model info: {json.dumps(client.get_model_info(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("(Make sure transformers and torch are installed)")


def example_streaming():
    """Example: Streaming generation."""
    print("\n" + "=" * 60)
    print("Example 4: Streaming Generation")
    print("=" * 60)
    
    try:
        client = LocalLLMClient(model_name="gpt2", backend="llama")
        
        prompt = "Generate a short story about a robot:"
        print(f"Prompt: {prompt}")
        print("Response (streaming):")
        
        for chunk in client.generate_stream(prompt, max_tokens=256):
            print(chunk, end='', flush=True)
        
        print()  # New line
        
    except Exception as e:
        print(f"Error: {e}")


def example_with_eacp_orchestrator():
    """Example: Using LLMClient within EACP orchestrator."""
    print("\n" + "=" * 60)
    print("Example 5: Integration with EACP Orchestrator")
    print("=" * 60)
    
    from main import EACPOrchestrator
    
    config = {
        "llm": {
            "model_name": "gpt2",  # or llama2 with Ollama
            "backend": "ollama"  # or "vllm", "llama"
        }
    }
    
    try:
        orchestrator = EACPOrchestrator(config=config)
        
        # Use the LLM client directly
        prompt = "What are the benefits of open-source AI?"
        response = orchestrator.llm_client.generate(prompt, max_tokens=256)
        
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")


def comparison_table():
    """Print comparison of local LLM backends."""
    print("\n" + "=" * 60)
    print("Local LLM Backends Comparison")
    print("=" * 60)
    
    comparison = """
    ╔════════╦═════════╦════════╦═════════╦══════════════╗
    ║ Backend║ Speed   ║ Memory ║ Ease    ║ Requirements ║
    ╠════════╬═════════╬════════╬═════════╬══════════════╣
    ║ Ollama ║ Medium  ║ Medium ║ Easy    ║ Ollama app   ║
    ║ vLLM   ║ Fast    ║ Medium ║ Medium  ║ CUDA, torch  ║
    ║ Llama  ║ Medium  ║ High   ║ Hard    ║ transformers ║
    ╚════════╩═════════╩════════╩═════════╩══════════════╝
    
    Recommended:
    - Development: Ollama (easiest setup)
    - Production: vLLM (fastest inference)
    - Resource-constrained: quantized models with QLoRA
    """
    print(comparison)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("EACP Local LLM Deployment Examples")
    print("=" * 60)
    
    # Show comparison
    comparison_table()
    
    # Run examples (comment out if dependencies missing)
    try:
        example_ollama()
    except:
        print("(Ollama example skipped - not installed)")
    
    try:
        example_local_transformers()
    except:
        print("(Transformers example skipped - not installed)")
    
    try:
        example_streaming()
    except:
        print("(Streaming example skipped - dependencies missing)")
    
    print("\n" + "=" * 60)
    print("For more examples, see: examples/")
    print("=" * 60)
