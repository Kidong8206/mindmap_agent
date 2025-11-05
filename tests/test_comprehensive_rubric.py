"""
Unit tests for Comprehensive Rubric evaluation (10 metrics).

Tests all comprehensive evaluation metrics that combine:
- Structural quality (context + layout)
- Content coverage and relevance
- Technical quality (parsing, stability, performance)
- User preferences
"""

import json
import tempfile
from pathlib import Path
import pytest

# Import evaluation functions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.evaluate.evaluate_comprehensive import (
    calculate_structural_score_weighted_sum,
    calculate_content_coverage,
    calculate_offtopic_penalty,
    calculate_format_compliance_rate,
    calculate_parsing_success_rate,
    calculate_user_preference_alignment,
    calculate_reproducibility,
    calculate_processing_time_score,
    calculate_stability,
    calculate_api_cost_penalty,
    evaluate_comprehensive
)

from test_utils import (
    load_mock_graph,
    load_mock_keywords,
    load_mock_golden_annotations,
    load_mock_turns,
    assert_metric_in_range
)


@pytest.fixture
def mock_graph_data():
    """Load mock graph data."""
    return load_mock_graph()


@pytest.fixture
def mock_keywords_data():
    """Load mock keywords data."""
    return load_mock_keywords()


@pytest.fixture
def mock_golden_data():
    """Load mock golden annotations."""
    return load_mock_golden_annotations()


@pytest.fixture
def mock_turns_data():
    """Load mock conversation turns."""
    return load_mock_turns()


@pytest.fixture
def mock_context_score():
    """Mock context rubric score."""
    return 0.85


@pytest.fixture
def mock_layout_score():
    """Mock layout rubric score."""
    return 0.78


class TestStructuralScore:
    """Test calculate_structural_score_weighted_sum metric."""

    def test_structural_score_basic(self, mock_context_score, mock_layout_score):
        """Test basic structural score calculation."""
        result = calculate_structural_score_weighted_sum(
            context_score=mock_context_score,
            layout_score=mock_layout_score
        )

        assert "structural_score" in result
        assert "context_weight" in result
        assert "layout_weight" in result

        assert_metric_in_range(result["structural_score"])

    def test_structural_score_equal_weights(self):
        """Test structural score with equal weights."""
        result = calculate_structural_score_weighted_sum(
            context_score=0.8,
            layout_score=0.6,
            context_weight=0.5,
            layout_weight=0.5
        )

        # Should be average: (0.8 + 0.6) / 2 = 0.7
        assert abs(result["structural_score"] - 0.7) < 0.01

    def test_structural_score_context_heavy(self):
        """Test structural score with context-heavy weighting."""
        result = calculate_structural_score_weighted_sum(
            context_score=0.9,
            layout_score=0.3,
            context_weight=0.9,
            layout_weight=0.1
        )

        # Should be closer to context score
        assert result["structural_score"] > 0.8

    def test_structural_score_perfect(self):
        """Test structural score with perfect scores."""
        result = calculate_structural_score_weighted_sum(
            context_score=1.0,
            layout_score=1.0
        )

        assert result["structural_score"] == 1.0


class TestContentCoverage:
    """Test calculate_content_coverage metric."""

    def test_content_coverage_basic(self, mock_keywords_data, mock_golden_data):
        """Test basic content coverage calculation."""
        result = calculate_content_coverage(mock_keywords_data, mock_golden_data)

        assert "keyword_coverage" in result
        assert "coverage_rate" in result
        assert "matched_keywords" in result

        assert_metric_in_range(result["coverage_rate"])

    def test_perfect_coverage(self, mock_golden_data):
        """Test perfect keyword coverage."""
        perfect_keywords = {
            "keywords_by_path": [
                {
                    "path_id": "main_0",
                    "keywords": [
                        {"word": kw, "score": 0.9}
                        for kw in mock_golden_data["true_keywords"]
                    ]
                }
            ]
        }

        result = calculate_content_coverage(perfect_keywords, mock_golden_data)

        # Should achieve 100% coverage
        assert result["coverage_rate"] >= 0.95

    def test_partial_coverage(self, mock_golden_data):
        """Test partial keyword coverage."""
        partial_keywords = {
            "keywords_by_path": [
                {
                    "path_id": "main_0",
                    "keywords": [
                        {"word": "React Hook", "score": 0.9},
                        {"word": "useState", "score": 0.8}
                    ]
                }
            ]
        }

        result = calculate_content_coverage(partial_keywords, mock_golden_data)

        # Should have partial coverage
        assert 0.2 <= result["coverage_rate"] <= 0.5

    def test_no_coverage(self, mock_golden_data):
        """Test no keyword coverage."""
        no_keywords = {
            "keywords_by_path": [
                {
                    "path_id": "main_0",
                    "keywords": [
                        {"word": "Irrelevant", "score": 0.9},
                        {"word": "Random", "score": 0.8}
                    ]
                }
            ]
        }

        result = calculate_content_coverage(no_keywords, mock_golden_data)

        assert result["coverage_rate"] == 0.0


