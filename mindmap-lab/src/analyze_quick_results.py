#!/usr/bin/env python3
"""빠른 검증 실험 결과 분석"""
import json
import pandas as pd
from pathlib import Path

class QuickAnalyzer:
    def __init__(self):
        self.registry_file = Path("../outputs/quick_test/quick_registry.csv")
        self.output_dir = Path("../outputs/quick_test")
    
    def analyze(self):
        if not self.registry_file.exists():
            print(f"⚠ quick_registry.csv 없음")
            return
        
        print("=" * 60)
        print("빠른 검증 실험 결과 분석")
        print("=" * 60)
        
        df = pd.read_csv(self.registry_file)
        print(f"\n총 실험: {len(df)}개")
        
        success_df = df[df["status"] == "success"]
        print(f"성공: {len(success_df)}개 ({len(success_df)/len(df)*100:.1f}%)")
        
        if len(success_df) == 0:
            print("⚠ 성공한 실험이 없습니다.")
            return
        
        # 기본 통계
        print(f"\n### 기본 통계")
        print(f"평균 점수: {success_df['total_score'].mean():.2f} ± {success_df['total_score'].std():.2f}")
        print(f"점수 범위: {success_df['total_score'].min():.2f} ~ {success_df['total_score'].max():.2f}")
        print(f"평균 노드: {success_df['node_count'].mean():.1f}개")
        print(f"평균 키워드 중복도: {success_df['keyword_overlap'].mean():.2f}%")
        
        # 조합별 순위
        print(f"\n### 조합별 순위 (Top 5)")
        top_combinations = success_df.groupby("combination_name")["total_score"].agg(['mean', 'count']).round(2)
        top_combinations = top_combinations.sort_values("mean", ascending=False)
        
        for i, (name, row) in enumerate(top_combinations.iterrows(), 1):
            print(f"{i}. {name:30s} - {row['mean']:.2f}점 ({int(row['count'])}회)")
        
        # 대화별 결과
        print(f"\n### 대화별 평균 점수")
        conv_scores = success_df.groupby("conversation_id")["total_score"].mean().round(2).sort_values(ascending=False)
        for conv_id, score in conv_scores.items():
            print(f"  {conv_id}: {score:.2f}")
        
        # JSON 저장
        summary = {
            "total_experiments": len(df),
            "success_count": len(success_df),
            "success_rate": len(success_df)/len(df),
            "avg_score": float(success_df['total_score'].mean()),
            "std_score": float(success_df['total_score'].std()),
            "min_score": float(success_df['total_score'].min()),
            "max_score": float(success_df['total_score'].max()),
            "top_combination": top_combinations.index[0],
            "top_score": float(top_combinations.iloc[0]['mean'])
        }
        
        with open(self.output_dir / "quick_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("분석 완료!")
        print(f"요약 파일: {self.output_dir / 'quick_summary.json'}")
        print("=" * 60)
        
        print("\n✅ 검증 결과가 정상이면 전체 실험을 실행하세요:")
        print("   cd .. && ./run_full_experiment.sh")

if __name__ == "__main__":
    analyzer = QuickAnalyzer()
    analyzer.analyze()
