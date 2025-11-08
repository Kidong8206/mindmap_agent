#!/usr/bin/env python3
"""
Claude vs GPT-4 실험 결과 비교 분석 스크립트

Usage:
    python3 analyze_comparison.py

Input Files:
    - outputs/claude_data/experiments_claude.csv
    - outputs/gpt_data/experiments_gpt.csv

Output Files:
    - outputs/comparison/comparison_summary.json
    - outputs/comparison/statistical_tests.json
    - outputs/comparison/comparison_report.md
    - outputs/comparison/figures/*.png
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 경로 설정
BASE_DIR = Path(__file__).parent
CLAUDE_DATA = BASE_DIR / "outputs" / "claude_data" / "experiments_claude.csv"
GPT_DATA = BASE_DIR / "outputs" / "gpt_data" / "experiments_gpt.csv"
OUTPUT_DIR = BASE_DIR / "outputs" / "comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "figures").mkdir(exist_ok=True)

print("=" * 70)
print("📊 Claude vs GPT-4 비교 분석")
print("=" * 70)

# =============================================================================
# 1. 데이터 로드
# =============================================================================

print("\n[1/7] 데이터 로드 중...")

try:
    df_claude = pd.read_csv(CLAUDE_DATA)
    df_gpt = pd.read_csv(GPT_DATA)
    print(f"  ✓ Claude 데이터: {len(df_claude)}개 실험")
    print(f"  ✓ GPT 데이터: {len(df_gpt)}개 실험")
except FileNotFoundError as e:
    print(f"  ✗ 에러: {e}")
    print("\n실험 파일이 없습니다. 먼저 실험을 실행하세요:")
    print("  1. Colab에서 Claude 실험 실행")
    print("  2. Colab에서 GPT 실험 실행")
    print("  3. 결과 파일을 다운로드하여 outputs/ 폴더에 저장")
    exit(1)

# 데이터 검증
assert len(df_claude) == len(df_gpt), "실험 개수가 다릅니다!"
assert all(df_claude['combination_id'] == df_gpt['combination_id']), "조합 순서가 다릅니다!"
assert all(df_claude['conversation_id'] == df_gpt['conversation_id']), "대화 순서가 다릅니다!"

# API 레이블 추가
df_claude['api'] = 'Claude'
df_gpt['api'] = 'GPT-4'

# 병합
df_combined = pd.concat([df_claude, df_gpt], ignore_index=True)

# =============================================================================
# 2. 기술 통계
# =============================================================================

print("\n[2/7] 기술 통계 계산 중...")

def get_descriptive_stats(df):
    """기술 통계 계산"""
    success_df = df[df['status'] == 'success']

    if len(success_df) == 0:
        return {
            "count": 0,
            "success_rate": 0.0,
            "mean": None,
            "std": None,
            "min": None,
            "q1": None,
            "median": None,
            "q3": None,
            "max": None,
            "skewness": None,
            "kurtosis": None
        }

    scores = success_df['total_score']

    return {
        "count": len(success_df),
        "success_rate": round(len(success_df) / len(df) * 100, 2),
        "mean": round(scores.mean(), 2),
        "std": round(scores.std(), 2),
        "min": round(scores.min(), 2),
        "q1": round(scores.quantile(0.25), 2),
        "median": round(scores.median(), 2),
        "q3": round(scores.quantile(0.75), 2),
        "max": round(scores.max(), 2),
        "skewness": round(stats.skew(scores), 3),
        "kurtosis": round(stats.kurtosis(scores), 3)
    }

claude_stats = get_descriptive_stats(df_claude)
gpt_stats = get_descriptive_stats(df_gpt)

print(f"\n  Claude 통계:")
print(f"    성공률: {claude_stats['success_rate']}%")
print(f"    평균 점수: {claude_stats['mean']} (± {claude_stats['std']})")
print(f"    중앙값: {claude_stats['median']}")
print(f"    범위: [{claude_stats['min']}, {claude_stats['max']}]")

print(f"\n  GPT-4 통계:")
print(f"    성공률: {gpt_stats['success_rate']}%")
print(f"    평균 점수: {gpt_stats['mean']} (± {gpt_stats['std']})")
print(f"    중앙값: {gpt_stats['median']}")
print(f"    범위: [{gpt_stats['min']}, {gpt_stats['max']}]")

# =============================================================================
# 3. 추론 통계
# =============================================================================

print("\n[3/7] 추론 통계 검정 중...")

# 성공한 실험만 필터링
claude_success = df_claude[df_claude['status'] == 'success']
gpt_success = df_gpt[df_gpt['status'] == 'success']

statistical_tests = {}

# 3.1 Independent t-test (전체 비교)
if len(claude_success) > 0 and len(gpt_success) > 0:
    claude_scores = claude_success['total_score']
    gpt_scores = gpt_success['total_score']

    t_stat, p_value = stats.ttest_ind(claude_scores, gpt_scores)

    # Cohen's d (효과 크기)
    def cohens_d(group1, group2):
        n1, n2 = len(group1), len(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
        return (np.mean(group1) - np.mean(group2)) / pooled_std

    d = cohens_d(claude_scores, gpt_scores)

    # 효과 크기 해석
    if abs(d) < 0.2:
        effect_interpretation = "작은 효과"
    elif abs(d) < 0.5:
        effect_interpretation = "중간 효과"
    elif abs(d) < 0.8:
        effect_interpretation = "큰 효과"
    else:
        effect_interpretation = "매우 큰 효과"

    statistical_tests['overall_ttest'] = {
        "test_name": "Independent Samples t-test",
        "claude_mean": round(claude_scores.mean(), 2),
        "gpt_mean": round(gpt_scores.mean(), 2),
        "difference": round(claude_scores.mean() - gpt_scores.mean(), 2),
        "t_statistic": round(t_stat, 3),
        "p_value": round(p_value, 6),
        "significant": bool(p_value < 0.05),
        "cohens_d": round(d, 3),
        "effect_size_interpretation": effect_interpretation
    }

    print(f"\n  전체 비교 (t-test):")
    print(f"    Claude 평균: {claude_scores.mean():.2f}")
    print(f"    GPT 평균: {gpt_scores.mean():.2f}")
    print(f"    차이: {claude_scores.mean() - gpt_scores.mean():.2f}")
    print(f"    t = {t_stat:.3f}, p = {p_value:.6f}")
    print(f"    Cohen's d = {d:.3f} ({effect_interpretation})")

    if p_value < 0.05:
        winner = "Claude" if claude_scores.mean() > gpt_scores.mean() else "GPT-4"
        print(f"    ✓ {winner}가 통계적으로 유의미하게 우수함 (p < 0.05)")
    else:
        print(f"    ✗ 통계적으로 유의미한 차이 없음 (p ≥ 0.05)")

# 3.2 Chi-square test (실패율 비교)
contingency_table = pd.crosstab(df_combined['api'], df_combined['status'])
chi2, p_chi, dof, expected = stats.chi2_contingency(contingency_table)

statistical_tests['failure_rate_chi2'] = {
    "test_name": "Chi-Square Test (Failure Rate)",
    "claude_failure_rate": round((1 - claude_stats['success_rate']/100) * 100, 2),
    "gpt_failure_rate": round((1 - gpt_stats['success_rate']/100) * 100, 2),
    "chi2_statistic": round(chi2, 3),
    "p_value": round(p_chi, 6),
    "degrees_of_freedom": int(dof),
    "significant": bool(p_chi < 0.05)
}

print(f"\n  실패율 비교 (Chi-Square):")
print(f"    Claude 실패율: {(1-claude_stats['success_rate']/100)*100:.2f}%")
print(f"    GPT 실패율: {(1-gpt_stats['success_rate']/100)*100:.2f}%")
print(f"    χ² = {chi2:.3f}, p = {p_chi:.6f}")

# 3.3 Mann-Whitney U test (실행 시간 비교)
if len(claude_success) > 0 and len(gpt_success) > 0:
    u_stat, p_mann = stats.mannwhitneyu(
        claude_success['execution_time_sec'],
        gpt_success['execution_time_sec'],
        alternative='two-sided'
    )

    statistical_tests['execution_time_mannwhitney'] = {
        "test_name": "Mann-Whitney U Test (Execution Time)",
        "claude_median_time": round(claude_success['execution_time_sec'].median(), 2),
        "gpt_median_time": round(gpt_success['execution_time_sec'].median(), 2),
        "u_statistic": float(u_stat),
        "p_value": round(p_mann, 6),
        "significant": bool(p_mann < 0.05)
    }

    print(f"\n  실행 시간 비교 (Mann-Whitney U):")
    print(f"    Claude 중앙값: {claude_success['execution_time_sec'].median():.2f}초")
    print(f"    GPT 중앙값: {gpt_success['execution_time_sec'].median():.2f}초")
    print(f"    U = {u_stat:.0f}, p = {p_mann:.6f}")

# =============================================================================
# 4. 조합별 비교
# =============================================================================

print("\n[4/7] 조합별 분석 중...")

combination_comparison = []

for comb_id in df_claude['combination_id'].unique():
    claude_comb = df_claude[
        (df_claude['combination_id'] == comb_id) &
        (df_claude['status'] == 'success')
    ]
    gpt_comb = df_gpt[
        (df_gpt['combination_id'] == comb_id) &
        (df_gpt['status'] == 'success')
    ]

    if len(claude_comb) > 0 and len(gpt_comb) > 0:
        claude_mean = claude_comb['total_score'].mean()
        gpt_mean = gpt_comb['total_score'].mean()

        # t-test
        t, p = stats.ttest_ind(claude_comb['total_score'], gpt_comb['total_score'])

        combination_comparison.append({
            "combination_id": comb_id,
            "combination_name": claude_comb.iloc[0]['combination_name'],
            "claude_mean": round(claude_mean, 2),
            "gpt_mean": round(gpt_mean, 2),
            "difference": round(claude_mean - gpt_mean, 2),
            "winner": "Claude" if claude_mean > gpt_mean else "GPT-4",
            "t_statistic": round(t, 3),
            "p_value": round(p, 4),
            "significant": bool(p < 0.05)
        })

print(f"  ✓ {len(combination_comparison)}개 조합 분석 완료")

# 유의미한 차이가 있는 조합 수
sig_count = sum(1 for c in combination_comparison if c['significant'])
print(f"  ✓ 유의미한 차이가 있는 조합: {sig_count}개")

# =============================================================================
# 5. 대화 유형별 비교
# =============================================================================

print("\n[5/7] 대화 유형별 분석 중...")

conversation_type_comparison = []

for conv_type in df_claude['conversation_type'].unique():
    claude_type = df_claude[
        (df_claude['conversation_type'] == conv_type) &
        (df_claude['status'] == 'success')
    ]
    gpt_type = df_gpt[
        (df_gpt['conversation_type'] == conv_type) &
        (df_gpt['status'] == 'success')
    ]

    if len(claude_type) > 0 and len(gpt_type) > 0:
        claude_mean = claude_type['total_score'].mean()
        gpt_mean = gpt_type['total_score'].mean()

        # t-test
        t, p = stats.ttest_ind(claude_type['total_score'], gpt_type['total_score'])

        conversation_type_comparison.append({
            "conversation_type": conv_type,
            "claude_mean": round(claude_mean, 2),
            "gpt_mean": round(gpt_mean, 2),
            "difference": round(claude_mean - gpt_mean, 2),
            "winner": "Claude" if claude_mean > gpt_mean else "GPT-4",
            "t_statistic": round(t, 3),
            "p_value": round(p, 4),
            "significant": bool(p < 0.05)
        })

print(f"  ✓ {len(conversation_type_comparison)}개 유형 분석 완료")

# =============================================================================
# 6. 시각화
# =============================================================================

print("\n[6/7] 시각화 생성 중...")

# 6.1 전체 비교 박스플롯
if len(claude_success) > 0 and len(gpt_success) > 0:
    fig, ax = plt.subplots(figsize=(8, 6))

    combined_success = pd.concat([
        claude_success.assign(api='Claude'),
        gpt_success.assign(api='GPT-4')
    ])

    ax.boxplot([claude_success['total_score'], gpt_success['total_score']],
               labels=['Claude', 'GPT-4'])
    ax.set_ylabel('Total Score')
    ax.set_title('Claude vs GPT-4: Overall Performance')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "figures" / "overall_comparison_boxplot.png", dpi=300)
    plt.close()
    print("  ✓ overall_comparison_boxplot.png")

# 6.2 조합별 비교 히트맵
if combination_comparison:
    pivot_data = []
    for comp in combination_comparison:
        pivot_data.append({
            'Combination': comp['combination_id'],
            'Claude': comp['claude_mean'],
            'GPT-4': comp['gpt_mean']
        })

    df_pivot = pd.DataFrame(pivot_data).set_index('Combination')

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(df_pivot, annot=True, fmt='.2f', cmap='RdYlGn', center=75,
                vmin=60, vmax=90, ax=ax)
    ax.set_title('Performance by Combination')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "figures" / "combination_heatmap.png", dpi=300)
    plt.close()
    print("  ✓ combination_heatmap.png")

# 6.3 대화 유형별 비교 바 차트
if conversation_type_comparison:
    fig, ax = plt.subplots(figsize=(10, 6))

    types = [c['conversation_type'] for c in conversation_type_comparison]
    claude_means = [c['claude_mean'] for c in conversation_type_comparison]
    gpt_means = [c['gpt_mean'] for c in conversation_type_comparison]

    x = np.arange(len(types))
    width = 0.35

    ax.bar(x - width/2, claude_means, width, label='Claude', color='#4A90E2')
    ax.bar(x + width/2, gpt_means, width, label='GPT-4', color='#50E3C2')

    ax.set_ylabel('Average Score')
    ax.set_title('Performance by Conversation Type')
    ax.set_xticks(x)
    ax.set_xticklabels(types, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "figures" / "conversation_type_comparison.png", dpi=300)
    plt.close()
    print("  ✓ conversation_type_comparison.png")

# =============================================================================
# 7. 결과 저장
# =============================================================================

print("\n[7/7] 결과 저장 중...")

# 7.1 요약 JSON
summary = {
    "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "descriptive_statistics": {
        "claude": claude_stats,
        "gpt": gpt_stats
    },
    "statistical_tests": statistical_tests,
    "combination_comparison": combination_comparison,
    "conversation_type_comparison": conversation_type_comparison
}

with open(OUTPUT_DIR / "comparison_summary.json", 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("  ✓ comparison_summary.json")

# 7.2 통계 검정 JSON
with open(OUTPUT_DIR / "statistical_tests.json", 'w', encoding='utf-8') as f:
    json.dump(statistical_tests, f, ensure_ascii=False, indent=2)

print("  ✓ statistical_tests.json")

# 7.3 Markdown 보고서
report = f"""# Claude vs GPT-4 비교 분석 보고서

