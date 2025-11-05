"""
Pipeline Orchestrator

Runs complete mindmap generation pipeline: Stage 0-4 + Visualization
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from agents.ingest import gpt_preprocessor
from agents.session import gpt_session_classifier
from agents.context import gpt_context_analyzer
from agents.keyword import gpt_keyword_extractor
from agents.layout import gpt_layout_generator
from agents.visualizer import visualize_mindmap
from agents.utils import save_json


def run_pipeline(
    input_conversation: str,
    session_id: str = None,
    layout_type: str = "hierarchical",
    layout_direction: str = "top-down",
    output_dir: str = None
) -> dict:
    """
    Run complete mindmap generation pipeline

    Args:
        input_conversation: Path to raw conversation file
        session_id: Conversation ID (auto-generated if None)
        layout_type: Layout algorithm
        layout_direction: Layout direction
        output_dir: Output directory (auto-generated if None)

    Returns:
        Pipeline result dict with paths and metrics
    """
    start_time = time.time()

    # Generate session_id if not provided
    if session_id is None:
        session_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Generate output directory
    if output_dir is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        run_id = f"run_{timestamp}_{session_id}"
        output_dir = f"outputs/runs/{run_id}"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"=" * 80)
    logger.info(f"PIPELINE START: {session_id}")
    logger.info(f"Output Directory: {output_dir}")
    logger.info(f"=" * 80)

    results = {
        "session_id": session_id,
        "run_id": run_id if output_dir is None else output_dir,
        "input_conversation": input_conversation,
        "layout_type": layout_type,
        "layout_direction": layout_direction,
        "stages": {}
    }

    try:
        # ===== Stage 0: Preprocessing =====
        logger.info("\n" + "=" * 80)
        logger.info("STAGE 0: Preprocessing")
        logger.info("=" * 80)

        stage0_output = output_path / "0_turns.jsonl"

        stage0_result = gpt_preprocessor.run(
            input_path=input_conversation,
            output_path=str(stage0_output),
            session_id=session_id
        )

        results["stages"]["stage0"] = stage0_result

        if stage0_result["status"] != "success":
            raise RuntimeError(f"Stage 0 failed: {stage0_result.get('error')}")

        # ===== Stage 1: Session Classification =====
        logger.info("\n" + "=" * 80)
        logger.info("STAGE 1: Session Classification")
        logger.info("=" * 80)

        stage1_output = output_path / "1_session_split.json"

        stage1_result = gpt_session_classifier.run(
            input_path=str(stage0_output),
            output_path=str(stage1_output)
        )

        results["stages"]["stage1"] = stage1_result

        if stage1_result["status"] != "success":
            raise RuntimeError(f"Stage 1 failed: {stage1_result.get('error')}")

        # ===== Stage 2: Context Analysis =====
        logger.info("\n" + "=" * 80)
        logger.info("STAGE 2: Context Analysis")
        logger.info("=" * 80)

        stage2_output = output_path / "2_context.json"

        stage2_result = gpt_context_analyzer.run(
            input_path=str(stage1_output),
            output_path=str(stage2_output),
            turns_path=str(stage0_output)
        )

        results["stages"]["stage2"] = stage2_result

        if stage2_result["status"] != "success":
            raise RuntimeError(f"Stage 2 failed: {stage2_result.get('error')}")

        # ===== Stage 3: Keyword Extraction =====
        logger.info("\n" + "=" * 80)
        logger.info("STAGE 3: Keyword Extraction")
        logger.info("=" * 80)

        stage3_output = output_path / "3_keywords.json"

        stage3_result = gpt_keyword_extractor.run(
            input_path=str(stage2_output),
            output_path=str(stage3_output),
            turns_path=str(stage0_output)
        )

        results["stages"]["stage3"] = stage3_result

        if stage3_result["status"] != "success":
            raise RuntimeError(f"Stage 3 failed: {stage3_result.get('error')}")

        # ===== Stage 4: Layout Generation =====
        logger.info("\n" + "=" * 80)
        logger.info("STAGE 4: Layout Generation")
        logger.info("=" * 80)

        stage4_output = output_path / "4_graph.json"

        stage4_result = gpt_layout_generator.run(
            input_path=str(stage3_output),
            output_path=str(stage4_output),
            context_path=str(stage2_output),
            layout_type=layout_type,
            layout_direction=layout_direction
        )

        results["stages"]["stage4"] = stage4_result

        if stage4_result["status"] != "success":
            raise RuntimeError(f"Stage 4 failed: {stage4_result.get('error')}")

        # ===== Visualization =====
        logger.info("\n" + "=" * 80)
        logger.info("VISUALIZATION")
        logger.info("=" * 80)

        visualization_output = output_path / "visualization.png"

        visualize_mindmap(
            graph_json_path=str(stage4_output),
            output_png_path=str(visualization_output)
        )

        results["visualization_path"] = str(visualization_output)

        # ===== Summary =====
        total_time = time.time() - start_time

        results["status"] = "success"
        results["total_processing_time"] = total_time

        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Total Time: {total_time:.2f}s")
        logger.info(f"Output Directory: {output_dir}")
        logger.info(f"Visualization: {visualization_output}")
        logger.info("=" * 80)

        # Save metadata
        metadata_path = output_path / "metadata.json"
        save_json(results, str(metadata_path))

        return results

    except Exception as e:
        total_time = time.time() - start_time

        logger.error("\n" + "=" * 80)
        logger.error("PIPELINE FAILED")
        logger.error("=" * 80)
        logger.error(f"Error: {e}")
        logger.error(f"Total Time: {total_time:.2f}s")
        logger.error("=" * 80)

        results["status"] = "error"
        results["error"] = str(e)
        results["total_processing_time"] = total_time

        # Save metadata even on failure
        metadata_path = output_path / "metadata.json"
        save_json(results, str(metadata_path))

        raise


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Run mindmap generation pipeline"
    )

    parser.add_argument(
        "input",
        help="Path to raw conversation file"
    )

    parser.add_argument(
        "--session-id",
        help="Conversation ID (default: auto-generated)"
    )

    parser.add_argument(
        "--layout",
        choices=["hierarchical", "radial", "timeline", "force_directed"],
        default="hierarchical",
        help="Layout algorithm (default: hierarchical)"
    )

    parser.add_argument(
        "--direction",
        choices=["top-down", "left-right", "radial-out", "chronological"],
        default="top-down",
        help="Layout direction (default: top-down)"
    )

    parser.add_argument(
        "--output",
        help="Output directory (default: auto-generated)"
    )

    args = parser.parse_args()

    # Run pipeline
    result = run_pipeline(
        input_conversation=args.input,
        session_id=args.session_id,
        layout_type=args.layout,
        layout_direction=args.direction,
        output_dir=args.output
    )

    if result["status"] == "success":
        print(f"\n✅ Pipeline completed successfully!")
        print(f"📁 Output: {result['run_id']}")
        print(f"🖼️  Visualization: {result['visualization_path']}")
        sys.exit(0)
    else:
        print(f"\n❌ Pipeline failed: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
