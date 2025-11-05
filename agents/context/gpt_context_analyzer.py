"""
Stage 2: GPT-based context analyzer

Identifies main path and side branches within each session.
"""

import time
from typing import Dict, Any, List

from loguru import logger

from agents.utils import robust_gpt_call, load_json, load_jsonl, save_json
from agents.prompts import build_prompt, CONTEXT_ANALYZE_PROMPT


def run(
    input_path: str,
    output_path: str,
    turns_path: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Analyze conversation context: main path vs side branches

    Args:
        input_path: Path to session split JSON from Stage 1
        output_path: Path to save context analysis JSON
        turns_path: Path to turns JSONL from Stage 0 (for turn text)

    Returns:
        {
            "status": "success" | "error",
            "processing_time": float,
            "contexts_count": int,
            "error": str (optional)
        }
    """
    logger.info(f"[STAGE 2] Starting context analysis")
    start_time = time.time()

    try:
        # Load sessions and turns
        session_data = load_json(input_path)
        turns = load_jsonl(turns_path)

        sessions = session_data.get("sessions", [])
        session_id = session_data.get("session_id", "conv_001")

        if not sessions:
            raise ValueError("No sessions found in input")

        # Analyze each session
        contexts = []

        for session in sessions:
            logger.info(f"[STAGE 2] Analyzing session {session['session_num']}")

            context = _analyze_single_session(session, turns)
            contexts.append(context)

        # Build result
        result = {
            "session_id": session_id,
            "algorithm": "gpt_context_analyzer",
            "contexts": contexts
        }

        # Save result
        save_json(result, output_path)

        elapsed = time.time() - start_time
        logger.info(f"[STAGE 2] SUCCESS: {len(contexts)} contexts analyzed in {elapsed:.2f}s")

        return {
            "status": "success",
            "processing_time": elapsed,
            "contexts_count": len(contexts),
            "session_id": session_id
        }

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[STAGE 2] ERROR: {e}")

        return {
            "status": "error",
            "processing_time": elapsed,
            "error": str(e)
        }


def _analyze_single_session(
    session: Dict[str, Any],
    all_turns: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze one session to identify main/side paths

    Args:
        session: Session dict from Stage 1
        all_turns: All turns from Stage 0

    Returns:
        Context dict with main_path and side_paths
    """
    session_num = session["session_num"]
    turn_range = session["turn_range"]
    summary = session["summary"]

    # Extract session turns
    start_turn, end_turn = turn_range
    session_turns = all_turns[start_turn:end_turn + 1]

    # Format turns for prompt
    session_turns_text = "\n".join([
        f"[{t['turn_id']}] {t['role']}: {t['text']}"
        for t in session_turns
    ])

    # Build prompt
    prompt = build_prompt(
        CONTEXT_ANALYZE_PROMPT,
        session_num=session_num,
        session_summary=summary,
        turn_range=turn_range,
        session_turns_text=session_turns_text
    )

    # Call GPT
    response = robust_gpt_call(
        prompt=prompt,
        response_format={"type": "json_object"},
        schema_path="context_schema.json"
    )

    return response