class TestOffTopicPenalty:
    """Test calculate_offtopic_penalty metric."""

    def test_offtopic_basic(self, mock_graph_data, mock_turns_data):
        """Test basic off-topic penalty calculation."""
        result = calculate_offtopic_penalty(mock_graph_data, mock_turns_data)

        assert "offtopic_nodes" in result
        assert "offtopic_rate" in result
        assert "penalty_score" in result

        assert_metric_in_range(result["penalty_score"])

    def test_no_offtopic(self, mock_turns_data):
        """Test graph with no off-topic nodes."""
        relevant_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "label": "React Hook"},
                    {"id": "1", "label": "useState"},
                    {"id": "2", "label": "useEffect"}
                ],
                "edges": []
            }
        }

        result = calculate_offtopic_penalty(relevant_graph, mock_turns_data)

        # No off-topic nodes = no penalty
        assert result["offtopic_rate"] <= 0.1
        assert result["penalty_score"] >= 0.9

    def test_with_offtopic(self, mock_turns_data):
        """Test graph with off-topic nodes."""
        offtopic_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "label": "React Hook"},
                    {"id": "1", "label": "Quantum Physics"},  # Off-topic
                    {"id": "2", "label": "Cooking Recipe"}    # Off-topic
                ],
                "edges": []
            }
        }

        result = calculate_offtopic_penalty(offtopic_graph, mock_turns_data)

        # High off-topic rate = penalty
        assert result["offtopic_rate"] >= 0.3
        assert result["penalty_score"] < 0.8


class TestFormatCompliance:
    """Test calculate_format_compliance_rate metric."""

    def test_format_compliance_basic(self):
        """Test basic format compliance calculation."""
        # All stages valid
        pipeline_outputs = {
            "stage_0_turns": {"turns": [{"turn_id": 0}]},
            "stage_1_sessions": {"sessions": [{"session_num": 0}]},
            "stage_2_context": {"contexts": []},
            "stage_3_keywords": {"keywords_by_path": []},
            "stage_4_graph": {"graph": {"nodes": [], "edges": []}}
        }

        result = calculate_format_compliance_rate(pipeline_outputs)

        assert "compliance_rate" in result
        assert "valid_stages" in result
        assert "total_stages" in result

        assert result["compliance_rate"] == 1.0

    def test_partial_compliance(self):
        """Test partial format compliance."""
        # Some stages invalid
        pipeline_outputs = {
            "stage_0_turns": {"turns": [{"turn_id": 0}]},
            "stage_1_sessions": {},  # Missing required field
            "stage_2_context": {"contexts": []},
            "stage_3_keywords": None,  # Invalid
            "stage_4_graph": {"graph": {"nodes": [], "edges": []}}
        }

        result = calculate_format_compliance_rate(pipeline_outputs)

        assert result["compliance_rate"] < 1.0
        assert result["valid_stages"] == 3

    def test_all_invalid(self):
        """Test all stages invalid."""
        pipeline_outputs = {
            "stage_0_turns": None,
            "stage_1_sessions": None,
            "stage_2_context": None,
            "stage_3_keywords": None,
            "stage_4_graph": None
        }

        result = calculate_format_compliance_rate(pipeline_outputs)

        assert result["compliance_rate"] == 0.0


class TestParsingSuccess:
    """Test calculate_parsing_success_rate metric."""

    def test_parsing_success_basic(self):
        """Test basic parsing success calculation."""
        # All stages succeeded
        execution_log = {
            "stage_0": {"status": "success"},
            "stage_1": {"status": "success"},
            "stage_2": {"status": "success"},
            "stage_3": {"status": "success"},
            "stage_4": {"status": "success"}
        }

        result = calculate_parsing_success_rate(execution_log)

        assert "success_rate" in result
        assert "successful_stages" in result
        assert "failed_stages" in result

        assert result["success_rate"] == 1.0

    def test_partial_success(self):
        """Test partial parsing success."""
        execution_log = {
            "stage_0": {"status": "success"},
            "stage_1": {"status": "success"},
            "stage_2": {"status": "failed"},
            "stage_3": {"status": "success"},
            "stage_4": {"status": "failed"}
        }

        result = calculate_parsing_success_rate(execution_log)

        assert result["success_rate"] == 0.6  # 3/5
        assert len(result["failed_stages"]) == 2

    def test_all_failed(self):
        """Test all stages failed."""
        execution_log = {
            f"stage_{i}": {"status": "failed"}
            for i in range(5)
        }

        result = calculate_parsing_success_rate(execution_log)

        assert result["success_rate"] == 0.0


