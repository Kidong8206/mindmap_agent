#!/usr/bin/env python3
"""결과 분석 모듈 - registry.csv → 통계 및 순위"""
import json
import pandas as pd
from pathlib import Path

class ResultAnalyzer:
    def __init__(self):
        self.registry_file = Path("../outputs/registry.csv")
        self.output_dir = Path("../outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    def analyze(self):
        """전체 분석 실행"""
        if not self.registry_file.exists():
            print(f"⚠ registry.csv 없음: {self.registry_file}")
            return
        
        print("=" * 60)
        print("실험 결과 분석")
        print("=" * 60)
        
        # 데이터 로드
        df = pd.read_csv(self.registry_file)
        print(f"\n총 실험 수: {len(df)}개")
        
        # 성공한 실험만 필터링
        success_df = df[df["status"] == "success"]
        print(f"성공한 실험: {len(success_df)}개 ({len(success_df)/len(df)*100:.1f}%)")
        
        if len(success_df) == 0:
            print("⚠ 성공한 실험이 없습니다.")
            return
        
        # 1. 전체 통계
        summary = self._compute_summary(success_df)
        self._save_json(summary, "summary.json")
        self._print_summary(summary)
        
        # 2. 조합별 순위
        top_combinations = self._compute_top_combinations(success_df)
        self._save_json(top_combinations, "top_combinations.json")
        self._print_top_combinations(top_combinations)
        
        # 3. 대화 유형별 분석
        by_type = self._compute_by_type(success_df)
        self._save_json(by_type, "by_type.json")
        self._print_by_type(by_type)
        
        print("\n" + "=" * 60)
        print("분석 완료!")
        print(f"출력 파일:")
        print(f"  - {self.output_dir}/summary.json")
        print(f"  - {self.output_dir}/top_combinations.json")
        print(f"  - {self.output_dir}/by_type.json")
        print("=" * 60)
    
    def _compute_summary(self, df):
        """전체 통계"""
        return {
            "total_experiments": len(df),
            "metrics": {
                "total_score": {
                    "mean": float(df["total_score"].mean()),
                    "std": float(df["total_score"].std()),
                    "min": float(df["total_score"].min()),
                    "max": float(df["total_score"].max())
                },
                "node_count": {
                    "mean": float(df["node_count"].mean()),
                    "std": float(df["node_count"].std()),
                    "min": int(df["node_count"].min()),
                    "max": int(df["node_count"].max())
                },
                "keyword_overlap": {
                    "mean": float(df["keyword_overlap"].mean()),
                    "std": float(df["keyword_overlap"].std())
                },
                "max_depth": {
                    "mean": float(df["max_depth"].mean()),
                    "std": float(df["max_depth"].std())
                }
            },
            "avg_elapsed_time": float(df["elapsed_time"].mean())
        }
    
    def _compute_top_combinations(self, df):
        """조합별 평균 점수 및 순위"""
        grouped = df.groupby("combination_name").agg({
            "total_score": ["mean", "std", "count"],
            "node_count": "mean",
            "keyword_overlap": "mean",
            "max_depth": "mean"
        }).round(2)
        
        grouped.columns = ["avg_score", "std_score", "count", "avg_nodes", "avg_overlap", "avg_depth"]
        grouped = grouped.sort_values("avg_score", ascending=False)
        
        # Top 10
        top_10 = []
        for i, (name, row) in enumerate(grouped.head(10).iterrows(), 1):
            top_10.append({
                "rank": i,
                "combination": name,
                "avg_score": float(row["avg_score"]),
                "std_score": float(row["std_score"]),
                "experiments": int(row["count"]),
                "avg_nodes": float(row["avg_nodes"]),
                "avg_overlap": float(row["avg_overlap"]),
                "avg_depth": float(row["avg_depth"])
            })
        
        return {
            "top_10": top_10,
            "all_combinations": grouped.to_dict("index")
        }
    
    def _compute_by_type(self, df):
        """대화 유형별 최적 조합"""
        # 대화 ID에서 유형 추정
        def get_type(conv_id):
            num = int(conv_id.replace("conv_", ""))
            if 1 <= num <= 3:
                return "learning_short"
            elif 4 <= num <= 7:
                return "learning_medium"
            elif 8 <= num <= 10:
                return "learning_long"
            elif 11 <= num <= 15:
                return "brainstorming"
            else:
                return "info_search"
        
        df["conv_type"] = df["conversation_id"].apply(get_type)
        
        by_type = {}
        for conv_type in df["conv_type"].unique():
            type_df = df[df["conv_type"] == conv_type]
            
            # 유형별 최고 조합
            best = type_df.groupby("combination_name")["total_score"].mean().sort_values(ascending=False)
            
            by_type[conv_type] = {
                "experiments": len(type_df),
                "avg_score": float(type_df["total_score"].mean()),
                "best_combination": best.index[0] if len(best) > 0 else None,
                "best_score": float(best.iloc[0]) if len(best) > 0 else None,
                "top_3": [
                    {"combination": name, "score": float(score)}
                    for name, score in best.head(3).items()
                ]
            }
        
        return by_type
    
    def _save_json(self, data, filename):
        """JSON 저장"""
        output_file = self.output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _print_summary(self, summary):
        """전체 통계 출력"""
        print("\n### 전체 통계")
        print(f"총 실험: {summary['total_experiments']}개")
        print(f"\n평균 점수: {summary['metrics']['total_score']['mean']:.2f} ± {summary['metrics']['total_score']['std']:.2f}")
        print(f"점수 범위: {summary['metrics']['total_score']['min']:.2f} ~ {summary['metrics']['total_score']['max']:.2f}")
        print(f"평균 노드: {summary['metrics']['node_count']['mean']:.1f}개")
        print(f"평균 키워드 중복도: {summary['metrics']['keyword_overlap']['mean']:.2f}%")
    
    def _print_top_combinations(self, top_combinations):
        """Top 10 출력"""
        print("\n### Top 10 조합")
        for item in top_combinations["top_10"]:
            print(f"{item['rank']:2d}. {item['combination']:30s} - {item['avg_score']:.2f}점 ({item['experiments']}회)")
    
    def _print_by_type(self, by_type):
        """유형별 분석 출력"""
        print("\n### 대화 유형별 최적 조합")
        for conv_type, data in by_type.items():
            print(f"\n[{conv_type}]")
            print(f"  평균 점수: {data['avg_score']:.2f}")
            print(f"  최적 조합: {data['best_combination']} ({data['best_score']:.2f}점)")

if __name__ == "__main__":
    analyzer = ResultAnalyzer()
    analyzer.analyze()
