"""
Test utilities for loading mock fixtures and helper functions.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_mock_turns() -> List[Dict[str, Any]]:
    """Load mock conversation turns from JSONL."""
    with open(FIXTURES_DIR / "mock_turns.jsonl", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def load_mock_session_split() -> Dict[str, Any]:
    """Load mock session split data."""
    with open(FIXTURES_DIR / "mock_session_split.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_mock_context() -> Dict[str, Any]:
    """Load mock context analysis data."""
    with open(FIXTURES_DIR / "mock_context.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_mock_keywords() -> Dict[str, Any]:
    """Load mock keyword extraction data."""
    with open(FIXTURES_DIR / "mock_keywords.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_mock_graph() -> Dict[str, Any]:
    """Load mock graph layout data."""
    with open(FIXTURES_DIR / "mock_graph.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_mock_golden_annotations() -> Dict[str, Any]:
    """Load mock golden annotations."""
    with open(FIXTURES_DIR / "mock_golden_annotations.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_mock_embeddings() -> np.ndarray:
    """
    Load mock embeddings from JSON format.

    Returns:
        np.ndarray: Shape (num_turns, embedding_dim)
    """
    with open(FIXTURES_DIR / "mock_embeddings.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    embeddings = np.array(data["embeddings"], dtype=np.float32)

    # Normalize to unit vectors (as would be done with real embeddings)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / (norms + 1e-8)

    return embeddings


def save_temp_json(data: Dict[str, Any], filename: str) -> Path:
    """
    Save temporary JSON file for testing.

    Args:
        data: Data to save
        filename: Filename (will be saved in fixtures directory)

    Returns:
        Path to saved file
    """
    filepath = FIXTURES_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath


def save_temp_embeddings(embeddings: np.ndarray, filename: str) -> Path:
    """
    Save temporary embeddings file for testing.

    Args:
        embeddings: Embeddings array
        filename: Filename (will be saved in fixtures directory)

    Returns:
        Path to saved file
    """
    filepath = FIXTURES_DIR / filename
    np.save(filepath, embeddings)
    return filepath


def assert_metric_in_range(metric_value: float, min_val: float = 0.0, max_val: float = 1.0):
    """
    Assert that a metric value is within expected range.

    Args:
        metric_value: The metric value to check
        min_val: Minimum expected value
        max_val: Maximum expected value

    Raises:
        AssertionError: If value is out of range
    """
    assert min_val <= metric_value <= max_val, \
        f"Metric value {metric_value} out of range [{min_val}, {max_val}]"


def assert_all_metrics_present(result: Dict[str, Any], expected_keys: List[str]):
    """
    Assert that all expected metric keys are present in result.

    Args:
        result: Result dictionary from evaluation function
        expected_keys: List of expected keys

    Raises:
        AssertionError: If any key is missing
    """
    for key in expected_keys:
        assert key in result, f"Missing expected key: {key}"


def create_minimal_graph(num_nodes: int = 3) -> Dict[str, Any]:
    """
    Create a minimal graph structure for testing.

    Args:
        num_nodes: Number of nodes to create

    Returns:
        Graph dictionary
    """
    nodes = []
    edges = []

    for i in range(num_nodes):
        nodes.append({
            "id": f"node_{i}",
            "label": f"Node {i}",
            "type": "root" if i == 0 else "main",
            "depth": i,
            "x": 100 * i,
            "y": 100 * i,
            "size": 20,
            "color": "#3498db"
        })

        if i > 0:
            edges.append({
                "id": f"edge_{i-1}_{i}",
                "source": f"node_{i-1}",
                "target": f"node_{i}",
                "type": "main",
                "weight": 0.8
            })

    return {
        "nodes": nodes,
        "edges": edges,
        "layout": {"type": "hierarchical", "width": 1000, "height": 600}
    }