**생성 일시**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 1. 전체 비교

### 1.1 기술 통계

| 지표 | Claude | GPT-4 |
|------|--------|-------|
| 성공률 | {claude_stats['success_rate']}% | {gpt_stats['success_rate']}% |
| 평균 점수 | {claude_stats['mean']} | {gpt_stats['mean']} |
| 표준편차 | {claude_stats['std']} | {gpt_stats['std']} |
| 중앙값 | {claude_stats['median']} | {gpt_stats['median']} |
| 최소값 | {claude_stats['min']} | {gpt_stats['min']} |
| 최대값 | {claude_stats['max']} | {gpt_stats['max']} |

### 1.2 통계 검정

**Independent t-test**
- Claude 평균: {statistical_tests.get('overall_ttest', {}).get('claude_mean', 'N/A')}
- GPT-4 평균: {statistical_tests.get('overall_ttest', {}).get('gpt_mean', 'N/A')}
- 차이: {statistical_tests.get('overall_ttest', {}).get('difference', 'N/A')}
- t-통계량: {statistical_tests.get('overall_ttest', {}).get('t_statistic', 'N/A')}
- p-value: {statistical_tests.get('overall_ttest', {}).get('p_value', 'N/A')}
- Cohen's d: {statistical_tests.get('overall_ttest', {}).get('cohens_d', 'N/A')} ({statistical_tests.get('overall_ttest', {}).get('effect_size_interpretation', 'N/A')})

