"""
Golden set comparison utilities

Handles comparison between generated and golden reference data.
"""

import numpy as np
from typing import Dict, List, Set, Any, Tuple


def calculate_f1_score(
    predicted: Set[Any],
    true: Set[Any]
) -> Tuple[float, float, float]:
    """
    Calculate precision, recall, and F1 score

    Args:
        predicted: Set of predicted items
        true: Set of true items

    Returns:
        (precision, recall, f1)
    """
    if not predicted and not true:
        return 1.0, 1.0, 1.0

    if not predicted:
        return 0.0, 0.0, 0.0

    if not true:
        return 0.0, 0.0, 0.0

    tp = len(predicted & true)
    fp = len(predicted - true)
    fn = len(true - predicted)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return precision, recall, f1


def compare_with_golden(
    generated: dict,
    golden: dict,
    comparison_type: str = "graph"
) -> dict:
    """
    Compare generated output with golden reference

    Args:
        generated: Generated graph/data
        golden: Golden reference
        comparison_type: Type of comparison ("graph", "keywords", "sessions")

    Returns:
        Comparison metrics dict
    """
    if comparison_type == "graph":
        return compare_graphs(generated, golden)
    elif comparison_type == "keywords":
        return compare_keywords(generated, golden)
    elif comparison_type == "sessions":
        return compare_sessions(generated, golden)
    else:
        raise ValueError(f"Unknown comparison type: {comparison_type}")


def compare_graphs(generated: dict, golden: dict) -> dict:
    """
    Compare generated and golden graphs

    Args:
        generated: Generated graph
        golden: Golden graph

    Returns:
        Graph comparison metrics
    """
    gen_nodes = {n['label'] for n in generated.get('nodes', [])}
    gold_nodes = {n['label'] for n in golden.get('nodes', [])}

    gen_edges = {(e['source'], e['target']) for e in generated.get('edges', [])}
    gold_edges = {(e['source'], e['target']) for e in golden.get('edges', [])}

    # Node comparison
    node_precision, node_recall, node_f1 = calculate_f1_score(gen_nodes, gold_nodes)

    # Edge comparison
    edge_precision, edge_recall, edge_f1 = calculate_f1_score(gen_edges, gold_edges)

    # Jaccard similarity
    node_jaccard = len(gen_nodes & gold_nodes) / len(gen_nodes | gold_nodes) if gen_nodes | gold_nodes else 0
    edge_jaccard = len(gen_edges & gold_edges) / len(gen_edges | gold_edges) if gen_edges | gold_edges else 0

    return {
        "node_overlap": {
            "generated_count": len(gen_nodes),
            "golden_count": len(gold_nodes),
            "common_count": len(gen_nodes & gold_nodes),
            "precision": node_precision,
            "recall": node_recall,
            "f1": node_f1,
            "jaccard": node_jaccard
        },
        "edge_overlap": {
            "generated_count": len(gen_edges),
            "golden_count": len(gold_edges),
            "common_count": len(gen_edges & gold_edges),
            "precision": edge_precision,
            "recall": edge_recall,
            "f1": edge_f1,
            "jaccard": edge_jaccard
        }
    }


def compare_keywords(generated: List[str], golden: List[str]) -> dict:
    """
    Compare keyword lists

    Args:
        generated: Generated keywords
        golden: Golden keywords

    Returns:
        Keyword comparison metrics
    """
    gen_set = set(generated)
    gold_set = set(golden)

    precision, recall, f1 = calculate_f1_score(gen_set, gold_set)

    return {
        "generated_count": len(generated),
        "golden_count": len(golden),
        "common_count": len(gen_set & gold_set),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "missing_keywords": list(gold_set - gen_set),
        "extra_keywords": list(gen_set - gold_set)
    }


def compare_sessions(generated: List[List[int]], golden: List[List[int]]) -> dict:
    """
    Compare session boundaries

    Args:
        generated: List of session turn ranges
        golden: List of golden session turn ranges

    Returns:
        Session comparison metrics
    """
    # Extract boundaries
    gen_boundaries = {turn for session in generated for turn in [session[0], session[-1]]}
    gold_boundaries = {turn for session in golden for turn in [session[0], session[-1]]}

    precision, recall, f1 = calculate_f1_score(gen_boundaries, gold_boundaries)

    # Window-based matching (allow ±1 turn tolerance)
    matched = 0
    for gb in gold_boundaries:
        if any(abs(gb - pb) <= 1 for pb in gen_boundaries):
            matched += 1

    window_recall = matched / len(gold_boundaries) if gold_boundaries else 0

    return {
        "generated_sessions": len(generated),
        "golden_sessions": len(golden),
        "exact_precision": precision,
        "exact_recall": recall,
        "exact_f1": f1,
        "window_recall": window_recall,
        "generated_boundaries": sorted(list(gen_boundaries)),
        "golden_boundaries": sorted(list(gold_boundaries))
    }


def calculate_jaccard_similarity(set1: Set, set2: Set) -> float:
    """
    Calculate Jaccard similarity coefficient

    Args:
        set1: First set
        set2: Second set

    Returns:
        Jaccard similarity (0-1)
    """
    if not set1 and not set2:
        return 1.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0


def compare_node_attributes(
    generated_nodes: List[dict],
    golden_nodes: List[dict],
    attribute: str = "depth"
) -> dict:
    """
    Compare specific attribute across nodes

    Args:
        generated_nodes: Generated node list
        golden_nodes: Golden node list
        attribute: Attribute to compare

    Returns:
        Attribute comparison metrics
    """
    gen_values = [n.get(attribute, 0) for n in generated_nodes]
    gold_values = [n.get(attribute, 0) for n in golden_nodes]

    if not gen_values or not gold_values:
        return {"error": "No values to compare"}

    # Distribution comparison
    gen_mean = np.mean(gen_values)
    gold_mean = np.mean(gold_values)

    gen_std = np.std(gen_values)
    gold_std = np.std(gold_values)

    # Absolute difference
    mean_diff = abs(gen_mean - gold_mean)
    std_diff = abs(gen_std - gold_std)

    return {
        "attribute": attribute,
        "generated_mean": gen_mean,
        "golden_mean": gold_mean,
        "generated_std": gen_std,
        "golden_std": gold_std,
        "mean_difference": mean_diff,
        "std_difference": std_diff,
        "normalized_difference": mean_diff / gold_mean if gold_mean > 0 else 0
    }
