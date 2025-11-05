"""
Integration tests for complete evaluation system.

Tests the full evaluation flow:
1. Load mock data for all pipeline stages
2. Run Context Rubric evaluation (10 metrics)
3. Run Layout Rubric evaluation (10 metrics)
4. Run Comprehensive Rubric evaluation (10 metrics)
5. Verify overall scoring and reporting
"""

import json
import tempfile
from pathlib import Path
import pytest
import numpy as np

# Import evaluation functions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.evaluate.evaluate_context import evaluate_context
from agents.evaluate.evaluate_layout import evaluate_layout
from agents.evaluate.evaluate_comprehensive import evaluate_comprehensive

from test_utils import (
    load_mock_turns,
    load_mock_session_split,
    load_mock_context,
    load_mock_keywords,
    load_mock_graph,
    load_mock_golden_annotations,
    load_mock_embeddings,
    save_temp_json,
    save_temp_embeddings,
    assert_metric_in_range
)


@pytest.fixture
def all_mock_data():
    """Load all mock data needed for integration test."""
    return {
        "turns": load_mock_turns(),
        "session_split": load_mock_session_split(),
        "context": load_mock_context(),
        "keywords": load_mock_keywords(),
        "graph": load_mock_graph(),
        "golden": load_mock_golden_annotations(),
        "embeddings": load_mock_embeddings()
    }


@pytest.fixture
def temp_files(all_mock_data):
    """Create all temporary files needed for evaluation."""
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())

    # Save all data to temp files
    turns_file = temp_dir / "turns.jsonl"
    with open(turns_file, "w", encoding="utf-8") as f:
        json.dump(all_mock_data["turns"], f, ensure_ascii=False)

    session_file = temp_dir / "session_split.json"
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(all_mock_data["session_split"], f, ensure_ascii=False)

    context_file = temp_dir / "context.json"
    with open(context_file, "w", encoding="utf-8") as f:
        json.dump(all_mock_data["context"], f, ensure_ascii=False)

    keywords_file = temp_dir / "keywords.json"
    with open(keywords_file, "w", encoding="utf-8") as f:
        json.dump(all_mock_data["keywords"], f, ensure_ascii=False)

    graph_file = temp_dir / "graph.json"
    with open(graph_file, "w", encoding="utf-8") as f:
        json.dump(all_mock_data["graph"], f, ensure_ascii=False)

    embeddings_file = temp_dir / "embeddings.npy"
    np.save(embeddings_file, all_mock_data["embeddings"])

    return {
        "turns": str(turns_file),
        "session_split": str(session_file),
        "context": str(context_file),
        "keywords": str(keywords_file),
        "graph": str(graph_file),
        "embeddings": str(embeddings_file),
        "golden": all_mock_data["golden"]
    }


class TestContextRubricIntegration:
    """Integration test for Context Rubric."""

    def test_context_rubric_full_evaluation(self, temp_files):
        """Test complete context rubric evaluation."""
        result = evaluate_context(
            context_json=temp_files["context"],
            embeddings_npy=temp_files["embeddings"],
            session_split_json=temp_files["session_split"],
            golden_annotations=temp_files["golden"],
            processing_time=1.5
        )

        # Verify structure
        assert "context_rubric_score" in result
        assert "metrics" in result
        assert "metadata" in result

        # Verify all 10 metrics are present and valid
        metrics = result["metrics"]
        assert len(metrics) == 10

        for metric_name, metric_data in metrics.items():
            assert isinstance(metric_data, dict), f"Metric {metric_name} should be dict"
            # Each metric should have at least a score
            assert len(metric_data) > 0

        # Verify overall score is valid
        assert_metric_in_range(result["context_rubric_score"])

        # Verify metadata
        assert result["metadata"]["num_metrics"] == 10
        assert result["metadata"]["processing_time"] == 1.5

        print("\n✓ Context Rubric Integration Test Passed")
        print(f"  Overall Score: {result['context_rubric_score']:.3f}")
        print(f"  Metrics Evaluated: {len(metrics)}")


