"""
Layout Rubric Evaluation (10 metrics)

Evaluates the quality of mindmap layout and visual design.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from collections import defaultdict

from agents.utils import load_json
from .utils.graph_metrics import (
    calculate_depth_entropy,
    count_edge_crossings,
    check_node_overlaps,
    calculate_modularity,
    calculate_graph_metrics
)


# ===== Metric 1: Depth Balance =====

def calculate_depth_balance(graph_json: str, **kwargs) -> Dict[str, Any]:
    """
    Metric 1: 깊이 엔트로피

    노드 깊이 분포의 균형도 (lower entropy = better balance)

    Args:
        graph_json: Path to graph JSON

    Returns:
        Score dict
    """
    graph_data = load_json(graph_json)
    nodes = graph_data.get('graph', {}).get('nodes', [])

    entropy = calculate_depth_entropy(nodes)

    # Convert to score (lower entropy is better, so invert)
    score = 1.0 - entropy

    return {
        "value": score,
        "details": {
            "entropy": entropy,
            "normalized_score": score
        }
    }


# ===== Metric 2: Branching Balance =====

def calculate_branching_balance_metric(graph_json: str, **kwargs) -> Dict[str, Any]:
    """
    Metric 2: 분기 균형

    자식 노드 수의 균등도

    Args:
        graph_json: Path to graph JSON

    Returns:
        Score dict
    """
    graph_data = load_json(graph_json)
    edges = graph_data.get('graph', {}).get('edges', [])

    # Count children for each node
    children_counts = defaultdict(int)
    for edge in edges:
        children_counts[edge['source']] += 1

    counts = list(children_counts.values())

    if not counts:
        return {"value": 1.0, "details": {"no_children": True}}

    mean_count = np.mean(counts)
    std_count = np.std(counts)

    # Calculate balance: 1 - CV (coefficient of variation)
    cv = std_count / mean_count if mean_count > 0 else 0
    balance = max(0.0, 1.0 - cv)

    return {
        "value": balance,
        "details": {
            "mean_children": mean_count,
            "std_children": std_count,
            "cv": cv,
            "balance": balance
        }
    }


# ===== Metric 3: Edge Crossing Minimization =====

def calculate_edge_crossing_minimization(graph_json: str, **kwargs) -> Dict[str, Any]:
    """
    Metric 3: 간선 교차 최소화

    선이 겹치지 않는 정도

    Args:
        graph_json: Path to graph JSON

    Returns:
        Score dict
    """
    graph_data = load_json(graph_json)
    graph = graph_data.get('graph', {})

    crossings = count_edge_crossings(graph)
    edges_count = len(graph.get('edges', []))

    # Max possible crossings = n*(n-1)/2
    max_crossings = (edges_count * (edges_count - 1)) / 2 if edges_count > 1 else 1

    # Calculate score
    score = 1.0 - (crossings / max_crossings) if max_crossings > 0 else 1.0

    return {
        "value": score,
        "details": {
            "actual_crossings": crossings,
            "max_possible_crossings": max_crossings,
            "crossing_rate": crossings / max_crossings if max_crossings > 0 else 0
        }
    }


# ===== Metric 4: Centrality Distribution Balance =====

def calculate_centrality_distribution_balance(graph_json: str, **kwargs) -> Dict[str, Any]:
    """
    Metric 4: 중심성 분포 균형

    PageRank 값의 편차

    Args:
        graph_json: Path to graph JSON

    Returns:
        Score dict
    """
    graph_data = load_json(graph_json)
    edges = graph_data.get('graph', {}).get('edges', [])
    nodes = graph_data.get('graph', {}).get('nodes', [])

    if not edges:
        return {"value": 1.0, "details": {"no_edges": True}}

    # Simple centrality: count incoming edges
    centralities = defaultdict(int)
    for edge in edges:
        centralities[edge['target']] += 1

    # Add root nodes (degree 0)
    for node in nodes:
        if node['id'] not in centralities:
            centralities[node['id']] = 0

    values = list(centralities.values())

    if not values:
        return {"value": 1.0, "details": {"no_values": True}}

    mean_val = np.mean(values)
    std_val = np.std(values)

    cv = std_val / mean_val if mean_val > 0 else 0
    balance = max(0.0, 1.0 - cv)

    return {
        "value": balance,
        "details": {
            "mean_centrality": mean_val,
            "std_centrality": std_val,
            "cv": cv
        }
    }


# ===== Metric 5: Cluster Cohesion =====

def calculate_cluster_cohesion_metric(graph_json: str, **kwargs) -> Dict[str, Any]:
    """
    Metric 5: 군집 응집도

    같은 주제 노드가 가까이 있는가 (modularity)

    Args:
        graph_json: Path to graph JSON

    Returns:
        Score dict
    """
    graph_data = load_json(graph_json)
    graph = graph_data.get('graph', {})

    modularity = calculate_modularity(graph)

    # Normalize modularity to 0-1 range (typical range is -0.5 to 1.0)
    normalized = (modularity + 0.5) / 1.5
    normalized = max(0.0, min(1.0, normalized))

    return {
        "value": normalized,
        "details": {
            "modularity": modularity,
            "normalized_score": normalized
        }
    }


# ===== Metric 6: Edge Length Variance =====

def calculate_edge_length_variance_metric(graph_json: str, **kwargs) -> Dict[str, Any]:
    """
    Metric 6: 엣지 길이 분산

    간선 길이의 일관성

    Args:
        graph_json: Path to graph JSON

    Returns:
        Score dict
    """
    graph_data = load_json(graph_json)
    graph = graph_data.get('graph', {})

    nodes = {n['id']: (n.get('x', 0), n.get('y', 0)) for n in graph.get('nodes', [])}
    edges = graph.get('edges', [])

    # Calculate edge lengths
    lengths = []
    for edge in edges:
        p1 = nodes.get(edge['source'])
        p2 = nodes.get(edge['target'])

        if p1 and p2:
            length = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            lengths.append(length)

    if not lengths:
        return {"value": 1.0, "details": {"no_edges": True}}

    mean_length = np.mean(lengths)
    std_length = np.std(lengths)

    cv = std_length / mean_length if mean_length > 0 else 0
    consistency = max(0.0, 1.0 - cv)

    return {
        "value": consistency,
        "details": {
            "mean_length": mean_length,
            "std_length": std_length,
            "cv": cv
        }
    }


# ===== Metric 7: Label Readability =====

def calculate_label_readability(graph_json: str, **kwargs) -> Dict[str, Any]:
    """
    Metric 7: 레이블 가독성

    텍스트가 겹치지 않는가

    Args:
        graph_json: Path to graph JSON

    Returns:
        Score dict
    """
    graph_data = load_json(graph_json)
    nodes = graph_data.get('graph', {}).get('nodes', [])

    # Check node overlaps (proxy for label overlaps)
    overlap_rate = check_node_overlaps(nodes, min_distance=50.0)

    score = 1.0 - overlap_rate

    return {
        "value": score,
        "details": {
            "overlap_rate": overlap_rate,
            "total_nodes": len(nodes)
        }
    }


# ===== Metric 8: Node Density =====

def calculate_node_density_metric(graph_json: str, **kwargs) -> Dict[str, Any]:
    """
    Metric 8: 노드 밀도

    적절한 노드 간 거리 유지

    Args:
        graph_json: Path to graph JSON

    Returns:
        Score dict
    """
    graph_data = load_json(graph_json)
    graph = graph_data.get('graph', {})

    nodes = graph.get('nodes', [])
    layout = graph.get('layout', {})

    if not nodes:
        return {"value": 0.0, "details": {"no_nodes": True}}

    width = layout.get('width', 1000)
    height = layout.get('height', 600)
    area = width * height

    density = len(nodes) / area

    # Optimal density: 0.01 - 0.02 nodes per 1000 pixels²
    optimal_min = 0.01 / 1000
    optimal_max = 0.02 / 1000

    if optimal_min <= density <= optimal_max:
        score = 1.0
    elif density < optimal_min:
        score = density / optimal_min
    else:
        score = max(0.0, 1.0 - (density - optimal_max) / optimal_max)

    return {
        "value": score,
        "details": {
            "density": density,
            "optimal_range": [optimal_min, optimal_max],
            "nodes_per_unit_area": density
        }
    }


# ===== Metric 9: Color Contrast =====

def calculate_color_contrast(graph_json: str, **kwargs) -> Dict[str, Any]:
    """
    Metric 9: 색상 대비

    노드 간 색상 구분도

    Args:
        graph_json: Path to graph JSON

    Returns:
        Score dict
    """
    graph_data = load_json(graph_json)
    nodes = graph_data.get('graph', {}).get('nodes', [])

    # Extract unique colors
    colors = [n.get('color', '#000000') for n in nodes]
    unique_colors = set(colors)

    # Simple heuristic: more unique colors = better distinction
    color_diversity = len(unique_colors) / len(colors) if colors else 0

    # Check if colors follow type convention
    type_colors = {'root': '#3498db', 'main': '#2ecc71', 'side': '#95a5a6'}
    convention_score = 0
    for node in nodes:
        node_type = node.get('type', '')
        node_color = node.get('color', '')
        if node_type in type_colors and node_color == type_colors[node_type]:
            convention_score += 1

    convention_rate = convention_score / len(nodes) if nodes else 0

    # Combined score
    score = (color_diversity * 0.3 + convention_rate * 0.7)

    return {
        "value": score,
        "details": {
            "unique_colors": len(unique_colors),
            "total_nodes": len(colors),
            "color_diversity": color_diversity,
            "convention_rate": convention_rate
        }
    }


# ===== Metric 10: Interaction Responsiveness =====

def calculate_interaction_responsiveness(render_time: float = 0.05, **kwargs) -> Dict[str, Any]:
    """
    Metric 10: 상호작용 응답성

    확대/축소 지연 시간

    Args:
        render_time: Rendering time in seconds

    Returns:
        Score dict
    """
    # Normalize: 0.05s = 1.0, 0.5s = 0.0
    normalized = max(0.0, 1.0 - (render_time - 0.05) / 0.45)

    return {
        "value": normalized,
        "details": {
            "render_time_sec": render_time,
            "normalized_score": normalized
        }
    }


# ===== Main Evaluation Function =====

def evaluate_layout(
    graph_json: str,
    render_time: float = 0.05,
    weights: Optional[Dict[str, float]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Run all 10 layout rubric evaluations

    Args:
        graph_json: Path to graph JSON
        render_time: Rendering time
        weights: Optional custom weights dict

    Returns:
        Complete layout evaluation results
    """
    # Default weights
    if weights is None:
        weights = {
            "depth_balance": 0.14,
            "branching_balance": 0.12,
            "edge_crossing_minimization": 0.13,
            "centrality_distribution_balance": 0.10,
            "cluster_cohesion": 0.11,
            "edge_length_variance": 0.09,
            "label_readability": 0.10,
            "node_density": 0.08,
            "color_contrast": 0.07,
            "interaction_responsiveness": 0.06
        }

    # Calculate all metrics
    results = {
        "depth_balance": calculate_depth_balance(graph_json),
        "branching_balance": calculate_branching_balance_metric(graph_json),
        "edge_crossing_minimization": calculate_edge_crossing_minimization(graph_json),
        "centrality_distribution_balance": calculate_centrality_distribution_balance(graph_json),
        "cluster_cohesion": calculate_cluster_cohesion_metric(graph_json),
        "edge_length_variance": calculate_edge_length_variance_metric(graph_json),
        "label_readability": calculate_label_readability(graph_json),
        "node_density": calculate_node_density_metric(graph_json),
        "color_contrast": calculate_color_contrast(graph_json),
        "interaction_responsiveness": calculate_interaction_responsiveness(render_time)
    }

    # Calculate weighted score
    weighted_score = sum(
        results[metric]["value"] * weights[metric]
        for metric in weights.keys()
    )

    return {
        "rubric_type": "layout",
        "scores": results,
        "weights": weights,
        "weighted_score": weighted_score
    }
