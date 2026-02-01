"""
Instruction templates for fine-tuning
"""

INSTRUCTION_TEMPLATE = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input}

### Response:
{output}
"""

CHAT_TEMPLATE = """<|system|>
{system_message}
<|user|>
{user_message}
<|assistant|>
{assistant_message}
"""

TASK_COMPLETION_TEMPLATE = """Task: {task_description}
Context: {context}
Expected Output: {expected_output}

Complete the task based on the context provided.
"""