**결론**: {"통계적으로 유의미한 차이 있음" if statistical_tests.get('overall_ttest', {}).get('significant', False) else "통계적으로 유의미한 차이 없음"}

---

## 2. 조합별 비교

### 상위 5개 조합 (Claude 우세)

| 조합 ID | 조합명 | Claude | GPT-4 | 차이 | p-value |
|---------|--------|--------|-------|------|---------|
"""

# 조합별 정렬 (Claude 우세 순)
sorted_combs = sorted(combination_comparison, key=lambda x: x['difference'], reverse=True)

for comp in sorted_combs[:5]:
    report += f"| {comp['combination_id']} | {comp['combination_name']} | {comp['claude_mean']} | {comp['gpt_mean']} | {comp['difference']:+.2f} | {comp['p_value']:.4f} |\n"

report += "\n### 하위 5개 조합 (GPT-4 우세)\n\n"
report += "| 조합 ID | 조합명 | Claude | GPT-4 | 차이 | p-value |\n"
report += "|---------|--------|--------|-------|------|---------|\n"

for comp in sorted_combs[-5:]:
    report += f"| {comp['combination_id']} | {comp['combination_name']} | {comp['claude_mean']} | {comp['gpt_mean']} | {comp['difference']:+.2f} | {comp['p_value']:.4f} |\n"

report += f"""

