"""
Data Validator for EACP Data Pipeline
Validates and quality-checks data before ingestion into RAG or fine-tuning
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validates data quality for RAG ingestion and fine-tuning datasets.

    Checks:
    - Schema validation (required fields, types)
    - Content quality (length, language, encoding)
    - Duplicate detection
    - Fine-tuning format validation (instruction/input/output)
    - RAG document validation (content, metadata)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.validation_results: List[Dict[str, Any]] = []

    def validate_rag_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate documents for RAG vector DB ingestion.

        Expected format:
        {
            "text": "document content",
            "metadata": {"source": "...", "type": "..."}
        }
        """
        results = {
            "total": len(documents),
            "valid": 0,
            "invalid": 0,
            "warnings": 0,
            "issues": [],
            "stats": {
                "avg_length": 0,
                "min_length": float("inf"),
                "max_length": 0,
                "empty_count": 0,
                "duplicate_count": 0
            }
        }

        seen_texts = set()
        total_length = 0

        for i, doc in enumerate(documents):
            issues = []

            # Check required fields
            text = doc.get("text", "")
            if not text:
                issues.append(f"Document {i}: Missing or empty 'text' field")
                results["stats"]["empty_count"] += 1

            # Check content length
            word_count = len(text.split()) if text else 0
            total_length += word_count

            if word_count < 5:
                issues.append(f"Document {i}: Very short content ({word_count} words)")

            if word_count > 10000:
                issues.append(f"Document {i}: Very long content ({word_count} words), consider chunking")

            # Track min/max
            if word_count < results["stats"]["min_length"]:
                results["stats"]["min_length"] = word_count
            if word_count > results["stats"]["max_length"]:
                results["stats"]["max_length"] = word_count

            # Check for duplicates
            text_hash = hash(text[:500]) if text else hash("")
            if text_hash in seen_texts:
                issues.append(f"Document {i}: Duplicate content detected")
                results["stats"]["duplicate_count"] += 1
            seen_texts.add(text_hash)

            # Check metadata
            metadata = doc.get("metadata", {})
            if not metadata:
                issues.append(f"Document {i}: Missing metadata")

            if not metadata.get("source"):
                issues.append(f"Document {i}: Missing source in metadata")

            # Classify result
            if any("Missing or empty 'text'" in issue for issue in issues):
                results["invalid"] += 1
            elif issues:
                results["warnings"] += 1
                results["valid"] += 1
            else:
                results["valid"] += 1

            results["issues"].extend(issues)

        # Calculate averages
        if documents:
            results["stats"]["avg_length"] = round(total_length / len(documents), 1)

        if results["stats"]["min_length"] == float("inf"):
            results["stats"]["min_length"] = 0

        self.validation_results.append({
            "type": "rag",
            "timestamp": datetime.now().isoformat(),
            "results": results
        })

        return results

    def validate_fine_tuning_data(self, data: List[Dict[str, Any]],
                                   format_type: str = "alpaca") -> Dict[str, Any]:
        """
        Validate fine-tuning dataset.

        Supported formats:
        - alpaca: {"instruction": "", "input": "", "output": ""}
        - sharegpt: {"conversations": [{"from": "human", "value": ""}, ...]}
        - openai: {"messages": [{"role": "", "content": ""}, ...]}
        """
        results = {
            "total": len(data),
            "valid": 0,
            "invalid": 0,
            "warnings": 0,
            "issues": [],
            "format": format_type,
            "stats": {
                "avg_instruction_length": 0,
                "avg_output_length": 0,
                "empty_outputs": 0,
                "empty_instructions": 0
            }
        }

        total_instruction_len = 0
        total_output_len = 0

        for i, record in enumerate(data):
            issues = []

            if format_type == "alpaca":
                issues = self._validate_alpaca(i, record)
                instruction = record.get("instruction", "")
                output = record.get("output", "")
                total_instruction_len += len(instruction.split())
                total_output_len += len(output.split())
                if not instruction.strip():
                    results["stats"]["empty_instructions"] += 1
                if not output.strip():
                    results["stats"]["empty_outputs"] += 1

            elif format_type == "sharegpt":
                issues = self._validate_sharegpt(i, record)

            elif format_type == "openai":
                issues = self._validate_openai(i, record)

            if any("INVALID" in issue for issue in issues):
                results["invalid"] += 1
            elif issues:
                results["warnings"] += 1
                results["valid"] += 1
            else:
                results["valid"] += 1

            results["issues"].extend(issues)

        # Stats
        if data:
            results["stats"]["avg_instruction_length"] = round(total_instruction_len / len(data), 1)
            results["stats"]["avg_output_length"] = round(total_output_len / len(data), 1)

        self.validation_results.append({
            "type": "fine_tuning",
            "format": format_type,
            "timestamp": datetime.now().isoformat(),
            "results": results
        })

        return results

    def _validate_alpaca(self, index: int, record: Dict[str, Any]) -> List[str]:
        """Validate alpaca format record"""
        issues = []

        if "instruction" not in record:
            issues.append(f"Record {index}: INVALID - Missing 'instruction' field")
        elif not record["instruction"].strip():
            issues.append(f"Record {index}: Empty instruction")

        if "output" not in record:
            issues.append(f"Record {index}: INVALID - Missing 'output' field")
        elif not record["output"].strip():
            issues.append(f"Record {index}: Empty output")

        # Check for reasonable lengths
        instruction_len = len(record.get("instruction", "").split())
        output_len = len(record.get("output", "").split())

        if instruction_len > 1000:
            issues.append(f"Record {index}: Very long instruction ({instruction_len} words)")
        if output_len > 2000:
            issues.append(f"Record {index}: Very long output ({output_len} words)")

        return issues

    def _validate_sharegpt(self, index: int, record: Dict[str, Any]) -> List[str]:
        """Validate ShareGPT format record"""
        issues = []

        conversations = record.get("conversations", [])
        if not conversations:
            issues.append(f"Record {index}: INVALID - Missing or empty 'conversations'")
            return issues

        if len(conversations) < 2:
            issues.append(f"Record {index}: Conversation has fewer than 2 turns")

        for j, turn in enumerate(conversations):
            if "from" not in turn:
                issues.append(f"Record {index}, turn {j}: Missing 'from' field")
            if "value" not in turn:
                issues.append(f"Record {index}, turn {j}: Missing 'value' field")
            elif not turn["value"].strip():
                issues.append(f"Record {index}, turn {j}: Empty value")

        return issues

    def _validate_openai(self, index: int, record: Dict[str, Any]) -> List[str]:
        """Validate OpenAI chat format record"""
        issues = []

        messages = record.get("messages", [])
        if not messages:
            issues.append(f"Record {index}: INVALID - Missing or empty 'messages'")
            return issues

        valid_roles = {"system", "user", "assistant"}
        for j, msg in enumerate(messages):
            role = msg.get("role", "")
            if role not in valid_roles:
                issues.append(f"Record {index}, msg {j}: Invalid role '{role}'")
            if not msg.get("content", "").strip():
                issues.append(f"Record {index}, msg {j}: Empty content")

        # Check for at least user + assistant
        roles = [m.get("role") for m in messages]
        if "user" not in roles:
            issues.append(f"Record {index}: Missing 'user' message")
        if "assistant" not in roles:
            issues.append(f"Record {index}: Missing 'assistant' message")

        return issues

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all validations"""
        return {
            "total_validations": len(self.validation_results),
            "validations": self.validation_results
        }
