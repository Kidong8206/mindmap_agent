"""
Unit tests for Context Rubric evaluation (10 metrics).

Tests all context-related evaluation metrics to ensure they:
1. Return values in expected ranges
2. Handle edge cases properly
3. Correctly compare against golden annotations
"""

import json
import tempfile
from pathlib import Path
import pytest
import numpy as np

# Import evaluation functions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.evaluate.evaluate_context import (
    calculate_main_path_coherence,
    calculate_branch_detection_recall,
    calculate_side_main_connection_accuracy,
    calculate_session_boundary_f1,
    calculate_summary_path_consistency,
    calculate_topic_transition_stability_metric,
    calculate_edge_direction_error_rate,
    calculate_duplicate_branch_rate,
    calculate_latency,
    calculate_parsing_stability,
    evaluate_context
)

from test_utils import (
    load_mock_context,
    load_mock_golden_annotations,
    load_mock_embeddings,
    load_mock_session_split,
    save_temp_json,
    save_temp_embeddings,
    assert_metric_in_range
)


@pytest.fixture
def mock_context_data():
    """Load mock context data."""
    return load_mock_context()


@pytest.fixture
def mock_golden_data():
    """Load mock golden annotations."""
    return load_mock_golden_annotations()


@pytest.fixture
def mock_embeddings_array():
    """Load mock embeddings as numpy array."""
    return load_mock_embeddings()


@pytest.fixture
def mock_session_split_data():
    """Load mock session split data."""
    return load_mock_session_split()


@pytest.fixture
def temp_context_file(mock_context_data):
    """Create temporary context JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(mock_context_data, f, ensure_ascii=False)
        return f.name


@pytest.fixture
def temp_embeddings_file(mock_embeddings_array):
    """Create temporary embeddings NPY file."""
    with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as f:
        np.save(f.name, mock_embeddings_array)
        return f.name


@pytest.fixture
def temp_session_file(mock_session_split_data):
    """Create temporary session split JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(mock_session_split_data, f, ensure_ascii=False)
        return f.name


class TestMainPathCoherence:
    """Test calculate_main_path_coherence metric."""

    def test_coherence_basic(self, mock_context_data, mock_embeddings_array):
        """Test basic coherence calculation."""
        result = calculate_main_path_coherence(mock_context_data, mock_embeddings_array)

        assert "main_path_coherence" in result
        assert "coherence_per_session" in result

        assert_metric_in_range(result["main_path_coherence"])

    def test_coherence_per_session(self, mock_context_data, mock_embeddings_array):
        """Test that coherence is calculated per session."""
        result = calculate_main_path_coherence(mock_context_data, mock_embeddings_array)

        coherence_scores = result["coherence_per_session"]
        assert len(coherence_scores) == 2  # Mock data has 2 sessions

        for score in coherence_scores:
            assert_metric_in_range(score)

    def test_empty_main_path(self, mock_embeddings_array):
        """Test handling of empty main path."""
        empty_context = {
            "contexts": [
                {
                    "session_num": 0,
                    "main_path": {"turns": []},
                    "side_paths": []
                }
            ]
        }

        result = calculate_main_path_coherence(empty_context, mock_embeddings_array)
        # Should handle gracefully, returning 0.0 or default value
        assert result["main_path_coherence"] >= 0.0


class TestBranchDetection:
    """Test calculate_branch_detection_recall metric."""

    def test_branch_detection_basic(self, mock_context_data, mock_golden_data):
        """Test basic branch detection recall."""
        result = calculate_branch_detection_recall(mock_context_data, mock_golden_data)

        assert "recall" in result
        assert "precision" in result
        assert "f1" in result

        assert_metric_in_range(result["recall"])
        assert_metric_in_range(result["precision"])
        assert_metric_in_range(result["f1"])

    def test_perfect_branch_detection(self, mock_golden_data):
        """Test perfect branch detection (all branches found)."""
        # Use golden data as predictions for perfect match
        context_with_all_branches = {
            "contexts": [
                {
                    "session_num": 1,
                    "main_path": {"turns": [6, 7, 8, 9]},
                    "side_paths": mock_golden_data["true_side_branches"]
                }
            ]
        }

        result = calculate_branch_detection_recall(context_with_all_branches, mock_golden_data)

        # Should be close to perfect
        assert result["recall"] >= 0.9
        assert result["f1"] >= 0.9

    def test_no_branches_detected(self, mock_golden_data):
        """Test when no branches are detected."""
        context_no_branches = {
            "contexts": [
                {
                    "session_num": 0,
                    "main_path": {"turns": [0, 1, 2, 3]},
                    "side_paths": []
                }
            ]
        }

        result = calculate_branch_detection_recall(context_no_branches, mock_golden_data)

        assert result["recall"] < 1.0  # Can't have perfect recall if branches exist
        assert result["f1"] < 1.0