class TestUserPreferenceAlignment:
    """Test calculate_user_preference_alignment metric."""

    def test_user_preference_basic(self):
        """Test basic user preference alignment."""
        user_rating = 4.5  # Out of 5

        result = calculate_user_preference_alignment(user_rating, max_rating=5.0)

        assert "user_rating" in result
        assert "normalized_score" in result
        assert "alignment_score" in result

        assert_metric_in_range(result["alignment_score"])

    def test_perfect_rating(self):
        """Test perfect user rating."""
        result = calculate_user_preference_alignment(5.0, max_rating=5.0)

        assert result["normalized_score"] == 1.0
        assert result["alignment_score"] == 1.0

    def test_low_rating(self):
        """Test low user rating."""
        result = calculate_user_preference_alignment(1.0, max_rating=5.0)

        assert result["normalized_score"] == 0.2
        assert result["alignment_score"] <= 0.3

    def test_no_rating(self):
        """Test when no user rating is available."""
        result = calculate_user_preference_alignment(None)

        # Should return neutral/default score
        assert "alignment_score" in result
        assert 0.4 <= result["alignment_score"] <= 0.6


class TestReproducibility:
    """Test calculate_reproducibility metric."""

    def test_reproducibility_basic(self):
        """Test basic reproducibility calculation."""
        # Same output twice
        run_1 = {"nodes": [{"id": "0"}, {"id": "1"}], "edges": []}
        run_2 = {"nodes": [{"id": "0"}, {"id": "1"}], "edges": []}

        result = calculate_reproducibility([run_1, run_2])

        assert "reproducibility_score" in result
        assert "num_runs" in result
        assert "consistency_rate" in result

        assert result["reproducibility_score"] == 1.0

    def test_partial_reproducibility(self):
        """Test partial reproducibility."""
        run_1 = {"nodes": [{"id": "0"}, {"id": "1"}], "edges": []}
        run_2 = {"nodes": [{"id": "0"}, {"id": "2"}], "edges": []}  # Different

        result = calculate_reproducibility([run_1, run_2])

        # Not perfectly reproducible
        assert result["reproducibility_score"] < 1.0

    def test_single_run(self):
        """Test with single run (can't measure reproducibility)."""
        run_1 = {"nodes": [{"id": "0"}], "edges": []}

        result = calculate_reproducibility([run_1])

        # Should return default/neutral score
        assert "reproducibility_score" in result


class TestProcessingTimeScore:
    """Test calculate_processing_time_score metric."""

    def test_processing_time_basic(self):
        """Test basic processing time score."""
        result = calculate_processing_time_score(total_time=5.0)

        assert "total_time_seconds" in result
        assert "time_score" in result

        assert_metric_in_range(result["time_score"])

    def test_fast_processing(self):
        """Test fast processing."""
        result = calculate_processing_time_score(total_time=1.0)

        # Fast = high score
        assert result["time_score"] >= 0.8

    def test_slow_processing(self):
        """Test slow processing."""
        result = calculate_processing_time_score(total_time=30.0)

        # Slow = low score
        assert result["time_score"] <= 0.4

    def test_extremely_slow(self):
        """Test extremely slow processing."""
        result = calculate_processing_time_score(total_time=120.0)

        # Should have very low score
        assert result["time_score"] <= 0.2


class TestStability:
    """Test calculate_stability metric."""

    def test_stability_basic(self):
        """Test basic stability calculation."""
        error_log = {
            "total_attempts": 10,
            "successful": 9,
            "failed": 1,
            "errors": [{"stage": 2, "error": "Timeout"}]
        }

        result = calculate_stability(error_log)

        assert "success_rate" in result
        assert "error_rate" in result
        assert "stability_score" in result

        assert_metric_in_range(result["stability_score"])

    def test_perfect_stability(self):
        """Test perfect stability (no errors)."""
        error_log = {
            "total_attempts": 10,
            "successful": 10,
            "failed": 0,
            "errors": []
        }

        result = calculate_stability(error_log)

        assert result["error_rate"] == 0.0
        assert result["stability_score"] == 1.0

    def test_unstable(self):
        """Test unstable system (many errors)."""
        error_log = {
            "total_attempts": 10,
            "successful": 5,
            "failed": 5,
            "errors": [{"error": f"Error {i}"} for i in range(5)]
        }

        result = calculate_stability(error_log)

        assert result["error_rate"] == 0.5
        assert result["stability_score"] <= 0.6

    def test_completely_unstable(self):
        """Test completely unstable (all errors)."""
        error_log = {
            "total_attempts": 10,
            "successful": 0,
            "failed": 10,
            "errors": [{"error": f"Error {i}"} for i in range(10)]
        }

        result = calculate_stability(error_log)

        assert result["error_rate"] == 1.0
        assert result["stability_score"] == 0.0


