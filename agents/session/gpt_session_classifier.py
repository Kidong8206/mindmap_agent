"""
Stage 1: GPT-based session classifier

Identifies topic boundaries and splits conversation into sessions.
"""

import time
from typing import Dict, Any, List

from loguru import logger

from agents.utils import robust_gpt_call, load_jsonl, save_json
from agents.prompts import build_prompt, SESSION_CLASSIFY_PROMPT


def run(
    input_path: str,
    output_path: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Classify conversation into topical sessions using GPT

    Args:
        input_path: Path to JSONL file from Stage 0 (0_turns.jsonl)
        output_path: Path to save session split JSON

    Returns:
        {
            "status": "success" | "error",
            "processing_time": float,
            "session_count": int,
            "error": str (optional)
        }
    """
    logger.info(f"[STAGE 1] Starting session classification")
    start_time = time.time()

    try:
        # Load turns
        turns = load_jsonl(input_path)

        if not turns:
            raise ValueError("No turns found in input file")

        # Extract session_id from first turn
        session_id = turns[0].get("session_id", "conv_001")

        # Format turns for prompt
        conversation_text = _format_turns_for_prompt(turns)

        # Build prompt
        prompt = build_prompt(
            SESSION_CLASSIFY_PROMPT,
            conversation_text=conversation_text,
            session_id=session_id
        )

        # Call GPT
        response = robust_gpt_call(
            prompt=prompt,
            response_format={"type": "json_object"},
            schema_path="session_split_schema.json"
        )

        # Save result
        save_json(response, output_path)

        sessions = response.get("sessions", [])
        elapsed = time.time() - start_time

        logger.info(f"[STAGE 1] SUCCESS: {len(sessions)} sessions identified in {elapsed:.2f}s")

        return {
            "status": "success",
            "processing_time": elapsed,
            "session_count": len(sessions),
            "session_id": session_id
        }

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[STAGE 1] ERROR: {e}")

        return {
            "status": "error",
            "processing_time": elapsed,
            "error": str(e)
        }


def _format_turns_for_prompt(turns: List[Dict[str, Any]]) -> str:
    """
    Format turns into readable text for GPT prompt

    Example output:
    [0] user: 안녕하세요
    [1] assistant: 안녕하세요! 무엇을 도와드릴까요?
    [2] user: React Hook에 대해 알려주세요
    """
    lines = []
    for turn in turns:
        turn_id = turn.get("turn_id", 0)
        role = turn.get("role", "unknown")
        text = turn.get("text", "")
        lines.append(f"[{turn_id}] {role}: {text}")

    return "\n".join(lines)
