"""
Unit tests for Layout Rubric evaluation (10 metrics).

Tests all layout-related evaluation metrics to ensure they:
1. Return values in expected ranges
2. Handle edge cases properly
3. Correctly evaluate visual quality
"""

import json
import tempfile
from pathlib import Path
import pytest

# Import evaluation functions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.evaluate.evaluate_layout import (
    calculate_depth_balance,
    calculate_branching_balance_metric,
    calculate_edge_crossing_minimization,
    calculate_centrality_distribution_balance,
    calculate_cluster_cohesion_metric,
    calculate_edge_length_variance_metric,
    calculate_label_readability,
    calculate_node_density_metric,
    calculate_color_contrast,
    calculate_interaction_responsiveness,
    evaluate_layout
)

from test_utils import (
    load_mock_graph,
    load_mock_golden_annotations,
    assert_metric_in_range,
    create_minimal_graph
)


@pytest.fixture
def mock_graph_data():
    """Load mock graph data."""
    return load_mock_graph()


@pytest.fixture
def mock_golden_data():
    """Load mock golden annotations."""
    return load_mock_golden_annotations()


@pytest.fixture
def temp_graph_file(mock_graph_data):
    """Create temporary graph JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(mock_graph_data, f, ensure_ascii=False)
        return f.name


class TestDepthBalance:
    """Test calculate_depth_balance metric."""

    def test_depth_balance_basic(self, mock_graph_data):
        """Test basic depth balance calculation."""
        result = calculate_depth_balance(mock_graph_data)

        assert "depth_entropy" in result
        assert "balance_score" in result
        assert "depth_distribution" in result

        assert_metric_in_range(result["balance_score"])
        assert result["depth_entropy"] >= 0.0

    def test_perfect_balance(self):
        """Test perfectly balanced tree (all nodes at same depth)."""
        balanced_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "depth": 0},
                    {"id": "1", "depth": 1},
                    {"id": "2", "depth": 1},
                    {"id": "3", "depth": 1}
                ],
                "edges": []
            }
        }

        result = calculate_depth_balance(balanced_graph)

        # High entropy = good balance
        assert result["balance_score"] >= 0.7

    def test_imbalanced_depth(self):
        """Test imbalanced tree (skewed depths)."""
        imbalanced_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "depth": 0},
                    {"id": "1", "depth": 1},
                    {"id": "2", "depth": 5},
                    {"id": "3", "depth": 5}
                ],
                "edges": []
            }
        }

        result = calculate_depth_balance(imbalanced_graph)

        # Lower entropy for imbalanced
        assert result["balance_score"] < 1.0


class TestBranchingBalance:
    """Test calculate_branching_balance_metric metric."""

    def test_branching_balance_basic(self, mock_graph_data):
        """Test basic branching balance calculation."""
        result = calculate_branching_balance_metric(mock_graph_data)

        assert "branching_variance" in result
        assert "balance_score" in result
        assert "branching_per_node" in result

        assert_metric_in_range(result["balance_score"])
        assert result["branching_variance"] >= 0.0

    def test_uniform_branching(self):
        """Test graph with uniform branching."""
        uniform_graph = {
            "graph": {
                "nodes": [
                    {"id": "0"},
                    {"id": "1"},
                    {"id": "2"},
                    {"id": "3"},
                    {"id": "4"},
                    {"id": "5"}
                ],
                "edges": [
                    {"source": "0", "target": "1"},
                    {"source": "0", "target": "2"},
                    {"source": "1", "target": "3"},
                    {"source": "1", "target": "4"},
                    {"source": "2", "target": "5"}
                ]
            }
        }

        result = calculate_branching_balance_metric(uniform_graph)

        # Low variance = good balance
        assert result["balance_score"] >= 0.6

    def test_star_topology(self):
        """Test star topology (one node connects to all)."""
        star_graph = {
            "graph": {
                "nodes": [{"id": str(i)} for i in range(6)],
                "edges": [
                    {"source": "0", "target": str(i)} for i in range(1, 6)
                ]
            }
        }

        result = calculate_branching_balance_metric(star_graph)

        # High variance for star topology
        assert result["branching_variance"] > 0.0


class TestEdgeCrossing:
    """Test calculate_edge_crossing_minimization metric."""

    def test_edge_crossing_basic(self, mock_graph_data):
        """Test basic edge crossing calculation."""
        result = calculate_edge_crossing_minimization(mock_graph_data)

        assert "num_crossings" in result
        assert "crossing_score" in result

        assert_metric_in_range(result["crossing_score"])
        assert result["num_crossings"] >= 0

    def test_no_crossings(self):
        """Test graph with no edge crossings."""
        no_crossing_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "x": 0, "y": 0},
                    {"id": "1", "x": 100, "y": 0},
                    {"id": "2", "x": 0, "y": 100}
                ],
                "edges": [
                    {"source": "0", "target": "1"},
                    {"source": "0", "target": "2"}
                ]
            }
        }

        result = calculate_edge_crossing_minimization(no_crossing_graph)

        assert result["num_crossings"] == 0
        assert result["crossing_score"] == 1.0

    def test_with_crossings(self):
        """Test graph with edge crossings."""
        crossing_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "x": 0, "y": 0},
                    {"id": "1", "x": 100, "y": 100},
                    {"id": "2", "x": 0, "y": 100},
                    {"id": "3", "x": 100, "y": 0}
                ],
                "edges": [
                    {"source": "0", "target": "1"},  # Diagonal
                    {"source": "2", "target": "3"}   # Crossing diagonal
                ]
            }
        }

        result = calculate_edge_crossing_minimization(crossing_graph)

        # Should detect crossing
        assert result["num_crossings"] >= 1
        assert result["crossing_score"] < 1.0


class TestCentralityDistribution:
    """Test calculate_centrality_distribution_balance metric."""

    def test_centrality_basic(self, mock_graph_data):
        """Test basic centrality distribution calculation."""
        result = calculate_centrality_distribution_balance(mock_graph_data)

        assert "centrality_variance" in result
        assert "balance_score" in result
        assert "pagerank_scores" in result

        assert_metric_in_range(result["balance_score"])

    def test_balanced_centrality(self):
        """Test graph with balanced centrality."""
        # Cycle graph - all nodes have equal centrality
        cycle_graph = {
            "graph": {
                "nodes": [{"id": str(i)} for i in range(4)],
                "edges": [
                    {"source": "0", "target": "1"},
                    {"source": "1", "target": "2"},
                    {"source": "2", "target": "3"},
                    {"source": "3", "target": "0"}
                ]
            }
        }

        result = calculate_centrality_distribution_balance(cycle_graph)

        # Should have low variance
        assert result["balance_score"] >= 0.7

    def test_hub_topology(self):
        """Test graph with hub (high centrality variance)."""
        hub_graph = {
            "graph": {
                "nodes": [{"id": str(i)} for i in range(5)],
                "edges": [
                    {"source": "0", "target": str(i)} for i in range(1, 5)
                ]
            }
        }

        result = calculate_centrality_distribution_balance(hub_graph)

        # Hub has high centrality variance
        assert result["centrality_variance"] > 0.0


class TestClusterCohesion:
    """Test calculate_cluster_cohesion_metric metric."""

    def test_cluster_cohesion_basic(self, mock_graph_data):
        """Test basic cluster cohesion calculation."""
        result = calculate_cluster_cohesion_metric(mock_graph_data)

        assert "modularity" in result
        assert "cohesion_score" in result

        assert_metric_in_range(result["cohesion_score"])

    def test_well_defined_clusters(self):
        """Test graph with well-defined clusters."""
        clustered_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "path_id": "main_0"},
                    {"id": "1", "path_id": "main_0"},
                    {"id": "2", "path_id": "side_1"},
                    {"id": "3", "path_id": "side_1"}
                ],
                "edges": [
                    {"source": "0", "target": "1"},  # Within cluster
                    {"source": "2", "target": "3"},  # Within cluster
                    {"source": "0", "target": "2"}   # Between clusters
                ]
            }
        }

        result = calculate_cluster_cohesion_metric(clustered_graph)

        # Good clustering = positive modularity
        assert result["modularity"] >= 0.0

    def test_no_clustering(self):
        """Test fully connected graph (no clear clusters)."""
        complete_graph = {
            "graph": {
                "nodes": [{"id": str(i)} for i in range(4)],
                "edges": [
                    {"source": str(i), "target": str(j)}
                    for i in range(4) for j in range(i+1, 4)
                ]
            }
        }

        result = calculate_cluster_cohesion_metric(complete_graph)

        # Complete graph has low modularity
        assert result["modularity"] <= 0.5


class TestEdgeLengthVariance:
    """Test calculate_edge_length_variance_metric metric."""

    def test_edge_length_basic(self, mock_graph_data):
        """Test basic edge length variance calculation."""
        result = calculate_edge_length_variance_metric(mock_graph_data)

        assert "length_variance" in result
        assert "uniformity_score" in result
        assert "edge_lengths" in result

        assert_metric_in_range(result["uniformity_score"])

    def test_uniform_edge_lengths(self):
        """Test graph with uniform edge lengths."""
        uniform_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "x": 0, "y": 0},
                    {"id": "1", "x": 100, "y": 0},
                    {"id": "2", "x": 0, "y": 100},
                    {"id": "3", "x": 100, "y": 100}
                ],
                "edges": [
                    {"source": "0", "target": "1"},
                    {"source": "2", "target": "3"}
                ]
            }
        }

        result = calculate_edge_length_variance_metric(uniform_graph)

        # Should have low variance
        assert result["uniformity_score"] >= 0.8

    def test_variable_edge_lengths(self):
        """Test graph with variable edge lengths."""
        variable_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "x": 0, "y": 0},
                    {"id": "1", "x": 10, "y": 0},
                    {"id": "2", "x": 500, "y": 0}
                ],
                "edges": [
                    {"source": "0", "target": "1"},  # Short
                    {"source": "0", "target": "2"}   # Long
                ]
            }
        }

        result = calculate_edge_length_variance_metric(variable_graph)

        # High variance
        assert result["length_variance"] > 0.0
        assert result["uniformity_score"] < 0.8


class TestLabelReadability:
    """Test calculate_label_readability metric."""

    def test_label_readability_basic(self, mock_graph_data):
        """Test basic label readability calculation."""
        result = calculate_label_readability(mock_graph_data)

        assert "num_overlaps" in result
        assert "readability_score" in result

        assert_metric_in_range(result["readability_score"])

    def test_no_overlaps(self):
        """Test graph with no label overlaps."""
        spaced_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "x": 0, "y": 0, "label": "A", "size": 10},
                    {"id": "1", "x": 200, "y": 0, "label": "B", "size": 10},
                    {"id": "2", "x": 0, "y": 200, "label": "C", "size": 10}
                ],
                "edges": []
            }
        }

        result = calculate_label_readability(spaced_graph)

        assert result["num_overlaps"] == 0
        assert result["readability_score"] == 1.0

    def test_with_overlaps(self):
        """Test graph with overlapping labels."""
        overlapping_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "x": 0, "y": 0, "label": "Long Label A", "size": 30},
                    {"id": "1", "x": 10, "y": 10, "label": "Long Label B", "size": 30}
                ],
                "edges": []
            }
        }

        result = calculate_label_readability(overlapping_graph)

        # Should detect overlaps
        assert result["num_overlaps"] >= 1
        assert result["readability_score"] < 1.0


class TestNodeDensity:
    """Test calculate_node_density_metric metric."""

    def test_node_density_basic(self, mock_graph_data):
        """Test basic node density calculation."""
        result = calculate_node_density_metric(mock_graph_data)

        assert "density" in result
        assert "density_score" in result
        assert "canvas_area" in result

        assert_metric_in_range(result["density_score"])

    def test_optimal_density(self):
        """Test graph with optimal node density."""
        optimal_graph = {
            "graph": {
                "nodes": [
                    {"id": str(i), "x": i * 150, "y": 100, "size": 20}
                    for i in range(5)
                ],
                "edges": [],
                "layout": {"width": 1000, "height": 600}
            }
        }

        result = calculate_node_density_metric(optimal_graph)

        # Should be close to optimal
        assert result["density_score"] >= 0.6

    def test_too_dense(self):
        """Test graph with too many nodes (overcrowded)."""
        dense_graph = {
            "graph": {
                "nodes": [
                    {"id": str(i), "x": (i % 10) * 50, "y": (i // 10) * 50, "size": 40}
                    for i in range(100)
                ],
                "edges": [],
                "layout": {"width": 500, "height": 500}
            }
        }

        result = calculate_node_density_metric(dense_graph)

        # Too dense
        assert result["density"] > 0.5
        assert result["density_score"] < 0.7

    def test_too_sparse(self):
        """Test graph with too few nodes (too sparse)."""
        sparse_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "x": 0, "y": 0, "size": 10},
                    {"id": "1", "x": 1000, "y": 1000, "size": 10}
                ],
                "edges": [],
                "layout": {"width": 2000, "height": 2000}
            }
        }

        result = calculate_node_density_metric(sparse_graph)

        # Too sparse
        assert result["density"] < 0.01
        assert result["density_score"] < 0.7


class TestColorContrast:
    """Test calculate_color_contrast metric."""

    def test_color_contrast_basic(self, mock_graph_data):
        """Test basic color contrast calculation."""
        result = calculate_color_contrast(mock_graph_data)

        assert "min_contrast" in result
        assert "avg_contrast" in result
        assert "contrast_score" in result

        assert_metric_in_range(result["contrast_score"])

    def test_high_contrast(self):
        """Test graph with high color contrast."""
        high_contrast_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "color": "#000000", "type": "root"},
                    {"id": "1", "color": "#FFFFFF", "type": "main"},
                    {"id": "2", "color": "#FF0000", "type": "side"}
                ],
                "edges": []
            }
        }

        result = calculate_color_contrast(high_contrast_graph)

        # High contrast = high score
        assert result["contrast_score"] >= 0.7

    def test_low_contrast(self):
        """Test graph with low color contrast."""
        low_contrast_graph = {
            "graph": {
                "nodes": [
                    {"id": "0", "color": "#AAAAAA", "type": "root"},
                    {"id": "1", "color": "#AAAAAB", "type": "main"},
                    {"id": "2", "color": "#AAAAAC", "type": "main"}
                ],
                "edges": []
            }
        }

        result = calculate_color_contrast(low_contrast_graph)

        # Low contrast = low score
        assert result["min_contrast"] < 10.0
        assert result["contrast_score"] < 0.7

    def test_monochrome(self):
        """Test graph with same color (no contrast)."""
        monochrome_graph = {
            "graph": {
                "nodes": [
                    {"id": str(i), "color": "#3498db"}
                    for i in range(3)
                ],
                "edges": []
            }
        }

        result = calculate_color_contrast(monochrome_graph)

        # No contrast
        assert result["min_contrast"] == 0.0


class TestInteractionResponsiveness:
    """Test calculate_interaction_responsiveness metric."""

    def test_responsiveness_basic(self):
        """Test basic responsiveness calculation."""
        render_time = 0.5

        result = calculate_interaction_responsiveness(render_time)

        assert "render_time_ms" in result
        assert "responsiveness_score" in result

        assert_metric_in_range(result["responsiveness_score"])

    def test_fast_render(self):
        """Test fast rendering (high score)."""
        fast_time = 0.1

        result = calculate_interaction_responsiveness(fast_time)

        assert result["responsiveness_score"] >= 0.8

    def test_slow_render(self):
        """Test slow rendering (low score)."""
        slow_time = 5.0

        result = calculate_interaction_responsiveness(slow_time)

        assert result["responsiveness_score"] <= 0.5


class TestEvaluateLayoutIntegration:
    """Test the main evaluate_layout function."""

    def test_evaluate_layout_full(self, temp_graph_file, mock_golden_data):
        """Test full layout evaluation with all metrics."""
        result = evaluate_layout(
            graph_json=temp_graph_file,
            golden_annotations=mock_golden_data,
            render_time=0.8
        )

        # Check overall structure
        assert "layout_rubric_score" in result
        assert "metrics" in result
        assert "metadata" in result

        # Check that all 10 metrics are present
        metrics = result["metrics"]
        expected_metrics = [
            "depth_balance",
            "branching_balance",
            "edge_crossing_minimization",
            "centrality_distribution_balance",
            "cluster_cohesion",
            "edge_length_variance",
            "label_readability",
            "node_density",
            "color_contrast",
            "interaction_responsiveness"
        ]

        for metric in expected_metrics:
            assert metric in metrics, f"Missing metric: {metric}"

        # Check overall score
        assert_metric_in_range(result["layout_rubric_score"])

    def test_evaluate_layout_custom_weights(self, temp_graph_file, mock_golden_data):
        """Test evaluation with custom weights."""
        custom_weights = {
            "depth_balance": 0.5,
            "edge_crossing_minimization": 0.5,
            # Others default to 0
        }

        result = evaluate_layout(
            graph_json=temp_graph_file,
            golden_annotations=mock_golden_data,
            render_time=1.0,
            weights=custom_weights
        )

        # Score should be dominated by these two metrics
        assert "layout_rubric_score" in result
        assert_metric_in_range(result["layout_rubric_score"])

    def test_evaluate_layout_metadata(self, temp_graph_file, mock_golden_data):
        """Test that metadata is properly included."""
        result = evaluate_layout(
            graph_json=temp_graph_file,
            golden_annotations=mock_golden_data,
            render_time=1.5
        )

        metadata = result["metadata"]
        assert "render_time" in metadata
        assert "num_metrics" in metadata
        assert "num_nodes" in metadata
        assert "num_edges" in metadata
        assert "timestamp" in metadata

        assert metadata["render_time"] == 1.5
        assert metadata["num_metrics"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