class TestSideMainConnection:
    """Test calculate_side_main_connection_accuracy metric."""

    def test_connection_accuracy_basic(self, mock_context_data, mock_golden_data):
        """Test basic connection accuracy."""
        result = calculate_side_main_connection_accuracy(mock_context_data, mock_golden_data)

        assert "connection_accuracy" in result
        assert "total_branches" in result

        assert_metric_in_range(result["connection_accuracy"])

    def test_perfect_connections(self, mock_golden_data):
        """Test perfect branch-main connections."""
        # Exact match with golden data
        perfect_context = {
            "contexts": [
                {
                    "session_num": 1,
                    "main_path": {"turns": [6, 7, 8, 9]},
                    "side_paths": [
                        {
                            "path_id": "side_1_1",
                            "turns": [4, 5],
                            "branch_from_turn": 3,
                            "rejoin_turn": 6
                        }
                    ]
                }
            ]
        }

        result = calculate_side_main_connection_accuracy(perfect_context, mock_golden_data)

        assert result["connection_accuracy"] >= 0.9


class TestSessionBoundary:
    """Test calculate_session_boundary_f1 metric."""

    def test_session_boundary_basic(self, mock_session_split_data, mock_golden_data):
        """Test basic session boundary F1."""
        result = calculate_session_boundary_f1(mock_session_split_data, mock_golden_data)

        assert "boundary_f1" in result
        assert "precision" in result
        assert "recall" in result

        assert_metric_in_range(result["boundary_f1"])

    def test_perfect_boundaries(self, mock_golden_data):
        """Test perfect session boundary detection."""
        perfect_sessions = {
            "sessions": [
                {"session_num": 0, "turn_range": [0, 3]},
                {"session_num": 1, "turn_range": [4, 5]},
                {"session_num": 2, "turn_range": [6, 9]}
            ]
        }

        result = calculate_session_boundary_f1(perfect_sessions, mock_golden_data)

        # Should achieve high F1
        assert result["boundary_f1"] >= 0.8

    def test_no_boundaries(self, mock_golden_data):
        """Test when no boundaries are detected (single session)."""
        single_session = {
            "sessions": [
                {"session_num": 0, "turn_range": [0, 9]}
            ]
        }

        result = calculate_session_boundary_f1(single_session, mock_golden_data)

        # Low recall since boundaries exist
        assert result["recall"] < 0.5


class TestSummaryPathConsistency:
    """Test calculate_summary_path_consistency metric."""

    def test_summary_consistency_basic(self, mock_context_data, mock_golden_data):
        """Test basic summary-path consistency."""
        result = calculate_summary_path_consistency(mock_context_data, mock_golden_data)

        assert "keyword_coverage" in result
        assert "avg_coverage" in result

        assert_metric_in_range(result["avg_coverage"])

    def test_high_keyword_coverage(self, mock_golden_data):
        """Test high keyword coverage scenario."""
        context_with_keywords = {
            "contexts": [
                {
                    "session_num": 0,
                    "main_path": {
                        "keywords": ["React Hook", "useState", "함수형 컴포넌트"]
                    },
                    "side_paths": []
                },
                {
                    "session_num": 1,
                    "main_path": {
                        "keywords": ["useEffect", "API 호출"]
                    },
                    "side_paths": [
                        {
                            "keywords": ["클래스 컴포넌트", "this.state"]
                        }
                    ]
                }
            ]
        }

        result = calculate_summary_path_consistency(context_with_keywords, mock_golden_data)

        # Should have decent coverage
        assert result["avg_coverage"] >= 0.5