class TestLayoutRubricIntegration:
    """Integration test for Layout Rubric."""

    def test_layout_rubric_full_evaluation(self, temp_files):
        """Test complete layout rubric evaluation."""
        result = evaluate_layout(
            graph_json=temp_files["graph"],
            golden_annotations=temp_files["golden"],
            render_time=0.8
        )

        # Verify structure
        assert "layout_rubric_score" in result
        assert "metrics" in result
        assert "metadata" in result

        # Verify all 10 metrics are present and valid
        metrics = result["metrics"]
        assert len(metrics) == 10

        for metric_name, metric_data in metrics.items():
            assert isinstance(metric_data, dict), f"Metric {metric_name} should be dict"

        # Verify overall score is valid
        assert_metric_in_range(result["layout_rubric_score"])

        # Verify metadata
        assert result["metadata"]["num_metrics"] == 10
        assert result["metadata"]["render_time"] == 0.8

        print("\n✓ Layout Rubric Integration Test Passed")
        print(f"  Overall Score: {result['layout_rubric_score']:.3f}")
        print(f"  Metrics Evaluated: {len(metrics)}")


class TestComprehensiveRubricIntegration:
    """Integration test for Comprehensive Rubric."""

    def test_comprehensive_rubric_full_evaluation(self, temp_files, all_mock_data):
        """Test complete comprehensive rubric evaluation."""
        # First get context and layout scores
        context_result = evaluate_context(
            context_json=temp_files["context"],
            embeddings_npy=temp_files["embeddings"],
            session_split_json=temp_files["session_split"],
            golden_annotations=temp_files["golden"],
            processing_time=1.5
        )

        layout_result = evaluate_layout(
            graph_json=temp_files["graph"],
            golden_annotations=temp_files["golden"],
            render_time=0.8
        )

        # Mock pipeline outputs
        pipeline_outputs = {
            "stage_0_turns": all_mock_data["turns"],
            "stage_1_sessions": all_mock_data["session_split"],
            "stage_2_context": all_mock_data["context"],
            "stage_3_keywords": all_mock_data["keywords"],
            "stage_4_graph": all_mock_data["graph"]
        }

        # Mock execution log
        execution_log = {
            "stage_0": {"status": "success", "time": 0.5},
            "stage_1": {"status": "success", "time": 0.8},
            "stage_2": {"status": "success", "time": 1.2},
            "stage_3": {"status": "success", "time": 0.9},
            "stage_4": {"status": "success", "time": 1.1}
        }

        # Mock cost data
        cost_data = {
            "total_tokens": 8500,
            "total_cost_usd": 0.12
        }

        # Run comprehensive evaluation
        result = evaluate_comprehensive(
            context_rubric_score=context_result["context_rubric_score"],
            layout_rubric_score=layout_result["layout_rubric_score"],
            graph_json=temp_files["graph"],
            keywords_json=temp_files["keywords"],
            golden_annotations=temp_files["golden"],
            conversation_turns=all_mock_data["turns"],
            pipeline_outputs=pipeline_outputs,
            execution_log=execution_log,
            cost_data=cost_data,
            user_rating=4.0,
            total_processing_time=4.5
        )

        # Verify structure
        assert "comprehensive_rubric_score" in result
        assert "metrics" in result
        assert "metadata" in result

        # Verify all 10 metrics are present and valid
        metrics = result["metrics"]
        assert len(metrics) == 10

        for metric_name, metric_data in metrics.items():
            assert isinstance(metric_data, dict), f"Metric {metric_name} should be dict"

        # Verify overall score is valid
        assert_metric_in_range(result["comprehensive_rubric_score"])

        print("\n✓ Comprehensive Rubric Integration Test Passed")
        print(f"  Overall Score: {result['comprehensive_rubric_score']:.3f}")
        print(f"  Metrics Evaluated: {len(metrics)}")