---

## 3. 대화 유형별 비교

| 유형 | Claude | GPT-4 | 차이 | p-value |
|------|--------|-------|------|---------|
"""

for comp in conversation_type_comparison:
    report += f"| {comp['conversation_type']} | {comp['claude_mean']} | {comp['gpt_mean']} | {comp['difference']:+.2f} | {comp['p_value']:.4f} |\n"

report += f"""

---

## 4. 실행 시간 및 실패율

### 실행 시간

- Claude 중앙값: {statistical_tests.get('execution_time_mannwhitney', {}).get('claude_median_time', 'N/A')}초
- GPT-4 중앙값: {statistical_tests.get('execution_time_mannwhitney', {}).get('gpt_median_time', 'N/A')}초
- Mann-Whitney U = {statistical_tests.get('execution_time_mannwhitney', {}).get('u_statistic', 'N/A')}, p = {statistical_tests.get('execution_time_mannwhitney', {}).get('p_value', 'N/A')}

### 실패율

- Claude: {statistical_tests.get('failure_rate_chi2', {}).get('claude_failure_rate', 'N/A')}%
- GPT-4: {statistical_tests.get('failure_rate_chi2', {}).get('gpt_failure_rate', 'N/A')}%
- Chi-Square χ² = {statistical_tests.get('failure_rate_chi2', {}).get('chi2_statistic', 'N/A')}, p = {statistical_tests.get('failure_rate_chi2', {}).get('p_value', 'N/A')}

