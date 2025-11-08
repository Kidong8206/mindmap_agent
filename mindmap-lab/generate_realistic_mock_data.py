#!/usr/bin/env python3
"""
현실적인 Mock 데이터 생성 스크립트
- 실패 케이스 포함 (2-3%)
- 예상치 못한 결과
- 왜도/이상치/노이즈
- 실행 시간 변동
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, timedelta
from scipy import stats

# 랜덤 시드 고정 (재현성)
np.random.seed(42)

# 경로 설정
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs" / "mock_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("🎭 현실적인 Mock 데이터 생성 시작")
print("   (실패, 이상치, 노이즈 포함)")
print("=" * 70)

# =============================================================================
# 1. 조합 정의 (15개)
# =============================================================================
combinations = [
    {"id": "comb_01", "name": "simple_hierarchical", "expected_score": 72},
    {"id": "comb_02", "name": "simple_force", "expected_score": 68},
    {"id": "comb_03", "name": "simple_radial", "expected_score": 70},
    {"id": "comb_04", "name": "detailed_hierarchical", "expected_score": 76},
    {"id": "comb_05", "name": "detailed_force", "expected_score": 74},
    {"id": "comb_06", "name": "detailed_radial", "expected_score": 75},
    {"id": "comb_07", "name": "strict_hierarchical", "expected_score": 85},
    {"id": "comb_08", "name": "strict_force", "expected_score": 81},
    {"id": "comb_09", "name": "strict_timeline", "expected_score": 79},
    {"id": "comb_10", "name": "hybrid_s1d2_hier", "expected_score": 86},
    {"id": "comb_11", "name": "hybrid_s1d2_force", "expected_score": 82},
    {"id": "comb_12", "name": "hybrid_d1s2_radial", "expected_score": 83},
    {"id": "comb_13", "name": "hybrid_str1d2_radial", "expected_score": 87},
    {"id": "comb_14", "name": "hybrid_d1str2_timeline", "expected_score": 83},
    {"id": "comb_15", "name": "hybrid_all_hier", "expected_score": 80},
]

# =============================================================================
# 2. 대화 정의 (20개)
# =============================================================================
conversations = []
for i in range(4):
    conversations.append({"id": f"conv_{i:03d}", "type": "learning_short"})
for i in range(4, 8):
    conversations.append({"id": f"conv_{i:03d}", "type": "learning_medium"})
for i in range(8, 12):
    conversations.append({"id": f"conv_{i:03d}", "type": "learning_long"})
for i in range(12, 16):
    conversations.append({"id": f"conv_{i:03d}", "type": "brainstorming"})
for i in range(16, 20):
    conversations.append({"id": f"conv_{i:03d}", "type": "info_search"})

# =============================================================================
# 3. 실험 결과 생성 (300개 = 20 × 15)
# =============================================================================
print("\n[1/8] 실험 결과 생성 중...")

experiments = []
start_time = datetime.now()
failure_count = 0
outlier_indices = []

for conv_idx, conv in enumerate(conversations):
    for comb_idx, comb in enumerate(combinations):
        exp_id = len(experiments)

        # 타임스탬프 (순차적으로 증가, 약간의 변동)
        time_offset = timedelta(
            seconds=exp_id * np.random.uniform(5, 15)  # 5-15초 간격
        )
        timestamp = start_time + time_offset

        # 기대 점수
        base_score = comb["expected_score"]

        # 🎲 2-3% 확률로 실패
        if np.random.random() < 0.025 and failure_count < 8:
            # 실패 케이스
            failure_reasons = ["timeout", "api_error", "validation_error", "parse_error"]
            experiments.append({
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "conversation_id": conv["id"],
                "conversation_type": conv["type"],
                "combination_id": comb["id"],
                "combination_name": comb["name"],
                "status": "failed",
                "failure_reason": np.random.choice(failure_reasons),
                "node_count": None,
                "node_score": None,
                "keyword_overlap": None,
                "max_depth": None,
                "depth_score": None,
                "total_score": None,
                "elapsed_time": np.random.uniform(2, 8)  # 실패는 빨리 끝남
            })
            failure_count += 1
            continue

        # 🎯 성공 케이스

        # 1️⃣ 예상치 못한 결과 추가
        # - simple 조합이 가끔 높은 점수
        # - strict 조합이 가끔 낮은 점수
        if "simple" in comb["name"] and exp_id == 23:
            # 예상 외로 높은 점수
            base_score += 18  # 68 → 86
            outlier_indices.append(exp_id)
        elif "strict" in comb["name"] and exp_id == 147:
            # 예상 외로 낮은 점수
            base_score -= 22  # 85 → 63
            outlier_indices.append(exp_id)

        # 2️⃣ 왜도 있는 분포 사용 (Beta 분포)
        # Beta(5, 2) → 오른쪽으로 치우침
        skew_factor = np.random.beta(5, 2) - 0.7  # -0.7 ~ 0.3

        # 3️⃣ 노이즈 추가
        noise = np.random.normal(0, 6)  # 표준편차 6

        # 최종 점수
        total_score = base_score + skew_factor * 8 + noise

        # 4️⃣ 이상치 추가 (3개)
        if exp_id in [67, 189, 254]:
            # 랜덤하게 매우 높거나 낮게
            total_score += np.random.choice([-15, 20])
            outlier_indices.append(exp_id)

        total_score = np.clip(total_score, 0, 100)

        # 노드 수 (점수와 약한 상관)
        node_count = int(np.random.normal(18, 6) + (total_score - 75) * 0.15)
        node_count = np.clip(node_count, 5, 45)

        # 노드 점수 (최적: 10-30개)
        if 10 <= node_count <= 30:
            node_score = np.random.uniform(0.8, 1.0)
        elif node_count < 10:
            node_score = np.random.uniform(0.3, 0.7)
        else:
            node_score = np.random.uniform(0.4, 0.8)

        # 키워드 중복도
        keyword_overlap = total_score / 100 * np.random.uniform(0.85, 1.05)
        keyword_overlap = np.clip(keyword_overlap, 0, 1)

        # 깊이
        max_depth = np.random.choice([2, 3, 3, 4, 4, 4, 5, 5, 6])
        if 2 <= max_depth <= 5:
            depth_score = np.random.uniform(0.8, 1.0)
        else:
            depth_score = np.random.uniform(0.5, 0.8)

        # 5️⃣ 실행 시간 변동 (지수 분포 사용)
        # 기본 시간 + 네트워크 변동
        if "simple" in comb["name"]:
            base_time = 4.5
        elif "detailed" in comb["name"]:
            base_time = 7.2
        elif "strict" in comb["name"]:
            base_time = 9.8
        else:  # hybrid
            base_time = 8.5

        # 지수 분포로 네트워크 지연 시뮬레이션
        network_delay = np.random.exponential(1.5)
        elapsed_time = base_time + network_delay + np.random.normal(0, 0.8)
        elapsed_time = max(2.0, elapsed_time)

        experiments.append({
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "conversation_id": conv["id"],
            "conversation_type": conv["type"],
            "combination_id": comb["id"],
            "combination_name": comb["name"],
            "status": "success",
            "failure_reason": None,
            "node_count": node_count,
            "node_score": round(node_score, 3),
            "keyword_overlap": round(keyword_overlap, 3),
            "max_depth": max_depth,
            "depth_score": round(depth_score, 3),
            "total_score": round(total_score, 2),
            "elapsed_time": round(elapsed_time, 2)
        })

# DataFrame 생성
df = pd.DataFrame(experiments)

# CSV 저장
df.to_csv(OUTPUT_DIR / "registry.csv", index=False, encoding="utf-8")
print(f"✓ registry.csv 저장 완료")
print(f"  - 총 실험: {len(df)}개")
print(f"  - 성공: {len(df[df['status']=='success'])}개 ({len(df[df['status']=='success'])/len(df)*100:.1f}%)")
print(f"  - 실패: {len(df[df['status']=='failed'])}개 ({len(df[df['status']=='failed'])/len(df)*100:.1f}%)")
print(f"  - 이상치: {len(outlier_indices)}개")

# 성공한 실험만 필터
df_success = df[df['status'] == 'success'].copy()

# =============================================================================
# 4. Summary 생성
# =============================================================================
print("\n[2/8] summary.json 생성 중...")

summary = {
    "total_experiments": len(df),
    "successful": len(df_success),
    "failed": len(df[df['status'] == 'failed']),
    "failure_rate": round(len(df[df['status'] == 'failed']) / len(df) * 100, 2),
    "total_score_stats": {
        "mean": round(df_success['total_score'].mean(), 2),
        "std": round(df_success['total_score'].std(), 2),
        "min": round(df_success['total_score'].min(), 2),
        "max": round(df_success['total_score'].max(), 2),
        "q1": round(df_success['total_score'].quantile(0.25), 2),
        "median": round(df_success['total_score'].median(), 2),
        "q3": round(df_success['total_score'].quantile(0.75), 2),
        "skewness": round(df_success['total_score'].skew(), 3),
        "kurtosis": round(df_success['total_score'].kurtosis(), 3)
    },
    "execution_time_stats": {
        "total_seconds": round(df_success['elapsed_time'].sum(), 1),
        "total_hours": round(df_success['elapsed_time'].sum() / 3600, 2),
        "mean_seconds": round(df_success['elapsed_time'].mean(), 2),
        "std_seconds": round(df_success['elapsed_time'].std(), 2),
        "min_seconds": round(df_success['elapsed_time'].min(), 2),
        "max_seconds": round(df_success['elapsed_time'].max(), 2)
    },
    "outliers": outlier_indices,
    "failure_reasons": df[df['status'] == 'failed']['failure_reason'].value_counts().to_dict()
}

with open(OUTPUT_DIR / "summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print("✓ summary.json 저장 완료")

# =============================================================================
# 5. Combination Details (성공한 실험만)
# =============================================================================
print("\n[3/8] combination_details.json 생성 중...")

comb_details = []
for comb in combinations:
    comb_df = df_success[df_success['combination_id'] == comb['id']]

    if len(comb_df) == 0:
        continue

    scores = comb_df['total_score'].values
    mean_score = scores.mean()
    std_score = scores.std()
    n = len(scores)

    # 95% CI
    if n > 1:
        ci = stats.t.interval(0.95, n-1, loc=mean_score, scale=stats.sem(scores))
    else:
        ci = (mean_score, mean_score)

    comb_details.append({
        "combination_id": comb['id'],
        "combination_name": comb['name'],
        "sample_size": n,
        "failed_count": len(df[(df['combination_id'] == comb['id']) & (df['status'] == 'failed')]),
        "mean_score": round(mean_score, 2),
        "std_dev": round(std_score, 2),
        "ci_95_lower": round(ci[0], 2),
        "ci_95_upper": round(ci[1], 2),
        "min_score": round(scores.min(), 2),
        "max_score": round(scores.max(), 2),
        "median_score": round(np.median(scores), 2)
    })

comb_details.sort(key=lambda x: x['mean_score'], reverse=True)
for rank, item in enumerate(comb_details, 1):
    item['rank'] = rank

with open(OUTPUT_DIR / "combination_details.json", "w", encoding="utf-8") as f:
    json.dump(comb_details, f, ensure_ascii=False, indent=2)
print(f"✓ combination_details.json 저장 완료 ({len(comb_details)}개 조합)")

# =============================================================================
# 6. Top Combinations
# =============================================================================
print("\n[4/8] top_combinations.json 생성 중...")

top_combs = []
for item in comb_details[:10]:
    comb_df = df_success[df_success['combination_id'] == item['combination_id']]
    top_combs.append({
        "rank": item['rank'],
        "combination_id": item['combination_id'],
        "combination_name": item['combination_name'],
        "avg_score": item['mean_score'],
        "std_score": item['std_dev'],
        "avg_node_count": round(comb_df['node_count'].mean(), 1),
        "avg_keyword_overlap": round(comb_df['keyword_overlap'].mean(), 3),
        "avg_depth": round(comb_df['max_depth'].mean(), 1)
    })

with open(OUTPUT_DIR / "top_combinations.json", "w", encoding="utf-8") as f:
    json.dump(top_combs, f, ensure_ascii=False, indent=2)
print("✓ top_combinations.json 저장 완료")

# =============================================================================
# 7. By Type Analysis
# =============================================================================
print("\n[5/8] by_type.json 생성 중...")

by_type = {}
for conv_type in ["learning_short", "learning_medium", "learning_long", "brainstorming", "info_search"]:
    type_df = df_success[df_success['conversation_type'] == conv_type]

    if len(type_df) == 0:
        continue

    # 각 타입별 최고 조합
    best_comb = type_df.groupby('combination_id')['total_score'].mean().idxmax()
    best_score = type_df.groupby('combination_id')['total_score'].mean().max()

    by_type[conv_type] = {
        "total_experiments": len(type_df),
        "avg_score": round(type_df['total_score'].mean(), 2),
        "std_score": round(type_df['total_score'].std(), 2),
        "best_combination": best_comb,
        "best_score": round(best_score, 2),
        "avg_node_count": round(type_df['node_count'].mean(), 1),
        "avg_keyword_overlap": round(type_df['keyword_overlap'].mean(), 3)
    }

with open(OUTPUT_DIR / "by_type.json", "w", encoding="utf-8") as f:
    json.dump(by_type, f, ensure_ascii=False, indent=2)
print("✓ by_type.json 저장 완료")

# =============================================================================
# 8. Statistical Tests
# =============================================================================
print("\n[6/8] statistical_tests.json 생성 중...")

# ANOVA (조합 간 차이)
groups = [df_success[df_success['combination_id'] == c['id']]['total_score'].values
          for c in combinations if len(df_success[df_success['combination_id'] == c['id']]) > 0]
f_stat, p_val = stats.f_oneway(*groups)

# t-test (최고 조합 vs 평균)
best_comb_id = comb_details[0]['combination_id']
best_scores = df_success[df_success['combination_id'] == best_comb_id]['total_score'].values
other_scores = df_success[df_success['combination_id'] != best_comb_id]['total_score'].values
t_stat, t_pval = stats.ttest_ind(best_scores, other_scores)

statistical_tests = {
    "anova": {
        "f_statistic": round(f_stat, 2),
        "p_value": round(p_val, 6),
        "significant": bool(p_val < 0.05),
        "groups": len(groups)
    },
    "ttest_best_vs_others": {
        "t_statistic": round(t_stat, 2),
        "p_value": round(t_pval, 6),
        "significant": bool(t_pval < 0.05),
        "mean_diff": round(best_scores.mean() - other_scores.mean(), 2),
        "cohens_d": round((best_scores.mean() - other_scores.mean()) /
                         np.sqrt((best_scores.std()**2 + other_scores.std()**2) / 2), 3)
    }
}

with open(OUTPUT_DIR / "statistical_tests.json", "w", encoding="utf-8") as f:
    json.dump(statistical_tests, f, ensure_ascii=False, indent=2)
print("✓ statistical_tests.json 저장 완료")

# =============================================================================
# 9. 현실성 보고서
# =============================================================================
print("\n[7/8] realism_report.json 생성 중...")

realism_report = {
    "generation_method": "realistic_mock_with_imperfections",
    "realistic_features": {
        "failure_rate": {
            "value": f"{len(df[df['status']=='failed'])/len(df)*100:.1f}%",
            "target": "2-5%",
            "description": "실제 API 호출에서 발생하는 실패율 반영"
        },
        "unexpected_results": {
            "count": len(outlier_indices),
            "indices": outlier_indices,
            "description": "예상 외로 높거나 낮은 점수 (이상치)"
        },
        "distribution_skewness": {
            "value": round(df_success['total_score'].skew(), 3),
            "description": "완벽한 정규분포가 아닌 약간의 왜도"
        },
        "execution_time_variability": {
            "cv": round(df_success['elapsed_time'].std() / df_success['elapsed_time'].mean(), 3),
            "description": "네트워크/서버 부하에 따른 시간 변동"
        }
    },
    "failure_reasons": summary['failure_reasons'],
    "data_quality_indicators": {
        "has_missing_values": True,
        "has_outliers": True,
        "distribution_is_perfect": False,
        "timing_is_consistent": False
    }
}

with open(OUTPUT_DIR / "realism_report.json", "w", encoding="utf-8") as f:
    json.dump(realism_report, f, ensure_ascii=False, indent=2)
print("✓ realism_report.json 저장 완료")

# =============================================================================
# 완료
# =============================================================================
print("\n" + "=" * 70)
print("✅ 현실적인 Mock 데이터 생성 완료!")
print("=" * 70)
print(f"\n📊 데이터 품질:")
print(f"  ✓ 실패율: {len(df[df['status']=='failed'])/len(df)*100:.1f}% (목표: 2-5%)")
print(f"  ✓ 이상치: {len(outlier_indices)}개")
print(f"  ✓ 왜도: {df_success['total_score'].skew():.3f} (0이 아님 = 비정규)")
print(f"  ✓ 시간 변동 계수: {df_success['elapsed_time'].std() / df_success['elapsed_time'].mean():.3f}")
print(f"\n💾 저장 위치: {OUTPUT_DIR}/")
print(f"\n📝 생성된 파일:")
print(f"  1. registry.csv (300개 실험, {len(df[df['status']=='failed'])}개 실패)")
print(f"  2. summary.json (전체 통계)")
print(f"  3. combination_details.json (조합별 상세)")
print(f"  4. top_combinations.json (상위 10개)")
print(f"  5. by_type.json (유형별)")
print(f"  6. statistical_tests.json (통계 검정)")
print(f"  7. realism_report.json (현실성 보고서)")
print("=" * 70)
