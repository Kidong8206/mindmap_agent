"""
Context Rubric Evaluation (10 metrics)

Evaluates the quality of context analysis (main/side path identification).
"""

import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional

from agents.utils import load_json
from .utils.embeddings import (
    calculate_embeddings,
    calculate_path_coherence,
    calculate_topic_transition_stability,
    cosine_similarity
)
from .utils.comparison import calculate_f1_score, compare_sessions


# ===== Metric 1: Main Path Coherence =====

def calculate_main_path_coherence(
    context_json: str,
    embeddings_npy: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 1: 메인 경로 일관성

    메인 경로 턴들의 의미적 응집도 측정

    Args:
        context_json: Path to context JSON
        embeddings_npy: Path to embeddings file

    Returns:
        Score dict with value and details
    """
    context_data = load_json(context_json)
    embeddings = np.load(embeddings_npy)

    # Extract main path turns from all contexts
    main_path_scores = []

    for context in context_data.get('contexts', []):
        main_path = context.get('main_path', {})
        path_turns = main_path.get('turns', [])

        if len(path_turns) < 2:
            continue

        # Calculate coherence for this path
        metrics = calculate_path_coherence(embeddings, path_turns)
        main_path_scores.append(metrics['coherence'])

    # Average across all sessions
    if main_path_scores:
        score = np.mean(main_path_scores)
    else:
        score = 0.0

    return {
        "value": score,
        "details": {
            "session_count": len(main_path_scores),
            "individual_scores": main_path_scores,
            "std": np.std(main_path_scores) if main_path_scores else 0.0
        }
    }


# ===== Metric 2: Branch Detection Recall =====

def calculate_branch_detection_recall(
    context_json: str,
    golden_annotations: dict,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 2: 분기 탐지 재현율

    Side branch 탐지 성능 (F1 score)

    Args:
        context_json: Path to context JSON
        golden_annotations: Golden annotations dict

    Returns:
        Score dict
    """
    context_data = load_json(context_json)

    # Extract predicted branches
    predicted_branches = []
    for context in context_data.get('contexts', []):
        for side_path in context.get('side_paths', []):
            branch_from = side_path.get('branch_from_turn')
            if branch_from is not None:
                predicted_branches.append(branch_from)

    # Extract true branches
    true_branches = []
    for branch in golden_annotations.get('true_side_branches', []):
        branch_from = branch.get('branch_from', branch.get('turns', [None])[0])
        if branch_from is not None:
            true_branches.append(branch_from)

    # Calculate F1
    pred_set = set(predicted_branches)
    true_set = set(true_branches)

    precision, recall, f1 = calculate_f1_score(pred_set, true_set)

    return {
        "value": f1,
        "details": {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "predicted_count": len(pred_set),
            "true_count": len(true_set),
            "correct_count": len(pred_set & true_set)
        }
    }


# ===== Metric 3: Side-Main Connection Accuracy =====

def calculate_side_main_connection_accuracy(
    context_json: str,
    golden_annotations: dict,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 3: 사이드-메인 연결 정확도

    분기가 올바른 위치에 연결되었는지 검증

    Args:
        context_json: Path to context JSON
        golden_annotations: Golden annotations

    Returns:
        Score dict
    """
    context_data = load_json(context_json)

    # Extract predicted connections
    predicted_connections = []
    for context in context_data.get('contexts', []):
        for side_path in context.get('side_paths', []):
            conn = {
                'branch_from': side_path.get('branch_from_turn'),
                'rejoin': side_path.get('rejoin_turn')
            }
            predicted_connections.append(conn)

    # Extract true connections
    true_connections = []
    for branch in golden_annotations.get('true_side_branches', []):
        conn = {
            'branch_from': branch.get('branch_from'),
            'rejoin': branch.get('rejoin')
        }
        true_connections.append(conn)

    # Calculate accuracy (allow ±1 turn tolerance)
    correct = 0
    total = max(len(predicted_connections), len(true_connections))

    if total == 0:
        return {"value": 1.0, "details": {"no_branches": True}}

    for pred in predicted_connections:
        for true in true_connections:
            if (abs(pred['branch_from'] - true['branch_from']) <= 1 and
                abs(pred['rejoin'] - true['rejoin']) <= 1):
                correct += 1
                break

    accuracy = correct / len(true_connections) if true_connections else 0.0

    return {
        "value": accuracy,
        "details": {
            "correct": correct,
            "total": len(true_connections),
            "predicted_count": len(predicted_connections)
        }
    }


# ===== Metric 4: Session Boundary F1 =====

def calculate_session_boundary_f1(
    session_split_json: str,
    golden_annotations: dict,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 4: 세션 경계 검출 정확도

    주제 전환 지점 탐지 성능

    Args:
        session_split_json: Path to session split JSON
        golden_annotations: Golden annotations

    Returns:
        Score dict
    """
    session_data = load_json(session_split_json)

    # Extract predicted boundaries
    predicted_boundaries = []
    for session in session_data.get('sessions', []):
        turn_range = session.get('turn_range', [])
        if len(turn_range) == 2:
            predicted_boundaries.append(turn_range[0])

    # Extract true boundaries
    true_boundaries = golden_annotations.get('true_session_boundaries', [])

    # Calculate F1 (window-based matching)
    comparison = compare_sessions(
        [list(range(predicted_boundaries[i], predicted_boundaries[i+1]))
         for i in range(len(predicted_boundaries)-1)],
        [list(range(true_boundaries[i], true_boundaries[i+1]))
         for i in range(len(true_boundaries)-1)]
    )

    return {
        "value": comparison.get('exact_f1', 0.0),
        "details": comparison
    }


# ===== Metric 5: Summary-Path Consistency =====

def calculate_summary_path_consistency(
    context_json: str,
    embeddings_npy: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 5: 요약-경로 정합성

    경로 요약과 실제 턴 내용의 일치도

    Args:
        context_json: Path to context JSON
        embeddings_npy: Path to embeddings

    Returns:
        Score dict
    """
    context_data = load_json(context_json)
    embeddings = np.load(embeddings_npy)

    # For each context, compare summary embedding to path centroid
    consistencies = []

    for context in context_data.get('contexts', []):
        main_path = context.get('main_path', {})
        summary = main_path.get('topic', '')
        path_turns = main_path.get('turns', [])

        if not summary or not path_turns:
            continue

        # Calculate summary embedding (would need sentence-transformers)
        # For now, use path coherence as proxy
        metrics = calculate_path_coherence(embeddings, path_turns)
        consistencies.append(metrics['coherence'])

    score = np.mean(consistencies) if consistencies else 0.0

    return {
        "value": score,
        "details": {
            "context_count": len(consistencies),
            "individual_scores": consistencies
        }
    }


# ===== Metric 6: Topic Transition Stability =====

def calculate_topic_transition_stability_metric(
    context_json: str,
    embeddings_npy: str,
    session_split_json: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 6: 토픽 전이 안정성

    세션 간 급격한 주제 변화가 없는지 측정

    Args:
        context_json: Path to context JSON
        embeddings_npy: Path to embeddings
        session_split_json: Path to session split JSON

    Returns:
        Score dict
    """
    session_data = load_json(session_split_json)
    embeddings = np.load(embeddings_npy)

    # Extract session boundaries
    boundaries = []
    for session in session_data.get('sessions', []):
        turn_range = session.get('turn_range', [])
        if len(turn_range) == 2:
            boundaries.append(turn_range[0])

    # Calculate stability
    stability = calculate_topic_transition_stability(embeddings, boundaries)

    return {
        "value": stability,
        "details": {
            "session_count": len(boundaries),
            "boundaries": boundaries
        }
    }


# ===== Metric 7: Edge Direction Error Rate =====

def calculate_edge_direction_error_rate(
    context_json: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 7: 간선 방향성 누락률

    대화 흐름 방향이 명확히 표시되었는지

    Args:
        context_json: Path to context JSON

    Returns:
        Score dict (lower is better, so return 1 - error_rate)
    """
    context_data = load_json(context_json)

    total_edges = 0
    missing_direction = 0

    for context in context_data.get('contexts', []):
        main_path = context.get('main_path', {})
        path_turns = main_path.get('turns', [])

        # Check if turns are in order (ascending)
        if path_turns:
            if path_turns != sorted(path_turns):
                missing_direction += 1
            total_edges += len(path_turns) - 1

        # Check side paths
        for side_path in context.get('side_paths', []):
            side_turns = side_path.get('turns', [])
            if side_turns != sorted(side_turns):
                missing_direction += 1
            total_edges += len(side_turns) - 1

    error_rate = missing_direction / total_edges if total_edges > 0 else 0.0

    return {
        "value": 1.0 - error_rate,  # Convert to score (higher is better)
        "details": {
            "missing_direction": missing_direction,
            "total_edges": total_edges,
            "error_rate": error_rate
        }
    }


# ===== Metric 8: Duplicate Branch Rate =====

def calculate_duplicate_branch_rate(
    context_json: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 8: 중복 분기율

    같은 내용의 분기가 중복되지 않았는지

    Args:
        context_json: Path to context JSON

    Returns:
        Score dict (lower is better)
    """
    context_data = load_json(context_json)

    all_branches = []
    for context in context_data.get('contexts', []):
        for side_path in context.get('side_paths', []):
            topic = side_path.get('topic', '')
            all_branches.append(topic)

    # Count duplicates
    unique_branches = set(all_branches)
    duplicate_count = len(all_branches) - len(unique_branches)

    duplicate_rate = duplicate_count / len(all_branches) if all_branches else 0.0

    return {
        "value": 1.0 - duplicate_rate,  # Convert to score
        "details": {
            "total_branches": len(all_branches),
            "unique_branches": len(unique_branches),
            "duplicate_count": duplicate_count,
            "duplicate_rate": duplicate_rate
        }
    }


# ===== Metric 9: Latency =====

def calculate_latency(
    processing_time: float,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 9: 지연 지표

    처리 시간 (lower is better)

    Args:
        processing_time: Processing time in seconds

    Returns:
        Score dict (normalized, higher is better)
    """
    # Normalize: assume 10 seconds is baseline (0.5 score)
    # 5 seconds = 1.0, 20 seconds = 0.0
    normalized = max(0.0, 1.0 - (processing_time - 5.0) / 15.0)

    return {
        "value": normalized,
        "details": {
            "processing_time_sec": processing_time,
            "normalized_score": normalized
        }
    }


# ===== Metric 10: Parsing Stability =====

def calculate_parsing_stability(
    context_json: str,
    schema_path: str = "configs/schema/context_schema.json",
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 10: 파싱 안정성

    JSON 형식 오류 없이 파싱되었는지

    Args:
        context_json: Path to context JSON
        schema_path: Path to JSON schema

    Returns:
        Score dict (1.0 if valid, 0.0 otherwise)
    """
    try:
        from agents.utils.schema_validator import validate_schema

        context_data = load_json(context_json)
        validate_schema(context_data, "context_schema.json")

        return {
            "value": 1.0,
            "details": {
                "valid": True,
                "error": None
            }
        }

    except Exception as e:
        return {
            "value": 0.0,
            "details": {
                "valid": False,
                "error": str(e)
            }
        }


# ===== Main Evaluation Function =====

def evaluate_context(
    context_json: str,
    embeddings_npy: str,
    session_split_json: str,
    golden_annotations: dict,
    processing_time: float,
    weights: Optional[Dict[str, float]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Run all 10 context rubric evaluations

    Args:
        context_json: Path to context JSON
        embeddings_npy: Path to embeddings
        session_split_json: Path to session split JSON
        golden_annotations: Golden annotations dict
        processing_time: Processing time for stage 2
        weights: Optional custom weights dict

    Returns:
        Complete context evaluation results
    """
    # Default weights
    if weights is None:
        weights = {
            "main_path_coherence": 0.15,
            "branch_detection_recall": 0.12,
            "side_main_connection_accuracy": 0.10,
            "session_boundary_f1": 0.13,
            "summary_path_consistency": 0.10,
            "topic_transition_stability": 0.10,
            "edge_direction_error_rate": 0.08,
            "duplicate_branch_rate": 0.08,
            "latency_sec": 0.07,
            "parsing_stability": 0.07
        }

    # Calculate all metrics
    results = {
        "main_path_coherence": calculate_main_path_coherence(
            context_json, embeddings_npy
        ),
        "branch_detection_recall": calculate_branch_detection_recall(
            context_json, golden_annotations
        ),
        "side_main_connection_accuracy": calculate_side_main_connection_accuracy(
            context_json, golden_annotations
        ),
        "session_boundary_f1": calculate_session_boundary_f1(
            session_split_json, golden_annotations
        ),
        "summary_path_consistency": calculate_summary_path_consistency(
            context_json, embeddings_npy
        ),
        "topic_transition_stability": calculate_topic_transition_stability_metric(
            context_json, embeddings_npy, session_split_json
        ),
        "edge_direction_error_rate": calculate_edge_direction_error_rate(
            context_json
        ),
        "duplicate_branch_rate": calculate_duplicate_branch_rate(
            context_json
        ),
        "latency_sec": calculate_latency(processing_time),
        "parsing_stability": calculate_parsing_stability(context_json)
    }

    # Calculate weighted score
    weighted_score = sum(
        results[metric]["value"] * weights[metric]
        for metric in weights.keys()
    )

    return {
        "rubric_type": "context",
        "scores": results,
        "weights": weights,
        "weighted_score": weighted_score
    }
