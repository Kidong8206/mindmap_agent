#!/usr/bin/env python3
"""
빠른 검증용 축소 실험
5개 대화 × 5개 조합 = 25회 (약 30분)
"""
import os
import sys
import time
import yaml
import pandas as pd
from pathlib import Path
from datetime import datetime

from gpt_caller import GPTCaller
from validator import validate_sessions, validate_contexts, validate_keywords, validate_graph
from evaluator import evaluate
from utils import load_jsonl, load_json, save_json

# 축소 실험 설정
QUICK_CONVERSATIONS = [
    "conv_001",  # 학습_짧음 대표
    "conv_004",  # 학습_중간 대표
    "conv_008",  # 학습_긴 대표
    "conv_011",  # 브레인스토밍 대표
    "conv_016"   # 정보검색 대표
]

QUICK_COMBINATIONS = [
    "comb_01",   # simple_hierarchical
    "comb_04",   # detailed_hierarchical
    "comb_07",   # strict_hierarchical
    "comb_10",   # hybrid_s1d2_hier
    "comb_13"    # hybrid_str1d2_radial
]

class QuickLab:
    """축소 실험실 (빠른 검증용)"""
    
    def __init__(self, base_dir="../"):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "data"
        self.prompts_dir = self.base_dir / "prompts"
        self.outputs_dir = self.base_dir / "outputs" / "quick_test"
        self.logs_dir = self.outputs_dir / "logs"
        
        # 디렉토리 생성
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # GPT API 초기화
        self.gpt = GPTCaller()
        
        # 설정 로드
        with open(self.base_dir / "config.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 축소 조합만 필터링
        self.combinations = [c for c in config["combinations"] if c["id"] in QUICK_COMBINATIONS]
        
        # 결과 저장용
        self.results = []
    
    def run_stage1(self, conv_id, version):
        """Stage 1: 세션 분류"""
        print(f"  [Stage 1] 세션 분류 ({version})...")
        
        conv_file = self.data_dir / "conversations" / f"{conv_id}.jsonl"
        conversation = load_jsonl(conv_file)
        
        prompt_file = self.prompts_dir / f"stage1_{version}.txt"
        replacements = {
            "conversation_id": conv_id,
            "conversation": conversation
        }
        
        result = self.gpt.call(str(prompt_file), replacements)
        validate_sessions(result)
        
        output_file = self.data_dir / "sessions" / f"{conv_id}_{version}.json"
        save_json(result, output_file)
        
        return result
    
    def run_stage2(self, conv_id, version, sessions):
        """Stage 2: 맥락 분류"""
        print(f"  [Stage 2] 맥락 분류 ({version})...")
        
        conv_file = self.data_dir / "conversations" / f"{conv_id}.jsonl"
        conversation = load_jsonl(conv_file)
        
        prompt_file = self.prompts_dir / f"stage2_{version}.txt"
        replacements = {
            "conversation_id": conv_id,
            "sessions": sessions["sessions"],
            "conversation": conversation
        }
        
        result = self.gpt.call(str(prompt_file), replacements)
        validate_contexts(result)
        
        output_file = self.data_dir / "contexts" / f"{conv_id}_{version}.json"
        save_json(result, output_file)
        
        return result
    
    def run_stage3(self, conv_id, version, contexts):
        """Stage 3: 키워드 추출"""
        print(f"  [Stage 3] 키워드 추출 ({version})...")
        
        conv_file = self.data_dir / "conversations" / f"{conv_id}.jsonl"
        conversation = load_jsonl(conv_file)
        
        prompt_file = self.prompts_dir / f"stage3_{version}.txt"
        replacements = {
            "conversation_id": conv_id,
            "conversation": conversation,
            "contexts": contexts["contexts"]
        }
        
        result = self.gpt.call(str(prompt_file), replacements)
        validate_keywords(result)
        
        output_file = self.data_dir / "keywords" / f"{conv_id}_{version}.json"
        save_json(result, output_file)
        
        return result
    
    def run_stage4(self, conv_id, layout, sessions, contexts, keywords):
        """Stage 4: 마인드맵 생성"""
        print(f"  [Stage 4] 마인드맵 생성 ({layout})...")
        
        prompt_file = self.prompts_dir / f"stage4_{layout}.txt"
        replacements = {
            "conversation_id": conv_id,
            "sessions": sessions["sessions"],
            "contexts": contexts["contexts"],
            "keywords": keywords["keywords"]
        }
        
        result = self.gpt.call(str(prompt_file), replacements)
        validate_graph(result)
        
        output_file = self.data_dir / "graphs" / f"{conv_id}_{layout}.json"
        save_json(result, output_file)
        
        return result
    
    def run_stage5(self, conv_id, graph):
        """Stage 5: 평가"""
        print(f"  [Stage 5] 평가...")
        
        golden_file = self.data_dir / "golden_maps" / f"{conv_id}_golden.json"
        golden_graph = load_json(golden_file)
        
        scores = evaluate(graph, golden_graph)
        
        return scores
    
    def run_experiment(self, conv_id, combination):
        """1개 대화 × 1개 조합 = 1회 실험"""
        comb_id = combination["id"]
        comb_name = combination["name"]
        
        print(f"\n실험: {conv_id} × {comb_name}")
        
        start_time = time.time()
        
        try:
            sessions = self.run_stage1(conv_id, combination["stage1"])
            contexts = self.run_stage2(conv_id, combination["stage2"], sessions)
            keywords = self.run_stage3(conv_id, combination["stage3"], contexts)
            graph = self.run_stage4(conv_id, combination["stage4"], sessions, contexts, keywords)
            scores = self.run_stage5(conv_id, graph)
            
            elapsed = time.time() - start_time
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "conversation_id": conv_id,
                "combination_id": comb_id,
                "combination_name": comb_name,
                "stage1": combination["stage1"],
                "stage2": combination["stage2"],
                "stage3": combination["stage3"],
                "stage4": combination["stage4"],
                "node_count": scores["node_count"],
                "node_score": scores["node_score"],
                "keyword_overlap": scores["keyword_overlap"],
                "max_depth": scores["max_depth"],
                "depth_score": scores["depth_score"],
                "total_score": scores["total_score"],
                "elapsed_time": round(elapsed, 2),
                "status": "success"
            }
            
            print(f"  ✓ 완료 (점수: {scores['total_score']:.2f}, 시간: {elapsed:.1f}초)")
            
        except Exception as e:
            elapsed = time.time() - start_time
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "conversation_id": conv_id,
                "combination_id": comb_id,
                "combination_name": comb_name,
                "stage1": combination["stage1"],
                "stage2": combination["stage2"],
                "stage3": combination["stage3"],
                "stage4": combination["stage4"],
                "node_count": None,
                "node_score": None,
                "keyword_overlap": None,
                "max_depth": None,
                "depth_score": None,
                "total_score": None,
                "elapsed_time": round(elapsed, 2),
                "status": "failed",
                "error": str(e)
            }
            
            print(f"  ✗ 실패: {e}")
        
        self.results.append(result)
        self.save_results()
        
        return result
    
    def save_results(self):
        """결과를 CSV로 저장"""
        df = pd.DataFrame(self.results)
        output_file = self.outputs_dir / "quick_registry.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    def run_all(self):
        """축소 실험 실행 (5×5=25회)"""
        print("=" * 60)
        print("빠른 검증 실험 (축소 버전)")
        print("=" * 60)
        
        total = len(QUICK_CONVERSATIONS) * len(self.combinations)
        current = 0
        
        print(f"\n실험 규모: {len(QUICK_CONVERSATIONS)}개 대화 × {len(self.combinations)}개 조합 = {total}회")
        print(f"예상 시간: 약 30분")
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        for conv_id in QUICK_CONVERSATIONS:
            for combination in self.combinations:
                current += 1
                progress = (current / total) * 100
                
                print(f"\n[{current}/{total}] 진행률: {progress:.1f}%")
                
                self.run_experiment(conv_id, combination)
        
        print("\n" + "=" * 60)
        print("축소 실험 완료!")
        print("=" * 60)
        print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"결과 파일: {self.outputs_dir / 'quick_registry.csv'}")
        
        # 통계
        df = pd.DataFrame(self.results)
        success_rate = (df["status"] == "success").sum() / len(df) * 100
        
        if success_rate > 0:
            avg_score = df[df["status"] == "success"]["total_score"].mean()
            print(f"\n성공률: {success_rate:.1f}%")
            print(f"평균 점수: {avg_score:.2f}")
        
        print(f"총 실험 시간: {df['elapsed_time'].sum():.1f}초")
        
        print("\n다음 단계:")
        print("  1. 결과 확인: cat ../outputs/quick_test/quick_registry.csv")
        print("  2. 문제 없으면 전체 실험: cd .. && ./run_full_experiment.sh")

if __name__ == "__main__":
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("사용법: export OPENAI_API_KEY='your-key'")
        sys.exit(1)
    
    lab = QuickLab()
    lab.run_all()