class TestFullPipelineEvaluation:
    """Integration test for complete pipeline evaluation (all 3 rubrics)."""

    def test_complete_3_rubric_evaluation(self, temp_files, all_mock_data):
        """Test complete evaluation pipeline with all 3 rubrics (30 metrics total)."""
        print("\n" + "="*60)
        print("FULL PIPELINE EVALUATION TEST")
        print("="*60)

        # Step 1: Context Rubric (10 metrics)
        print("\n[1/3] Evaluating Context Rubric...")
        context_result = evaluate_context(
            context_json=temp_files["context"],
            embeddings_npy=temp_files["embeddings"],
            session_split_json=temp_files["session_split"],
            golden_annotations=temp_files["golden"],
            processing_time=1.5
        )

        context_score = context_result["context_rubric_score"]
        print(f"  ✓ Context Score: {context_score:.3f}")
        print(f"  ✓ Metrics: {len(context_result['metrics'])}")

        # Step 2: Layout Rubric (10 metrics)
        print("\n[2/3] Evaluating Layout Rubric...")
        layout_result = evaluate_layout(
            graph_json=temp_files["graph"],
            golden_annotations=temp_files["golden"],
            render_time=0.8
        )

        layout_score = layout_result["layout_rubric_score"]
        print(f"  ✓ Layout Score: {layout_score:.3f}")
        print(f"  ✓ Metrics: {len(layout_result['metrics'])}")

        # Step 3: Comprehensive Rubric (10 metrics)
        print("\n[3/3] Evaluating Comprehensive Rubric...")

        pipeline_outputs = {
            "stage_0_turns": all_mock_data["turns"],
            "stage_1_sessions": all_mock_data["session_split"],
            "stage_2_context": all_mock_data["context"],
            "stage_3_keywords": all_mock_data["keywords"],
            "stage_4_graph": all_mock_data["graph"]
        }

        execution_log = {
            f"stage_{i}": {"status": "success"} for i in range(5)
        }

        cost_data = {
            "total_tokens": 8500,
            "total_cost_usd": 0.12
        }

        comprehensive_result = evaluate_comprehensive(
            context_rubric_score=context_score,
            layout_rubric_score=layout_score,
            graph_json=temp_files["graph"],
            keywords_json=temp_files["keywords"],
            golden_annotations=temp_files["golden"],
            conversation_turns=all_mock_data["turns"],
            pipeline_outputs=pipeline_outputs,
            execution_log=execution_log,
            cost_data=cost_data,
            user_rating=4.0,
            total_processing_time=4.5
        )

        comprehensive_score = comprehensive_result["comprehensive_rubric_score"]
        print(f"  ✓ Comprehensive Score: {comprehensive_score:.3f}")
        print(f"  ✓ Metrics: {len(comprehensive_result['metrics'])}")

        # Aggregate results
        print("\n" + "="*60)
        print("FINAL EVALUATION SUMMARY")
        print("="*60)
        print(f"Context Rubric Score:        {context_score:.3f} (10 metrics)")
        print(f"Layout Rubric Score:         {layout_score:.3f} (10 metrics)")
        print(f"Comprehensive Rubric Score:  {comprehensive_score:.3f} (10 metrics)")
        print(f"\nTotal Metrics Evaluated:     30")

        # Calculate overall score (weighted average)
        overall_score = (
            0.33 * context_score +
            0.33 * layout_score +
            0.34 * comprehensive_score
        )

        print(f"Overall System Score:        {overall_score:.3f}")
        print("="*60)

        # Create final report
        final_report = {
            "evaluation_summary": {
                "overall_score": overall_score,
                "rubric_scores": {
                    "context": context_score,
                    "layout": layout_score,
                    "comprehensive": comprehensive_score
                },
                "total_metrics": 30,
                "status": "success"
            },
            "detailed_results": {
                "context_rubric": context_result,
                "layout_rubric": layout_result,
                "comprehensive_rubric": comprehensive_result
            }
        }

        # Verify final report structure
        assert "evaluation_summary" in final_report
        assert "detailed_results" in final_report
        assert final_report["evaluation_summary"]["total_metrics"] == 30
        assert_metric_in_range(overall_score)

        # Save report to temp file
        report_file = Path(temp_files["context"]).parent / "evaluation_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Evaluation report saved to: {report_file}")
        print("✓ All integration tests passed!")

        return final_report


