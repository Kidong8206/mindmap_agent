"""
Stage 3: GPT-based keyword extractor

Extracts 5-10 keywords from each path (main and side).
"""

import time
from typing import Dict, Any, List

from loguru import logger

from agents.utils import robust_gpt_call, load_json, load_jsonl, save_json
from agents.prompts import build_prompt, KEYWORD_EXTRACT_PROMPT


def run(
    input_path: str,
    output_path: str,
    turns_path: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Extract keywords from each path using GPT

    Args:
        input_path: Path to context JSON from Stage 2
        output_path: Path to save keywords JSON
        turns_path: Path to turns JSONL from Stage 0

    Returns:
        {
            "status": "success" | "error",
            "processing_time": float,
            "keywords_count": int,
            "error": str (optional)
        }
    """
    logger.info(f"[STAGE 3] Starting keyword extraction")
    start_time = time.time()

    try:
        # Load contexts and turns
        context_data = load_json(input_path)
        turns = load_jsonl(turns_path)

        contexts = context_data.get("contexts", [])
        session_id = context_data.get("session_id", "conv_001")

        if not contexts:
            raise ValueError("No contexts found in input")

        # Extract keywords for each path
        keywords_by_path = []
        total_keywords = 0

        for context in contexts:
            logger.info(f"[STAGE 3] Processing session {context['session_num']}")

            # Main path
            main_path = context["main_path"]
            main_keywords = _extract_keywords_from_path(main_path, turns)
            keywords_by_path.append(main_keywords)
            total_keywords += len(main_keywords.get("keywords", []))

            # Side paths
            for side_path in context.get("side_paths", []):
                side_keywords = _extract_keywords_from_path(side_path, turns)
                keywords_by_path.append(side_keywords)
                total_keywords += len(side_keywords.get("keywords", []))

        # Build result
        result = {
            "session_id": session_id,
            "algorithm": "gpt_keyword_extractor",
            "keywords_by_path": keywords_by_path
        }

        # Save result
        save_json(result, output_path)

        elapsed = time.time() - start_time
        logger.info(f"[STAGE 3] SUCCESS: {total_keywords} keywords extracted in {elapsed:.2f}s")

        return {
            "status": "success",
            "processing_time": elapsed,
            "keywords_count": total_keywords,
            "session_id": session_id
        }

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[STAGE 3] ERROR: {e}")

        return {
            "status": "error",
            "processing_time": elapsed,
            "error": str(e)
        }


def _extract_keywords_from_path(
    path: Dict[str, Any],
    all_turns: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extract keywords from a single path

    Args:
        path: Path dict (main_path or side_path)
        all_turns: All turns from Stage 0

    Returns:
        Keywords dict with path_id and keywords list
    """
    path_id = path["path_id"]
    path_topic = path["topic"]
    path_turns = path["turns"]

    # Extract turn texts
    path_texts = []
    for turn_idx in path_turns:
        if turn_idx < len(all_turns):
            path_texts.append(all_turns[turn_idx]["text"])

    path_text = " ".join(path_texts)

    # Build prompt
    prompt = build_prompt(
        KEYWORD_EXTRACT_PROMPT,
        path_id=path_id,
        path_topic=path_topic,
        path_turns=path_turns,
        path_text=path_text
    )

    # Call GPT
    response = robust_gpt_call(
        prompt=prompt,
        response_format={"type": "json_object"}
    )

    return response
