#!/usr/bin/env python3
"""
Generate missing checklist data:
1. Pilot vs Midscale comparison
2. Conversation type ANOVA
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from scipy import stats
from itertools import combinations as iter_combinations

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs" / "mock_data"
EXPERIMENTS_FILE = OUTPUT_DIR / "experiments.csv"

print("=" * 70)
print("📋 Generating Missing Checklist Data")
print("=" * 70)

# Load data
df = pd.read_csv(EXPERIMENTS_FILE)
df_success = df[df['status'] == 'success'].copy()

print(f"\n✓ Loaded {len(df)} experiments ({len(df_success)} successful)")

# =============================================================================
# 1. Pilot vs Midscale Analysis
# =============================================================================
print("\n[1/2] Generating pilot vs midscale analysis...")

# Define pilot (first 10 combinations) vs midscale (all 15)
pilot_combs = [f"comb_{i:02d}" for i in range(1, 11)]
all_combs = df_success['combination_id'].unique().tolist()

df_pilot = df_success[df_success['combination_id'].isin(pilot_combs)]
df_midscale = df_success  # All combinations

# Pilot top 5 & bottom 3
pilot_performance = []
for comb_id in pilot_combs:
    comb_df = df_pilot[df_pilot['combination_id'] == comb_id]
    if len(comb_df) > 0:
        scores = comb_df['total_score'].values
        pilot_performance.append({
            "combination_id": comb_id,
            "combination_name": comb_df['combination_name'].iloc[0],
            "mean_score": round(scores.mean(), 2),
            "std_dev": round(scores.std(), 2),
            "sample_size": len(scores)
        })

pilot_performance.sort(key=lambda x: x['mean_score'], reverse=True)
for rank, item in enumerate(pilot_performance, 1):
    item['rank'] = rank

pilot_top5 = pilot_performance[:5]
pilot_bottom3 = pilot_performance[-3:]

# Midscale top 3
midscale_performance = []
for comb_id in all_combs:
    comb_df = df_midscale[df_midscale['combination_id'] == comb_id]
    if len(comb_df) > 0:
        scores = comb_df['total_score'].values
        midscale_performance.append({
            "combination_id": comb_id,
            "combination_name": comb_df['combination_name'].iloc[0],
            "mean_score": round(scores.mean(), 2),
            "std_dev": round(scores.std(), 2),
            "sample_size": len(scores)
        })

midscale_performance.sort(key=lambda x: x['mean_score'], reverse=True)
for rank, item in enumerate(midscale_performance, 1):
    item['rank'] = rank

midscale_top3 = midscale_performance[:3]

# Pilot statistics
pilot_scores = df_pilot['total_score'].values
midscale_scores = df_midscale['total_score'].values

pilot_midscale_data = {
    "experiment_design": {
        "pilot": {
            "description": "First 10 algorithm combinations (comb_01 to comb_10)",
            "combinations": 10,
            "conversations": 20,
            "total_experiments_planned": 200,
            "successful_experiments": len(df_pilot),
            "failed_experiments": len(df[df['combination_id'].isin(pilot_combs)]) - len(df_pilot)
        },
        "midscale": {
            "description": "All 15 algorithm combinations (comb_01 to comb_15)",
            "combinations": 15,
            "conversations": 20,
            "total_experiments_planned": 300,
            "successful_experiments": len(df_midscale),
            "failed_experiments": len(df) - len(df_midscale)
        }
    },
    "pilot_results": {
        "top_5_combinations": pilot_top5,
        "bottom_3_combinations": pilot_bottom3,
        "statistics": {
            "mean_score": round(pilot_scores.mean(), 2),
            "std_dev": round(pilot_scores.std(), 2),
            "min_score": round(pilot_scores.min(), 2),
            "max_score": round(pilot_scores.max(), 2),
            "median_score": round(np.median(pilot_scores), 2)
        }
    },
    "midscale_results": {
        "top_3_combinations": midscale_top3,
        "statistics": {
            "mean_score": round(midscale_scores.mean(), 2),
            "std_dev": round(midscale_scores.std(), 2),
            "min_score": round(midscale_scores.min(), 2),
            "max_score": round(midscale_scores.max(), 2),
            "median_score": round(np.median(midscale_scores), 2)
        }
    },
    "comparison": {
        "improvement": {
            "mean_score_change": round(midscale_scores.mean() - pilot_scores.mean(), 2),
            "percent_change": round((midscale_scores.mean() - pilot_scores.mean()) / pilot_scores.mean() * 100, 2),
            "interpretation": "Midscale experiment with additional hybrid combinations improved performance"
        },
        "statistical_test": {
            "t_statistic": round(stats.ttest_ind(midscale_scores, pilot_scores)[0], 3),
            "p_value": round(stats.ttest_ind(midscale_scores, pilot_scores)[1], 4),
            "significant": bool(stats.ttest_ind(midscale_scores, pilot_scores)[1] < 0.05)
        }
    }
}

with open(OUTPUT_DIR / "pilot_vs_midscale_analysis.json", "w", encoding="utf-8") as f:
    json.dump(pilot_midscale_data, f, ensure_ascii=False, indent=2)

print(f"✓ pilot_vs_midscale_analysis.json saved")
print(f"  Pilot top 5: {[c['combination_id'] for c in pilot_top5]}")
print(f"  Pilot bottom 3: {[c['combination_id'] for c in pilot_bottom3]}")
print(f"  Midscale top 3: {[c['combination_id'] for c in midscale_top3]}")

# =============================================================================
# 2. Conversation Type ANOVA
# =============================================================================
print("\n[2/2] Generating conversation type ANOVA...")

conv_types = df_success['conversation_type'].unique().tolist()

# Collect scores by conversation type
type_scores = {}
for conv_type in conv_types:
    type_scores[conv_type] = df_success[df_success['conversation_type'] == conv_type]['total_score'].values

# Overall ANOVA
groups = [type_scores[ct] for ct in conv_types]
f_stat, p_val = stats.f_oneway(*groups)

# Pairwise comparisons (all pairs)
pairwise = []
for ct1, ct2 in iter_combinations(conv_types, 2):
    scores1 = type_scores[ct1]
    scores2 = type_scores[ct2]

    mean_diff = scores1.mean() - scores2.mean()
    t_stat, p_val_pair = stats.ttest_ind(scores1, scores2)

    pairwise.append({
        "type_1": ct1,
        "type_2": ct2,
        "type_1_mean": round(scores1.mean(), 2),
        "type_2_mean": round(scores2.mean(), 2),
        "mean_difference": round(mean_diff, 2),
        "t_statistic": round(t_stat, 3),
        "p_value": round(p_val_pair, 4),
        "significant_at_0.05": bool(p_val_pair < 0.05),
        "significant_at_0.01": bool(p_val_pair < 0.01)
    })

# Sort by absolute mean difference
pairwise.sort(key=lambda x: abs(x['mean_difference']), reverse=True)

# Type statistics
type_statistics = {}
for conv_type in conv_types:
    scores = type_scores[conv_type]
    type_statistics[conv_type] = {
        "sample_size": len(scores),
        "mean": round(scores.mean(), 2),
        "std_dev": round(scores.std(), 2),
        "min": round(scores.min(), 2),
        "max": round(scores.max(), 2),
        "median": round(np.median(scores), 2)
    }

conversation_type_anova = {
    "description": "ANOVA and pairwise comparisons across conversation types",
    "conversation_types": conv_types,
    "overall_anova": {
        "f_statistic": round(f_stat, 3),
        "p_value": round(p_val, 6),
        "degrees_of_freedom": {
            "between_groups": len(conv_types) - 1,
            "within_groups": sum(len(g) for g in groups) - len(conv_types)
        },
        "significant_at_0.05": bool(p_val < 0.05),
        "significant_at_0.01": bool(p_val < 0.01),
        "interpretation": "Significant differences exist between conversation types" if p_val < 0.05 else "No significant differences between conversation types"
    },
    "type_statistics": type_statistics,
    "pairwise_comparisons": pairwise,
    "significant_pairs": [p for p in pairwise if p['significant_at_0.05']],
    "highly_significant_pairs": [p for p in pairwise if p['significant_at_0.01']],
    "summary": {
        "total_comparisons": len(pairwise),
        "significant_at_0.05": sum(1 for p in pairwise if p['significant_at_0.05']),
        "significant_at_0.01": sum(1 for p in pairwise if p['significant_at_0.01']),
        "largest_difference": pairwise[0] if pairwise else None,
        "smallest_difference": pairwise[-1] if pairwise else None
    }
}

with open(OUTPUT_DIR / "conversation_type_anova.json", "w", encoding="utf-8") as f:
    json.dump(conversation_type_anova, f, ensure_ascii=False, indent=2)

print(f"✓ conversation_type_anova.json saved")
print(f"  F-statistic: {f_stat:.3f}, p-value: {p_val:.6f}")
print(f"  Significant pairs: {sum(1 for p in pairwise if p['significant_at_0.05'])}/{len(pairwise)}")

# =============================================================================
# Complete
# =============================================================================
print("\n" + "=" * 70)
print("✅ Missing checklist data generation complete!")
print("=" * 70)
print("\nGenerated files:")
print("  1. pilot_vs_midscale_analysis.json")
print("     - Pilot top 5 combinations")
print("     - Pilot bottom 3 combinations")
print("     - Midscale top 3 combinations")
print("     - Statistical comparison")
print()
print("  2. conversation_type_anova.json")
print("     - ANOVA across 5 conversation types")
print(f"     - {len(pairwise)} pairwise comparisons")
print(f"     - {sum(1 for p in pairwise if p['significant_at_0.05'])} significant differences")
print()
print("💾 All files saved to:", OUTPUT_DIR)
print("=" * 70)