class TestRubricConsistency:
    """Test consistency between rubrics."""

    def test_score_consistency(self, temp_files, all_mock_data):
        """Test that rubric scores are consistent and reasonable."""
        # Run all evaluations
        context_result = evaluate_context(
            context_json=temp_files["context"],
            embeddings_npy=temp_files["embeddings"],
            session_split_json=temp_files["session_split"],
            golden_annotations=temp_files["golden"],
            processing_time=1.5
        )

        layout_result = evaluate_layout(
            graph_json=temp_files["graph"],
            golden_annotations=temp_files["golden"],
            render_time=0.8
        )

        # Verify scores are in reasonable range
        assert 0.0 <= context_result["context_rubric_score"] <= 1.0
        assert 0.0 <= layout_result["layout_rubric_score"] <= 1.0

        # Scores should not be identical (different rubrics)
        # Unless the system is perfect or terrible
        if 0.1 < context_result["context_rubric_score"] < 0.9:
            assert abs(context_result["context_rubric_score"] -
                      layout_result["layout_rubric_score"]) > 0.01

        print("\n✓ Rubric Consistency Test Passed")


class TestErrorHandling:
    """Test error handling in evaluation pipeline."""

    def test_missing_files(self):
        """Test handling of missing input files."""
        with pytest.raises(Exception):
            evaluate_context(
                context_json="/nonexistent/file.json",
                embeddings_npy="/nonexistent/embeddings.npy",
                session_split_json="/nonexistent/sessions.json",
                golden_annotations={},
                processing_time=1.0
            )

    def test_invalid_data(self, temp_files):
        """Test handling of invalid data."""
        # Create invalid context file
        invalid_file = Path(temp_files["context"]).parent / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("{invalid json")

        with pytest.raises(Exception):
            evaluate_context(
                context_json=str(invalid_file),
                embeddings_npy=temp_files["embeddings"],
                session_split_json=temp_files["session_split"],
                golden_annotations=temp_files["golden"],
                processing_time=1.0
            )

    def test_empty_golden_annotations(self, temp_files):
        """Test handling of empty golden annotations."""
        # Should not crash, but may return lower scores
        result = evaluate_context(
            context_json=temp_files["context"],
            embeddings_npy=temp_files["embeddings"],
            session_split_json=temp_files["session_split"],
            golden_annotations={},  # Empty
            processing_time=1.0
        )

        # Should still return valid structure
        assert "context_rubric_score" in result
        assert "metrics" in result


class TestWeightCustomization:
    """Test custom weight configurations."""

    def test_custom_context_weights(self, temp_files):
        """Test context rubric with custom weights."""
        custom_weights = {
            "main_path_coherence": 0.8,
            "branch_detection_recall": 0.2
        }

        result = evaluate_context(
            context_json=temp_files["context"],
            embeddings_npy=temp_files["embeddings"],
            session_split_json=temp_files["session_split"],
            golden_annotations=temp_files["golden"],
            processing_time=1.0,
            weights=custom_weights
        )

        assert "context_rubric_score" in result
        assert_metric_in_range(result["context_rubric_score"])

        print("\n✓ Custom Weights Test Passed")

    def test_extreme_weights(self, temp_files):
        """Test rubric with extreme weights (all weight on one metric)."""
        extreme_weights = {
            "main_path_coherence": 1.0
            # All other metrics have 0 weight
        }

        result = evaluate_context(
            context_json=temp_files["context"],
            embeddings_npy=temp_files["embeddings"],
            session_split_json=temp_files["session_split"],
            golden_annotations=temp_files["golden"],
            processing_time=1.0,
            weights=extreme_weights
        )

        # Score should be dominated by single metric
        assert "context_rubric_score" in result


if __name__ == "__main__":
    # Run with verbose output
    pytest.main([__file__, "-v", "-s"])