class TestTopicTransitionStability:
    """Test calculate_topic_transition_stability_metric metric."""

    def test_transition_stability_basic(self, mock_context_data, mock_embeddings_array):
        """Test basic transition stability."""
        result = calculate_topic_transition_stability_metric(
            mock_context_data,
            mock_embeddings_array
        )

        assert "transition_stability" in result
        assert "avg_transition_similarity" in result

        assert_metric_in_range(result["transition_stability"])

    def test_single_session(self, mock_embeddings_array):
        """Test with single session (no transitions)."""
        single_session_context = {
            "contexts": [
                {
                    "session_num": 0,
                    "main_path": {"turns": [0, 1, 2, 3]},
                    "side_paths": []
                }
            ]
        }

        result = calculate_topic_transition_stability_metric(
            single_session_context,
            mock_embeddings_array
        )

        # No transitions, should return default
        assert result["transition_stability"] >= 0.0


class TestEdgeDirectionError:
    """Test calculate_edge_direction_error_rate metric."""

    def test_edge_direction_basic(self, mock_context_data):
        """Test basic edge direction error rate."""
        result = calculate_edge_direction_error_rate(mock_context_data)

        assert "error_rate" in result
        assert "total_edges" in result

        assert_metric_in_range(result["error_rate"])

    def test_all_forward_edges(self):
        """Test graph with all forward edges (no errors)."""
        good_context = {
            "contexts": [
                {
                    "session_num": 0,
                    "main_path": {"turns": [0, 1, 2, 3]},  # Forward
                    "side_paths": [
                        {
                            "turns": [4, 5],
                            "branch_from_turn": 3,
                            "rejoin_turn": 6  # Forward rejoin
                        }
                    ]
                }
            ]
        }

        result = calculate_edge_direction_error_rate(good_context)

        assert result["error_rate"] <= 0.1  # Should be low

    def test_backward_edges(self):
        """Test graph with backward edges (errors)."""
        bad_context = {
            "contexts": [
                {
                    "session_num": 0,
                    "main_path": {"turns": [0, 3, 1, 2]},  # Backward jump 3→1
                    "side_paths": []
                }
            ]
        }

        result = calculate_edge_direction_error_rate(bad_context)

        assert result["error_rate"] > 0.0  # Should detect errors


class TestDuplicateBranch:
    """Test calculate_duplicate_branch_rate metric."""

    def test_duplicate_branch_basic(self, mock_context_data):
        """Test basic duplicate branch detection."""
        result = calculate_duplicate_branch_rate(mock_context_data)

        assert "duplicate_rate" in result
        assert "total_branches" in result

        assert_metric_in_range(result["duplicate_rate"])

    def test_no_duplicates(self):
        """Test when no duplicate branches exist."""
        unique_branches = {
            "contexts": [
                {
                    "session_num": 0,
                    "main_path": {"turns": [0, 1, 2]},
                    "side_paths": [
                        {"turns": [3, 4], "topic": "Topic A"},
                        {"turns": [5, 6], "topic": "Topic B"}
                    ]
                }
            ]
        }

        result = calculate_duplicate_branch_rate(unique_branches)

        assert result["duplicate_rate"] == 0.0

    def test_with_duplicates(self):
        """Test when duplicate branches exist."""
        duplicate_branches = {
            "contexts": [
                {
                    "session_num": 0,
                    "main_path": {"turns": [0, 1, 2]},
                    "side_paths": [
                        {"turns": [3, 4], "topic": "Same Topic"},
                        {"turns": [5, 6], "topic": "Same Topic"},
                        {"turns": [7, 8], "topic": "Different Topic"}
                    ]
                }
            ]
        }

        result = calculate_duplicate_branch_rate(duplicate_branches)

        # Should detect duplicates
        assert result["duplicate_rate"] > 0.0


