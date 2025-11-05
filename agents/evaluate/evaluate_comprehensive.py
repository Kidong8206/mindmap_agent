"""
Comprehensive Rubric Evaluation (10 metrics)

Evaluates overall system quality combining all aspects.
"""

import numpy as np
from typing import Dict, List, Any, Optional

from agents.utils import load_json
from .utils.graph_metrics import calculate_tree_edit_distance
from .utils.comparison import compare_with_golden, compare_keywords


# ===== Metric 1: Structural Score Weighted Sum =====

def calculate_structural_score_weighted_sum(
    context_score: float,
    layout_score: float,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 1: 구조 점수 가중합

    맥락+레이아웃 종합

    Args:
        context_score: Context rubric weighted score
        layout_score: Layout rubric weighted score

    Returns:
        Score dict
    """
    score = 0.5 * context_score + 0.5 * layout_score

    return {
        "value": score,
        "details": {
            "context_score": context_score,
            "layout_score": layout_score,
            "weighted_sum": score
        }
    }


# ===== Metric 2: Content Coverage =====

def calculate_content_coverage(
    graph_json: str,
    golden_annotations: dict,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 2: 내용 포괄성

    원본 키워드 커버율

    Args:
        graph_json: Path to graph JSON
        golden_annotations: Golden annotations

    Returns:
        Score dict
    """
    graph_data = load_json(graph_json)
    nodes = graph_data.get('graph', {}).get('nodes', [])

    generated_keywords = {n['label'] for n in nodes}
    true_keywords = set(golden_annotations.get('true_keywords', []))

    if not true_keywords:
        return {"value": 1.0, "details": {"no_true_keywords": True}}

    coverage = len(generated_keywords & true_keywords) / len(true_keywords)

    return {
        "value": coverage,
        "details": {
            "generated_count": len(generated_keywords),
            "true_count": len(true_keywords),
            "covered_count": len(generated_keywords & true_keywords),
            "coverage_rate": coverage
        }
    }


# ===== Metric 3: Offtopic Penalty =====

def calculate_offtopic_penalty(
    graph_json: str,
    golden_annotations: dict,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 3: 오프토픽 패널티

    무관한 노드 비율

    Args:
        graph_json: Path to graph JSON
        golden_annotations: Golden annotations

    Returns:
        Score dict (negative penalty)
    """
    graph_data = load_json(graph_json)
    nodes = graph_data.get('graph', {}).get('nodes', [])

    generated_keywords = {n['label'] for n in nodes}
    true_keywords = set(golden_annotations.get('true_keywords', []))

    if not generated_keywords:
        return {"value": 0.0, "details": {"no_generated_keywords": True}}

    offtopic_count = len(generated_keywords - true_keywords)
    offtopic_rate = offtopic_count / len(generated_keywords)

    penalty = -1.0 * offtopic_rate

    return {
        "value": penalty,
        "details": {
            "offtopic_count": offtopic_count,
            "total_generated": len(generated_keywords),
            "offtopic_rate": offtopic_rate,
            "penalty": penalty
        }
    }


# ===== Metric 4: Format Compliance Rate =====

def calculate_format_compliance_rate(
    graph_json: str,
    schema_path: str = "configs/schema/graph_schema.json",
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 4: 포맷 준수율

    JSON 스키마 검증 통과율

    Args:
        graph_json: Path to graph JSON
        schema_path: Path to schema

    Returns:
        Score dict
    """
    try:
        from agents.utils.schema_validator import validate_schema

        graph_data = load_json(graph_json)
        validate_schema(graph_data, "graph_schema.json")

        # Check required fields
        graph = graph_data.get('graph', {})
        required_fields = ['nodes', 'edges', 'layout']
        valid_fields = sum(1 for f in required_fields if f in graph)

        compliance_rate = valid_fields / len(required_fields)

        return {
            "value": compliance_rate,
            "details": {
                "valid_fields": valid_fields,
                "required_fields": len(required_fields),
                "compliance_rate": compliance_rate
            }
        }

    except Exception as e:
        return {
            "value": 0.0,
            "details": {
                "error": str(e),
                "valid": False
            }
        }


# ===== Metric 5: Parsing Success Rate =====

def calculate_parsing_success_rate(
    stage_results: Dict[str, str],
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 5: 파싱 성공률

    5단계 모두 성공 여부

    Args:
        stage_results: Dict of stage statuses

    Returns:
        Score dict
    """
    total_stages = 5
    successful_stages = sum(1 for status in stage_results.values() if status == "success")

    success_rate = successful_stages / total_stages

    return {
        "value": success_rate,
        "details": {
            "successful_stages": successful_stages,
            "total_stages": total_stages,
            "stage_results": stage_results
        }
    }


# ===== Metric 6: User Preference Alignment =====

def calculate_user_preference_alignment(
    user_ratings: List[float],
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 6: 사용자 선호 적합도

    청소년 설문 평균 점수

    Args:
        user_ratings: List of user ratings (1-5 scale)

    Returns:
        Score dict
    """
    if not user_ratings:
        return {"value": 0.5, "details": {"no_ratings": True}}

    mean_rating = np.mean(user_ratings)
    normalized = mean_rating / 5.0  # Normalize to 0-1

    return {
        "value": normalized,
        "details": {
            "mean_rating": mean_rating,
            "rating_count": len(user_ratings),
            "normalized_score": normalized,
            "std": np.std(user_ratings)
        }
    }


# ===== Metric 7: Reproducibility =====

def calculate_reproducibility(
    seed_fixed: bool = True,
    temperature: float = 0.0,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 7: 재현성

    동일 입력에 동일 출력

    Args:
        seed_fixed: Whether random seed is fixed
        temperature: GPT temperature setting

    Returns:
        Score dict
    """
    # Perfect reproducibility if temperature=0 and seed fixed
    if temperature == 0.0 and seed_fixed:
        score = 1.0
    elif temperature == 0.0:
        score = 0.9
    elif seed_fixed:
        score = 0.7
    else:
        score = 0.5

    return {
        "value": score,
        "details": {
            "seed_fixed": seed_fixed,
            "temperature": temperature,
            "deterministic": temperature == 0.0
        }
    }


# ===== Metric 8: Processing Time =====

def calculate_processing_time_score(
    total_time_sec: float,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 8: 처리시간

    전체 파이프라인 속도

    Args:
        total_time_sec: Total processing time

    Returns:
        Score dict
    """
    # Normalize: 10 seconds baseline (0.5), 5s=1.0, 20s=0.0
    normalized = max(0.0, 1.0 - (total_time_sec - 5.0) / 15.0)

    return {
        "value": normalized,
        "details": {
            "total_time_sec": total_time_sec,
            "normalized_score": normalized
        }
    }


# ===== Metric 9: Stability =====

def calculate_stability(
    error_count: int,
    total_runs: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 9: 안정성

    오류율

    Args:
        error_count: Number of errors encountered
        total_runs: Total number of runs

    Returns:
        Score dict
    """
    if total_runs == 0:
        return {"value": 0.0, "details": {"no_runs": True}}

    error_rate = error_count / total_runs
    stability = 1.0 - error_rate

    return {
        "value": stability,
        "details": {
            "error_count": error_count,
            "total_runs": total_runs,
            "error_rate": error_rate,
            "stability": stability
        }
    }


# ===== Metric 10: API Cost =====

def calculate_api_cost_penalty(
    api_calls: int,
    cost_per_call: float = 0.01,
    **kwargs
) -> Dict[str, Any]:
    """
    Metric 10: API 비용

    GPT 호출 횟수 (penalty)

    Args:
        api_calls: Number of API calls
        cost_per_call: Cost per API call

    Returns:
        Score dict (negative penalty)
    """
    total_cost = api_calls * cost_per_call
    penalty = -1.0 * total_cost

    return {
        "value": penalty,
        "details": {
            "api_calls": api_calls,
            "cost_per_call": cost_per_call,
            "total_cost": total_cost,
            "penalty": penalty
        }
    }


# ===== Main Evaluation Function =====

def evaluate_comprehensive(
    graph_json: str,
    context_score: float,
    layout_score: float,
    golden_annotations: dict,
    stage_results: Dict[str, str],
    user_ratings: List[float],
    total_time_sec: float,
    api_calls: int,
    error_count: int = 0,
    total_runs: int = 1,
    weights: Optional[Dict[str, float]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Run all 10 comprehensive rubric evaluations

    Args:
        graph_json: Path to graph JSON
        context_score: Context rubric score
        layout_score: Layout rubric score
        golden_annotations: Golden annotations dict
        stage_results: Dict of stage statuses
        user_ratings: List of user ratings
        total_time_sec: Total processing time
        api_calls: Number of API calls
        error_count: Number of errors
        total_runs: Total runs
        weights: Optional custom weights

    Returns:
        Complete comprehensive evaluation results
    """
    # Default weights
    if weights is None:
        weights = {
            "structural_score_weighted_sum": 0.20,
            "content_coverage": 0.15,
            "offtopic_penalty": -0.10,
            "format_compliance_rate": 0.12,
            "parsing_success_rate": 0.13,
            "user_preference_alignment": 0.25,
            "reproducibility": 0.08,
            "processing_time": 0.05,
            "stability": 0.07,
            "api_cost": -0.05
        }

    # Calculate all metrics
    results = {
        "structural_score_weighted_sum": calculate_structural_score_weighted_sum(
            context_score, layout_score
        ),
        "content_coverage": calculate_content_coverage(
            graph_json, golden_annotations
        ),
        "offtopic_penalty": calculate_offtopic_penalty(
            graph_json, golden_annotations
        ),
        "format_compliance_rate": calculate_format_compliance_rate(graph_json),
        "parsing_success_rate": calculate_parsing_success_rate(stage_results),
        "user_preference_alignment": calculate_user_preference_alignment(user_ratings),
        "reproducibility": calculate_reproducibility(),
        "processing_time": calculate_processing_time_score(total_time_sec),
        "stability": calculate_stability(error_count, total_runs),
        "api_cost": calculate_api_cost_penalty(api_calls)
    }

    # Calculate weighted score
    weighted_score = sum(
        results[metric]["value"] * weights[metric]
        for metric in weights.keys()
    )

    return {
        "rubric_type": "comprehensive",
        "scores": results,
        "weights": weights,
        "weighted_score": weighted_score,
        "context_score": context_score,
        "layout_score": layout_score
    }
