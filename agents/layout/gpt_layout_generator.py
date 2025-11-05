"""
Stage 4: GPT-based layout generator

Generates final mindmap graph with node positions and edges.
"""

import json
import time
from typing import Dict, Any

from loguru import logger

from agents.utils import robust_gpt_call, load_json, save_json
from agents.prompts import build_prompt, LAYOUT_GENERATE_PROMPT


def run(
    input_path: str,
    output_path: str,
    context_path: str,
    layout_type: str = "hierarchical",
    layout_direction: str = "top-down",
    **kwargs
) -> Dict[str, Any]:
    """
    Generate mindmap layout using GPT

    Args:
        input_path: Path to keywords JSON from Stage 3
        output_path: Path to save graph JSON
        context_path: Path to context JSON from Stage 2
        layout_type: Layout algorithm ("hierarchical", "radial", "timeline", "force_directed")
        layout_direction: Layout direction ("top-down", "left-right", "radial-out", "chronological")

    Returns:
        {
            "status": "success" | "error",
            "processing_time": float,
            "nodes_count": int,
            "edges_count": int,
            "error": str (optional)
        }
    """
    logger.info(f"[STAGE 4] Starting layout generation: {layout_type} ({layout_direction})")
    start_time = time.time()

    try:
        # Load keywords and contexts
        keywords_data = load_json(input_path)
        contexts_data = load_json(context_path)

        session_id = keywords_data.get("session_id", "conv_001")

        # Format data for prompt
        keywords_json = json.dumps(
            keywords_data.get("keywords_by_path", []),
            indent=2,
            ensure_ascii=False
        )

        contexts_json = json.dumps(
            contexts_data.get("contexts", []),
            indent=2,
            ensure_ascii=False
        )

        # Build prompt
        prompt = build_prompt(
            LAYOUT_GENERATE_PROMPT,
            keywords_json=keywords_json,
            contexts_json=contexts_json,
            session_id=session_id,
            layout_algorithm=f"gpt_{layout_type}",
            layout_type=layout_type,
            layout_direction=layout_direction
        )

        # Call GPT
        response = robust_gpt_call(
            prompt=prompt,
            response_format={"type": "json_object"},
            schema_path="graph_schema.json"
        )

        # Save result
        save_json(response, output_path)

        graph = response.get("graph", {})
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        elapsed = time.time() - start_time
        logger.info(
            f"[STAGE 4] SUCCESS: {len(nodes)} nodes, {len(edges)} edges in {elapsed:.2f}s"
        )

        return {
            "status": "success",
            "processing_time": elapsed,
            "nodes_count": len(nodes),
            "edges_count": len(edges),
            "session_id": session_id
        }

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[STAGE 4] ERROR: {e}")

        return {
            "status": "error",
            "processing_time": elapsed,
            "error": str(e)
        }
