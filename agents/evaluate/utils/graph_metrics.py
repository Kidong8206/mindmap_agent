"""
Graph metrics calculation utilities

Handles graph-theoretic metrics for mindmap evaluation.
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from collections import defaultdict


def calculate_tree_edit_distance(tree1: dict, tree2: dict) -> int:
    """
    Calculate tree edit distance between two graphs

    Simplified TED using node/edge comparison

    Args:
        tree1: First graph dict with 'nodes' and 'edges'
        tree2: Second graph dict with 'nodes' and 'edges'

    Returns:
        Edit distance (number of operations)
    """
    nodes1 = {n['id']: n['label'] for n in tree1.get('nodes', [])}
    nodes2 = {n['id']: n['label'] for n in tree2.get('nodes', [])}

    edges1 = {(e['source'], e['target']) for e in tree1.get('edges', [])}
    edges2 = {(e['source'], e['target']) for e in tree2.get('edges', [])}

    # Node operations
    node_labels1 = set(nodes1.values())
    node_labels2 = set(nodes2.values())

    node_deletions = len(node_labels1 - node_labels2)
    node_insertions = len(node_labels2 - node_labels1)

    # Edge operations
    edge_deletions = len(edges1 - edges2)
    edge_insertions = len(edges2 - edges1)

    total_distance = node_deletions + node_insertions + edge_deletions + edge_insertions

    return total_distance


def calculate_graph_metrics(graph: dict) -> dict:
    """
    Calculate comprehensive graph metrics

    Args:
        graph: Graph dict with 'nodes' and 'edges'

    Returns:
        Dict of graph metrics
    """
    nodes = graph.get('nodes', [])
    edges = graph.get('edges', [])

    if not nodes:
        return {
            "node_count": 0,
            "edge_count": 0,
            "avg_degree": 0,
            "max_depth": 0,
            "branching_factor": 0
        }

    # Basic counts
    node_count = len(nodes)
    edge_count = len(edges)

    # Degree distribution
    degree_counts = defaultdict(int)
    for edge in edges:
        degree_counts[edge['source']] += 1

    degrees = list(degree_counts.values())
    avg_degree = np.mean(degrees) if degrees else 0

    # Depth distribution
    depths = [n.get('depth', 0) for n in nodes]
    max_depth = max(depths) if depths else 0

    # Branching factor (average children per node)
    children_counts = defaultdict(int)
    for edge in edges:
        children_counts[edge['source']] += 1

    branching_factors = [c for c in children_counts.values() if c > 0]
    avg_branching = np.mean(branching_factors) if branching_factors else 0

    return {
        "node_count": node_count,
        "edge_count": edge_count,
        "avg_degree": avg_degree,
        "max_depth": max_depth,
        "branching_factor": avg_branching,
        "depth_distribution": depths,
        "degree_distribution": degrees
    }


def count_edge_crossings(graph: dict) -> int:
    """
    Count edge crossings in graph layout

    Args:
        graph: Graph dict with nodes (with x, y) and edges

    Returns:
        Number of edge crossings
    """
    nodes = {n['id']: (n.get('x', 0), n.get('y', 0)) for n in graph.get('nodes', [])}
    edges = graph.get('edges', [])

    crossings = 0

    # Check each pair of edges
    for i, edge1 in enumerate(edges):
        for edge2 in edges[i+1:]:
            # Skip if edges share a node
            if (edge1['source'] == edge2['source'] or
                edge1['source'] == edge2['target'] or
                edge1['target'] == edge2['source'] or
                edge1['target'] == edge2['target']):
                continue

            # Check intersection
            p1 = nodes.get(edge1['source'])
            p2 = nodes.get(edge1['target'])
            p3 = nodes.get(edge2['source'])
            p4 = nodes.get(edge2['target'])

            if p1 and p2 and p3 and p4:
                if line_segments_intersect(p1, p2, p3, p4):
                    crossings += 1

    return crossings


def line_segments_intersect(
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    p3: Tuple[float, float],
    p4: Tuple[float, float]
) -> bool:
    """
    Check if two line segments intersect

    Uses CCW (counter-clockwise) algorithm
    """
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


def calculate_modularity(graph: dict, communities: List[List[str]] = None) -> float:
    """
    Calculate modularity score for graph clustering

    Args:
        graph: Graph dict
        communities: Optional list of communities (node id lists)

    Returns:
        Modularity score (-1 to 1)
    """
    if communities is None:
        # Auto-detect communities using simple depth-based clustering
        nodes = graph.get('nodes', [])
        depth_groups = defaultdict(list)
        for node in nodes:
            depth = node.get('depth', 0)
            depth_groups[depth].append(node['id'])
        communities = list(depth_groups.values())

    edges = graph.get('edges', [])
    m = len(edges)

    if m == 0:
        return 0.0

    # Build adjacency
    adj = defaultdict(set)
    degree = defaultdict(int)
    for edge in edges:
        adj[edge['source']].add(edge['target'])
        adj[edge['target']].add(edge['source'])
        degree[edge['source']] += 1
        degree[edge['target']] += 1

    # Calculate modularity
    Q = 0.0
    for community in communities:
        for i in community:
            for j in community:
                if j in adj[i]:
                    Q += 1 - (degree[i] * degree[j]) / (2 * m)

    Q /= (2 * m)

    return Q


def calculate_depth_entropy(nodes: List[dict]) -> float:
    """
    Calculate entropy of depth distribution

    Lower entropy = more balanced tree

    Args:
        nodes: List of node dicts with 'depth' field

    Returns:
        Normalized entropy (0-1)
    """
    if not nodes:
        return 0.0

    depths = [n.get('depth', 0) for n in nodes]
    depth_counts = defaultdict(int)
    for d in depths:
        depth_counts[d] += 1

    # Calculate probabilities
    total = len(depths)
    probs = [count / total for count in depth_counts.values()]

    # Calculate entropy
    entropy = -sum(p * np.log2(p) for p in probs if p > 0)

    # Normalize by max entropy
    max_entropy = np.log2(len(depth_counts)) if len(depth_counts) > 1 else 1

    return entropy / max_entropy if max_entropy > 0 else 0.0


def check_node_overlaps(nodes: List[dict], min_distance: float = 50.0) -> float:
    """
    Calculate ratio of overlapping nodes

    Args:
        nodes: List of node dicts with x, y, size
        min_distance: Minimum distance between node centers

    Returns:
        Overlap ratio (0-1)
    """
    if len(nodes) < 2:
        return 0.0

    overlaps = 0
    total_pairs = 0

    for i, node1 in enumerate(nodes):
        for node2 in nodes[i+1:]:
            x1, y1 = node1.get('x', 0), node1.get('y', 0)
            x2, y2 = node2.get('x', 0), node2.get('y', 0)

            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

            size1 = node1.get('size', 20)
            size2 = node2.get('size', 20)
            min_dist = min_distance + (size1 + size2) / 2

            if distance < min_dist:
                overlaps += 1

            total_pairs += 1

    return overlaps / total_pairs if total_pairs > 0 else 0.0
