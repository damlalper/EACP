"""
Fine-tuning example: Train a local LLM with LoRA on custom dataset
"""
import json
from pathlib import Path
from llm.fine_tune.trainer import FineTuningTrainer

# Example dataset preparation
def create_example_dataset():
    """Create example training dataset."""
    examples = [
        {
            "instruction": "Classify the sentiment of this text.",
            "input": "I love this product! It works great.",
            "output": "positive"
        },
        {
            "instruction": "Classify the sentiment of this text.",
            "input": "This product is terrible and broken.",
            "output": "negative"
        },
        {
            "instruction": "Translate English to French.",
            "input": "Hello, how are you?",
            "output": "Bonjour, comment allez-vous?"
        },
        {
            "instruction": "Answer the following question.",
            "input": "What is the capital of France?",
            "output": "Paris"
        },
        {
            "instruction": "Summarize the following text.",
            "input": "The Earth orbits the Sun every 365 days, which defines one year.",
            "output": "Earth takes 365 days to orbit the Sun."
        }
    ]
    
    # Save dataset
    data_file = Path("data/training_dataset.jsonl")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(data_file, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example) + '\n')
    
    print(f"Created example dataset: {data_file}")
    return str(data_file)


def main():
    """Run fine-tuning example."""
    
    # Step 1: Create example dataset
    print("=" * 60)
    print("Step 1: Prepare Dataset")
    print("=" * 60)
    dataset_path = create_example_dataset()
    
    # Step 2: Initialize trainer
    print("\n" + "=" * 60)
    print("Step 2: Initialize Trainer")
    print("=" * 60)
    
    # Using a smaller model for demo (can use: meta-llama/Llama-2-7b-hf)
    trainer = FineTuningTrainer(
        base_model="gpt2",  # Using GPT-2 for demo (small, fast)
        technique="lora",
        output_dir="./models/fine_tuned"
    )
    
    # Step 3: Prepare dataset
    print("\n" + "=" * 60)
    print("Step 3: Format Dataset for Training")
    print("=" * 60)
    
    formatted_path = "data/formatted_dataset.jsonl"
    trainer.prepare_dataset(dataset_path, formatted_path)
    
    # Step 4: Train with LoRA
    print("\n" + "=" * 60)
    print("Step 4: Fine-tune with LoRA")
    print("=" * 60)
    
    config = {
        "epochs": 2,
        "learning_rate": 2e-4,
        "batch_size": 4,
        "lora_r": 8,
        "lora_alpha": 16,
        "lora_dropout": 0.05
    }
    
    result = trainer.train(formatted_path, config=config)
    print(f"Training result: {json.dumps(result, indent=2)}")
    
    # Step 5: Example with QLoRA (commented out for speed)
    print("\n" + "=" * 60)
    print("Step 5: QLoRA Alternative (requires bitsandbytes)")
    print("=" * 60)
    print("""
    # Uncomment below to use QLoRA instead:
    trainer_qlora = FineTuningTrainer(
        base_model="meta-llama/Llama-2-7b-hf",  # Requires Hugging Face token
        technique="qlora"
    )
    result_qlora = trainer_qlora.train(formatted_path, config=config)
    """)
    
    print("\n" + "=" * 60)
    print("Fine-tuning example complete!")
    print("=" * 60)
    print(f"\nModel saved to: {result.get('model_path')}")
    print(f"Metrics: {json.dumps(result.get('metrics'), indent=2)}")


if __name__ == "__main__":
    main()
