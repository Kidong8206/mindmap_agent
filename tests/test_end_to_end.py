"""
End-to-End Pipeline Test

Tests the complete pipeline from conversation input to final mindmap with evaluation.
"""

import sys
import json
import tempfile
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.session.gpt_session_classifier import run as classify_sessions
from agents.context.gpt_context_analyzer import run as analyze_context
from agents.keyword.gpt_keyword_extractor import run as extract_keywords
from agents.layout.gpt_layout_generator import run as generate_layout

from agents.evaluate.evaluate_context import evaluate_context
from agents.evaluate.evaluate_layout import evaluate_layout
from agents.evaluate.evaluate_comprehensive import evaluate_comprehensive


def run_end_to_end_test():
    """
    Run complete end-to-end pipeline test.

    Pipeline:
    1. Input: mock_turns.jsonl (preprocessed conversation)
    2. Stage 1: Session classification (GPT)
    3. Stage 2: Context analysis (GPT)
    4. Stage 3: Keyword extraction (GPT)
    5. Stage 4: Layout generation (GPT)
    6. Evaluation: 30 metrics
    """

    print("=" * 70)
    print("END-TO-END PIPELINE TEST WITH GPT API")
    print("=" * 70)

    # Setup paths
    fixtures_dir = Path(__file__).parent / "fixtures"
    input_file = fixtures_dir / "mock_turns.jsonl"
    output_dir = Path(tempfile.mkdtemp())

    print(f"\nInput: {input_file}")
    print(f"Output: {output_dir}\n")

    # Track timing and results
    stage_times = {}
    stage_results = {}
    total_start = time.time()

    # Stage 1: Session Classification
    print("[1/5] Running Session Classification (GPT)...")
    start = time.time()
    try:
        session_file = output_dir / "session_split.json"
        classify_sessions(
            input_path=str(input_file),
            output_path=str(session_file),
            session_id="conv_001"
        )
        stage_times['stage_1'] = time.time() - start
        stage_results['stage_1'] = 'success'
        print(f"  ✓ Completed in {stage_times['stage_1']:.2f}s")
        print(f"  ✓ Output: {session_file}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        stage_results['stage_1'] = 'failed'
        return None

    # Stage 2: Context Analysis
    print("\n[2/5] Running Context Analysis (GPT)...")
    start = time.time()
    try:
        context_file = output_dir / "context.json"
        analyze_context(
            input_path=str(session_file),  # session_split.json
            output_path=str(context_file),
            turns_path=str(input_file)
        )
        stage_times['stage_2'] = time.time() - start
        stage_results['stage_2'] = 'success'
        print(f"  ✓ Completed in {stage_times['stage_2']:.2f}s")
        print(f"  ✓ Output: {context_file}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        stage_results['stage_2'] = 'failed'
        return None

    # Stage 3: Keyword Extraction
    print("\n[3/5] Running Keyword Extraction (GPT)...")
    start = time.time()
    try:
        keywords_file = output_dir / "keywords.json"
        extract_keywords(
            input_path=str(context_file),  # context.json
            output_path=str(keywords_file),
            turns_path=str(input_file)
        )
        stage_times['stage_3'] = time.time() - start
        stage_results['stage_3'] = 'success'
        print(f"  ✓ Completed in {stage_times['stage_3']:.2f}s")
        print(f"  ✓ Output: {keywords_file}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        stage_results['stage_3'] = 'failed'
        return None

    # Stage 4: Layout Generation
    print("\n[4/5] Running Layout Generation (GPT)...")
    start = time.time()
    try:
        graph_file = output_dir / "graph.json"
        generate_layout(
            input_path=str(keywords_file),  # keywords.json
            output_path=str(graph_file),
            context_path=str(context_file)
        )
        stage_times['stage_4'] = time.time() - start
        stage_results['stage_4'] = 'success'
        print(f"  ✓ Completed in {stage_times['stage_4']:.2f}s")
        print(f"  ✓ Output: {graph_file}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        stage_results['stage_4'] = 'failed'
        return None

    total_pipeline_time = time.time() - total_start

    # Stage 5: Evaluation
    print("\n[5/5] Running 30-Metric Evaluation...")
    print("  (Using mock golden annotations and embeddings)")

    # For evaluation, we need embeddings and golden annotations
    # Use mock data for now
    sys.path.insert(0, str(Path(__file__).parent))
    from test_utils import load_mock_embeddings, load_mock_golden_annotations
    import numpy as np

    embeddings = load_mock_embeddings()
    golden = load_mock_golden_annotations()

    # Save embeddings temporarily
    embeddings_file = output_dir / "embeddings.npy"
    np.save(embeddings_file, embeddings)

    # Run evaluations
    print("\n  Running Context Rubric...")
    context_eval = evaluate_context(
        context_json=str(context_file),
        embeddings_npy=str(embeddings_file),
        session_split_json=str(session_file),
        golden_annotations=golden,
        processing_time=stage_times['stage_2']
    )

    print("  Running Layout Rubric...")
    layout_eval = evaluate_layout(
        graph_json=str(graph_file),
        render_time=stage_times['stage_4']
    )

    print("  Running Comprehensive Rubric...")
    comprehensive_eval = evaluate_comprehensive(
        graph_json=str(graph_file),
        context_score=context_eval['weighted_score'],
        layout_score=layout_eval['weighted_score'],
        golden_annotations=golden,
        stage_results=stage_results,
        user_ratings=[4.0, 4.5, 3.5, 4.0],  # Mock user ratings
        total_time_sec=total_pipeline_time,
        api_calls=4,  # 4 GPT calls
        error_count=0,
        total_runs=1
    )

    # Final Results
    print("\n" + "=" * 70)
    print("END-TO-END PIPELINE TEST RESULTS")
    print("=" * 70)

    print("\n📊 Pipeline Execution:")
    for stage, status in stage_results.items():
        time_taken = stage_times.get(stage, 0)
        print(f"  {stage}: {status.upper()} ({time_taken:.2f}s)")
    print(f"  Total Pipeline Time: {total_pipeline_time:.2f}s")

    print("\n📊 Evaluation Scores:")
    ctx_score = context_eval['weighted_score']
    lay_score = layout_eval['weighted_score']
    com_score = comprehensive_eval['weighted_score']
    overall = (ctx_score + lay_score + com_score) / 3

    print(f"  Context Rubric:        {ctx_score:.4f}")
    print(f"  Layout Rubric:         {lay_score:.4f}")
    print(f"  Comprehensive Rubric:  {com_score:.4f}")
    print(f"  Overall Score:         {overall:.4f}")

    print("\n📁 Generated Files:")
    for file in sorted(output_dir.glob("*.json")):
        size = file.stat().st_size
        print(f"  {file.name} ({size} bytes)")

    print("\n" + "=" * 70)
    if all(s == 'success' for s in stage_results.values()):
        print("✅ END-TO-END TEST COMPLETED SUCCESSFULLY!")
    else:
        print("⚠️  END-TO-END TEST COMPLETED WITH SOME FAILURES")
    print("=" * 70)

    return {
        'stage_results': stage_results,
        'stage_times': stage_times,
        'evaluations': {
            'context': context_eval,
            'layout': layout_eval,
            'comprehensive': comprehensive_eval
        },
        'output_dir': output_dir,
        'overall_score': overall
    }


if __name__ == "__main__":
    result = run_end_to_end_test()

    if result and all(s == 'success' for s in result['stage_results'].values()):
        print(f"\n✅ Test passed!")
        print(f"📂 Output directory: {result['output_dir']}")
        print(f"🎯 Overall Score: {result['overall_score']:.4f}")
        sys.exit(0)
    else:
        print(f"\n❌ Test failed!")
        sys.exit(1)