class TestLatency:
    """Test calculate_latency metric."""

    def test_latency_basic(self):
        """Test basic latency calculation."""
        processing_time = 1.5  # 1.5 seconds

        result = calculate_latency(processing_time)

        assert "latency_seconds" in result
        assert "latency_score" in result

        assert result["latency_seconds"] == processing_time
        assert_metric_in_range(result["latency_score"])

    def test_fast_processing(self):
        """Test fast processing (high score)."""
        fast_time = 0.5

        result = calculate_latency(fast_time)

        assert result["latency_score"] >= 0.8

    def test_slow_processing(self):
        """Test slow processing (low score)."""
        slow_time = 10.0

        result = calculate_latency(slow_time)

        assert result["latency_score"] <= 0.5


class TestParsingStability:
    """Test calculate_parsing_stability metric."""

    def test_parsing_valid_json(self, temp_context_file):
        """Test parsing valid JSON file."""
        result = calculate_parsing_stability(temp_context_file)

        assert "is_valid" in result
        assert "has_required_fields" in result
        assert "stability_score" in result

        assert result["is_valid"] is True
        assert result["stability_score"] == 1.0

    def test_parsing_invalid_json(self):
        """Test parsing invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json")
            invalid_file = f.name

        result = calculate_parsing_stability(invalid_file)

        assert result["is_valid"] is False
        assert result["stability_score"] == 0.0

    def test_parsing_missing_fields(self):
        """Test parsing JSON with missing required fields."""
        incomplete_data = {"session_id": "test"}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(incomplete_data, f)
            incomplete_file = f.name

        result = calculate_parsing_stability(incomplete_file)

        assert result["has_required_fields"] is False


class TestEvaluateContextIntegration:
    """Test the main evaluate_context function."""

    def test_evaluate_context_full(
        self,
        temp_context_file,
        temp_embeddings_file,
        temp_session_file,
        mock_golden_data
    ):
        """Test full context evaluation with all metrics."""
        result = evaluate_context(
            context_json=temp_context_file,
            embeddings_npy=temp_embeddings_file,
            session_split_json=temp_session_file,
            golden_annotations=mock_golden_data,
            processing_time=1.5
        )

        # Check overall structure
        assert "context_rubric_score" in result
        assert "metrics" in result
        assert "metadata" in result

        # Check that all 10 metrics are present
        metrics = result["metrics"]
        expected_metrics = [
            "main_path_coherence",
            "branch_detection_recall",
            "side_main_connection_accuracy",
            "session_boundary_f1",
            "summary_path_consistency",
            "topic_transition_stability",
            "edge_direction_error_rate",
            "duplicate_branch_rate",
            "latency",
            "parsing_stability"
        ]

        for metric in expected_metrics:
            assert metric in metrics, f"Missing metric: {metric}"

        # Check overall score
        assert_metric_in_range(result["context_rubric_score"])

    def test_evaluate_context_custom_weights(
        self,
        temp_context_file,
        temp_embeddings_file,
        temp_session_file,
        mock_golden_data
    ):
        """Test evaluation with custom weights."""
        custom_weights = {
            "main_path_coherence": 0.5,
            "branch_detection_recall": 0.5,
            # Others default to 0
        }

        result = evaluate_context(
            context_json=temp_context_file,
            embeddings_npy=temp_embeddings_file,
            session_split_json=temp_session_file,
            golden_annotations=mock_golden_data,
            processing_time=1.0,
            weights=custom_weights
        )

        # Score should be dominated by these two metrics
        assert "context_rubric_score" in result
        assert_metric_in_range(result["context_rubric_score"])

    def test_evaluate_context_metadata(
        self,
        temp_context_file,
        temp_embeddings_file,
        temp_session_file,
        mock_golden_data
    ):
        """Test that metadata is properly included."""
        result = evaluate_context(
            context_json=temp_context_file,
            embeddings_npy=temp_embeddings_file,
            session_split_json=temp_session_file,
            golden_annotations=mock_golden_data,
            processing_time=2.0
        )

        metadata = result["metadata"]
        assert "processing_time" in metadata
        assert "num_metrics" in metadata
        assert "timestamp" in metadata

        assert metadata["processing_time"] == 2.0
        assert metadata["num_metrics"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