---

## 5. 결론

"""

# 결론 자동 생성
if statistical_tests.get('overall_ttest', {}).get('significant', False):
    winner = "Claude" if statistical_tests['overall_ttest']['claude_mean'] > statistical_tests['overall_ttest']['gpt_mean'] else "GPT-4"
    report += f"**{winner}**가 전체적으로 통계적으로 유의미하게 우수한 성능을 보였습니다 (p < 0.05).\n\n"
else:
    report += "두 API 간 전체 성능에 **통계적으로 유의미한 차이가 없습니다** (p ≥ 0.05).\n\n"

# 조합별 결과
claude_wins = sum(1 for c in combination_comparison if c['difference'] > 0)
gpt_wins = sum(1 for c in combination_comparison if c['difference'] < 0)
report += f"조합별 분석 결과:\n"
report += f"- Claude 우세: {claude_wins}개 조합\n"
report += f"- GPT-4 우세: {gpt_wins}개 조합\n\n"

report += """---

**참고 사항**: 이 보고서는 자동 생성되었습니다.
"""

with open(OUTPUT_DIR / "comparison_report.md", 'w', encoding='utf-8') as f:
    f.write(report)

print("  ✓ comparison_report.md")

# =============================================================================
# 완료
# =============================================================================

print("\n" + "=" * 70)
print("✅ 비교 분석 완료!")
print("=" * 70)
print(f"\n📁 결과 위치: {OUTPUT_DIR}")
print(f"\n생성된 파일:")
print(f"  - comparison_summary.json (전체 요약)")
print(f"  - statistical_tests.json (통계 검정 결과)")
print(f"  - comparison_report.md (Markdown 보고서)")
print(f"  - figures/overall_comparison_boxplot.png")
print(f"  - figures/combination_heatmap.png")
print(f"  - figures/conversation_type_comparison.png")
print(f"\n다음 단계:")
print(f"  1. comparison_report.md 확인")
print(f"  2. 그림 파일 확인")
print(f"  3. 보고서에 결과 추가")
print()
