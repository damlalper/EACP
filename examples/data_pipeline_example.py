"""
Data Pipeline & ETL Example
Demonstrates how to use the ETL engine for RAG data preparation
and fine-tuning dataset generation.
"""

import json
import os
from data_pipeline import ETLEngine, DocumentProcessor, DataValidator


def main():
    # =========================================================
    # 1. Initialize components
    # =========================================================
    etl = ETLEngine(config={"output_dir": "data/processed"})
    processor = DocumentProcessor()
    validator = DataValidator()

    print("Data Pipeline initialized")
    print(f"Supported formats: {processor.supported_formats}")

    # =========================================================
    # 2. Process individual documents
    # =========================================================
    print("\n--- Document Processing ---")

    # Create sample data directory
    os.makedirs("data/sample", exist_ok=True)

    # Create a sample text file
    sample_text = """
    Enterprise AI Platform Architecture

    The modern enterprise AI platform consists of several key components:

    1. Agent Framework: Multi-agent orchestration for task automation
    2. LLM Layer: Local and cloud-based model deployment
    3. Knowledge Base: Vector databases and semantic search
    4. Integration Layer: Enterprise system connectors (JIRA, SAP, CRM)
    5. MLOps: Monitoring, logging, and model lifecycle management

    Best practices include:
    - Use RAG for domain-specific knowledge retrieval
    - Fine-tune models with LoRA for cost-effective customization
    - Implement hybrid search combining semantic and keyword approaches
    - Monitor inference latency and model accuracy continuously
    """

    with open("data/sample/architecture.txt", "w", encoding="utf-8") as f:
        f.write(sample_text)

    result = processor.process_file("data/sample/architecture.txt")
    print(f"Processed: {result['filepath']}")
    print(f"  Format: {result['format']}")
    print(f"  Words: {result['word_count']}")
    print(f"  Lines: {result['line_count']}")

    # =========================================================
    # 3. ETL Job: Text files to RAG-ready chunks
    # =========================================================
    print("\n--- ETL: Text to RAG ---")

    job = etl.create_job(
        name="Sample docs to RAG",
        source_type="file",
        source_config={
            "path": "data/sample/architecture.txt",
            "chunk_size": 100,  # Small chunks for demo
            "chunk_overlap": 20
        },
        target="rag"
    )

    result = etl.run_job(job.job_id)
    print(f"Job: {result.name}")
    print(f"Status: {result.status}")
    print(f"Records processed: {result.records_processed}")
    print(f"Output: {result.output_path}")

    # Read and display output
    if result.output_path and os.path.exists(result.output_path):
        with open(result.output_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        print(f"\nGenerated {len(chunks)} RAG chunks:")
        for i, chunk in enumerate(chunks[:3]):
            print(f"  Chunk {i}: {chunk['text'][:80]}...")
            print(f"    Metadata: source={chunk['metadata']['source']}, "
                  f"chunk={chunk['metadata']['chunk_index']}/{chunk['metadata']['total_chunks']}")

    # =========================================================
    # 4. ETL Job: JSONL to fine-tuning format
    # =========================================================
    print("\n--- ETL: JSONL to Fine-Tuning ---")

    # Create sample training data
    training_data = [
        {"instruction": "Summarize the benefits of RAG.", "input": "", "output": "RAG combines retrieval with generation, providing up-to-date and domain-specific responses without fine-tuning."},
        {"instruction": "What is LoRA?", "input": "", "output": "LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning method that trains small adapter layers instead of the full model."},
        {"instruction": "Explain multi-agent orchestration.", "input": "", "output": "Multi-agent orchestration coordinates multiple AI agents with different roles to collaboratively complete complex tasks."}
    ]

    os.makedirs("data/sample", exist_ok=True)
    with open("data/sample/training.jsonl", "w", encoding="utf-8") as f:
        for record in training_data:
            f.write(json.dumps(record) + "\n")

    job = etl.create_job(
        name="Prepare fine-tuning dataset",
        source_type="jsonl",
        source_config={
            "path": "data/sample/training.jsonl",
            "format": "alpaca"
        },
        target="fine_tuning"
    )

    result = etl.run_job(job.job_id)
    print(f"Job: {result.name}")
    print(f"Status: {result.status}")
    print(f"Records: {result.records_processed}")

    # =========================================================
    # 5. Data Validation
    # =========================================================
    print("\n--- Data Validation: RAG Documents ---")

    sample_docs = [
        {"text": "This is a valid document with enough content to be useful for retrieval.", "metadata": {"source": "test.txt", "type": "txt"}},
        {"text": "", "metadata": {"source": "empty.txt"}},  # Invalid: empty
        {"text": "Short", "metadata": {}},  # Warning: too short, no source
        {"text": "This is a valid document with enough content to be useful for retrieval.", "metadata": {"source": "duplicate.txt"}},  # Duplicate
    ]

    validation = validator.validate_rag_documents(sample_docs)
    print(f"Total: {validation['total']}")
    print(f"Valid: {validation['valid']}")
    print(f"Invalid: {validation['invalid']}")
    print(f"Warnings: {validation['warnings']}")
    print(f"Duplicates: {validation['stats']['duplicate_count']}")
    print(f"Issues:")
    for issue in validation["issues"]:
        print(f"  - {issue}")

    print("\n--- Data Validation: Fine-Tuning ---")

    sample_ft_data = [
        {"instruction": "What is AI?", "input": "", "output": "Artificial Intelligence is the simulation of human intelligence in machines."},
        {"instruction": "", "input": "", "output": "No instruction"},  # Warning: empty instruction
        {"output": "Missing instruction field"},  # Invalid: no instruction
    ]

    ft_validation = validator.validate_fine_tuning_data(sample_ft_data, format_type="alpaca")
    print(f"Total: {ft_validation['total']}")
    print(f"Valid: {ft_validation['valid']}")
    print(f"Invalid: {ft_validation['invalid']}")
    print(f"Issues:")
    for issue in ft_validation["issues"]:
        print(f"  - {issue}")

    # =========================================================
    # 6. Job Management
    # =========================================================
    print("\n--- All Jobs ---")
    for job in etl.get_all_jobs():
        status = etl.get_job_status(job.job_id)
        print(f"  [{status['status']}] {status['name']} - {status['records_processed']} records")


if __name__ == "__main__":
    main()
