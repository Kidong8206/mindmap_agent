"""
Stage 0: GPT-based conversation preprocessor

Cleans raw conversation data and outputs standardized JSONL format.
"""

import time
from typing import Dict, Any

from loguru import logger

from agents.utils import robust_gpt_call, save_jsonl
from agents.prompts import build_prompt, PREPROCESS_PROMPT


def run(
    input_path: str,
    output_path: str,
    session_id: str = "conv_001",
    **kwargs
) -> Dict[str, Any]:
    """
    Preprocess raw conversation using GPT

    Args:
        input_path: Path to raw conversation file (JSON or text)
        output_path: Path to save processed JSONL
        session_id: Conversation ID (e.g., "conv_001")

    Returns:
        {
            "status": "success" | "error",
            "processing_time": float,
            "turns_count": int,
            "error": str (optional)
        }
    """
    logger.info(f"[STAGE 0] Starting preprocessing for {session_id}")
    start_time = time.time()

    try:
        # Load raw conversation
        raw_conversation = _load_raw_conversation(input_path)

        # Build prompt
        prompt = build_prompt(
            PREPROCESS_PROMPT,
            raw_conversation=raw_conversation,
            session_id=session_id
        )

        # Call GPT
        response = robust_gpt_call(
            prompt=prompt,
            response_format={"type": "json_object"},
            schema_path="turns_schema.json"
        )

        # Save as JSONL (one turn per line)
        turns = response.get("turns", [])
        save_jsonl(turns, output_path)

        elapsed = time.time() - start_time
        logger.info(f"[STAGE 0] SUCCESS: {len(turns)} turns processed in {elapsed:.2f}s")

        return {
            "status": "success",
            "processing_time": elapsed,
            "turns_count": len(turns),
            "session_id": session_id
        }

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[STAGE 0] ERROR: {e}")

        return {
            "status": "error",
            "processing_time": elapsed,
            "error": str(e)
        }


def _load_raw_conversation(file_path: str) -> str:
    """
    Load raw conversation from file

    Supports:
    - Plain text file
    - JSON file with specific structure
    - JSONL file

    Returns:
        String representation of conversation
    """
    from pathlib import Path
    import json

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    content = path.read_text(encoding='utf-8')

    # Try to parse as JSON
    try:
        data = json.loads(content)

        # If it's already structured conversation
        if isinstance(data, dict) and "turns" in data:
            turns = data["turns"]
            lines = []
            for turn in turns:
                role = turn.get("role", "unknown")
                text = turn.get("text", "")
                lines.append(f"{role}: {text}")
            return "\n".join(lines)

        # If it's a list of messages
        elif isinstance(data, list):
            lines = []
            for i, item in enumerate(data):
                role = item.get("role", f"speaker_{i%2}")
                text = item.get("content", item.get("text", ""))
                lines.append(f"{role}: {text}")
            return "\n".join(lines)

    except json.JSONDecodeError:
        # Not JSON, treat as plain text
        pass

    # Return as-is (plain text conversation)
    return content