class TestAPICostPenalty:
    """Test calculate_api_cost_penalty metric."""

    def test_api_cost_basic(self):
        """Test basic API cost penalty."""
        cost_data = {
            "total_tokens": 10000,
            "total_cost_usd": 0.15
        }

        result = calculate_api_cost_penalty(cost_data)

        assert "total_cost" in result
        assert "cost_score" in result
        assert "penalty_score" in result

        assert_metric_in_range(result["cost_score"])

    def test_low_cost(self):
        """Test low API cost (no penalty)."""
        cost_data = {
            "total_tokens": 1000,
            "total_cost_usd": 0.01
        }

        result = calculate_api_cost_penalty(cost_data)

        # Low cost = high score
        assert result["cost_score"] >= 0.9

    def test_high_cost(self):
        """Test high API cost (penalty applied)."""
        cost_data = {
            "total_tokens": 100000,
            "total_cost_usd": 1.50
        }

        result = calculate_api_cost_penalty(cost_data)

        # High cost = low score
        assert result["cost_score"] <= 0.5

    def test_extreme_cost(self):
        """Test extreme API cost."""
        cost_data = {
            "total_tokens": 1000000,
            "total_cost_usd": 10.0
        }

        result = calculate_api_cost_penalty(cost_data)

        # Should have penalty
        assert result["cost_score"] <= 0.3


class TestEvaluateComprehensiveIntegration:
    """Test the main evaluate_comprehensive function."""

    def test_evaluate_comprehensive_full(
        self,
        mock_graph_data,
        mock_keywords_data,
        mock_golden_data,
        mock_turns_data,
        mock_context_score,
        mock_layout_score
    ):
        """Test full comprehensive evaluation."""
        # Create temp files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(mock_graph_data, f, ensure_ascii=False)
            graph_file = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(mock_keywords_data, f, ensure_ascii=False)
            keywords_file = f.name

        # Mock pipeline outputs
        pipeline_outputs = {
            "stage_0_turns": {"turns": mock_turns_data},
            "stage_1_sessions": {"sessions": []},
            "stage_2_context": {"contexts": []},
            "stage_3_keywords": mock_keywords_data,
            "stage_4_graph": mock_graph_data
        }

        # Mock execution log
        execution_log = {
            f"stage_{i}": {"status": "success"} for i in range(5)
        }

        # Mock cost data
        cost_data = {"total_tokens": 5000, "total_cost_usd": 0.05}

        result = evaluate_comprehensive(
            context_rubric_score=mock_context_score,
            layout_rubric_score=mock_layout_score,
            graph_json=graph_file,
            keywords_json=keywords_file,
            golden_annotations=mock_golden_data,
            conversation_turns=mock_turns_data,
            pipeline_outputs=pipeline_outputs,
            execution_log=execution_log,
            cost_data=cost_data,
            user_rating=4.0,
            total_processing_time=3.5
        )

        # Check overall structure
        assert "comprehensive_rubric_score" in result
        assert "metrics" in result
        assert "metadata" in result

        # Check that all 10 metrics are present
        metrics = result["metrics"]
        expected_metrics = [
            "structural_score",
            "content_coverage",
            "offtopic_penalty",
            "format_compliance",
            "parsing_success",
            "user_preference_alignment",
            "reproducibility",
            "processing_time_score",
            "stability",
            "api_cost_penalty"
        ]

        for metric in expected_metrics:
            assert metric in metrics, f"Missing metric: {metric}"

        # Check overall score
        assert_metric_in_range(result["comprehensive_rubric_score"])

    def test_evaluate_comprehensive_custom_weights(
        self,
        mock_graph_data,
        mock_keywords_data,
        mock_golden_data,
        mock_turns_data,
        mock_context_score,
        mock_layout_score
    ):
        """Test comprehensive evaluation with custom weights."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(mock_graph_data, f, ensure_ascii=False)
            graph_file = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(mock_keywords_data, f, ensure_ascii=False)
            keywords_file = f.name

        custom_weights = {
            "user_preference_alignment": 0.8,
            "content_coverage": 0.2
        }

        result = evaluate_comprehensive(
            context_rubric_score=mock_context_score,
            layout_rubric_score=mock_layout_score,
            graph_json=graph_file,
            keywords_json=keywords_file,
            golden_annotations=mock_golden_data,
            conversation_turns=mock_turns_data,
            pipeline_outputs={},
            execution_log={},
            cost_data={},
            user_rating=5.0,
            total_processing_time=2.0,
            weights=custom_weights
        )

        # Score should be dominated by user preference
        assert "comprehensive_rubric_score" in result
        assert_metric_in_range(result["comprehensive_rubric_score"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
