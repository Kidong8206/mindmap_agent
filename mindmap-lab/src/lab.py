#!/usr/bin/env python3
"""
마인드맵 생성 조합 실험실
20개 대화 × 15개 조합 = 300회 실험
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

class MindmapLab:
    """마인드맵 생성 실험실"""
    
    def __init__(self, base_dir="../"):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "data"
        self.prompts_dir = self.base_dir / "prompts"
        self.outputs_dir = self.base_dir / "outputs"
        self.logs_dir = self.outputs_dir / "logs"
        
        # 디렉토리 생성
        self.outputs_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # GPT API 초기화
        self.gpt = GPTCaller()
        
        # 설정 로드
        with open(self.base_dir / "config.yaml", 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 결과 저장용
        self.results = []
    
    def run_stage1(self, conv_id, version):
        """Stage 1: 세션 분류"""
        print(f"  [Stage 1] 세션 분류 ({version})...")
        
        # 대화 로드
        conv_file = self.data_dir / "conversations" / f"{conv_id}.jsonl"
        conversation = load_jsonl(conv_file)
        
        # GPT 호출
        prompt_file = self.prompts_dir / f"stage1_{version}.txt"
        replacements = {
            "conversation_id": conv_id,
            "conversation": conversation
        }
        
        result = self.gpt.call(str(prompt_file), replacements)
        
        # 검증
        validate_sessions(result)
        
        # 저장
        output_file = self.data_dir / "sessions" / f"{conv_id}_{version}.json"
        save_json(result, output_file)
        
        return result
    
    def run_stage2(self, conv_id, version, sessions):
        """Stage 2: 맥락 분류"""
        print(f"  [Stage 2] 맥락 분류 ({version})...")
        
        # 대화 로드
        conv_file = self.data_dir / "conversations" / f"{conv_id}.jsonl"
        conversation = load_jsonl(conv_file)
        
        # GPT 호출
        prompt_file = self.prompts_dir / f"stage2_{version}.txt"
        replacements = {
            "conversation_id": conv_id,
            "sessions": sessions["sessions"],
            "conversation": conversation
        }
        
        result = self.gpt.call(str(prompt_file), replacements)
        
        # 검증
        validate_contexts(result)
        
        # 저장
        output_file = self.data_dir / "contexts" / f"{conv_id}_{version}.json"
        save_json(result, output_file)
        
        return result
    
    def run_stage3(self, conv_id, version, contexts):
        """Stage 3: 키워드 추출"""
        print(f"  [Stage 3] 키워드 추출 ({version})...")
        
        # 대화 로드
        conv_file = self.data_dir / "conversations" / f"{conv_id}.jsonl"
        conversation = load_jsonl(conv_file)
        
        # GPT 호출
        prompt_file = self.prompts_dir / f"stage3_{version}.txt"
        replacements = {
            "conversation_id": conv_id,
            "conversation": conversation,
            "contexts": contexts["contexts"]
        }
        
        result = self.gpt.call(str(prompt_file), replacements)
        
        # 검증
        validate_keywords(result)
        
        # 저장
        output_file = self.data_dir / "keywords" / f"{conv_id}_{version}.json"
        save_json(result, output_file)
        
        return result
    
    def run_stage4(self, conv_id, layout, sessions, contexts, keywords):
        """Stage 4: 마인드맵 생성"""
        print(f"  [Stage 4] 마인드맵 생성 ({layout})...")
        
        # GPT 호출
        prompt_file = self.prompts_dir / f"stage4_{layout}.txt"
        replacements = {
            "conversation_id": conv_id,
            "sessions": sessions["sessions"],
            "contexts": contexts["contexts"],
            "keywords": keywords["keywords"]
        }
        
        result = self.gpt.call(str(prompt_file), replacements)
        
        # 검증
        validate_graph(result)
        
        # 저장
        output_file = self.data_dir / "graphs" / f"{conv_id}_{layout}.json"
        save_json(result, output_file)
        
        return result
    
    def run_stage5(self, conv_id, graph):
        """Stage 5: 평가"""
        print(f"  [Stage 5] 평가...")
        
        # Golden map 로드
        golden_file = self.data_dir / "golden_maps" / f"{conv_id}_golden.json"
        golden_graph = load_json(golden_file)
        
        # 평가
        scores = evaluate(graph, golden_graph)
        
        return scores
    
    def run_experiment(self, conv_id, combination):
        """1개 대화 × 1개 조합 = 1회 실험"""
        comb_id = combination["id"]
        comb_name = combination["name"]
        
        print(f"\n실험: {conv_id} × {comb_name}")
        
        start_time = time.time()
        
        try:
            # Stage 1: 세션 분류
            sessions = self.run_stage1(conv_id, combination["stage1"])
            
            # Stage 2: 맥락 분류
            contexts = self.run_stage2(conv_id, combination["stage2"], sessions)
            
            # Stage 3: 키워드 추출
            keywords = self.run_stage3(conv_id, combination["stage3"], contexts)
            
            # Stage 4: 마인드맵 생성
            graph = self.run_stage4(
                conv_id, 
                combination["stage4"], 
                sessions, 
                contexts, 
                keywords
            )
            
            # Stage 5: 평가
            scores = self.run_stage5(conv_id, graph)
            
            elapsed = time.time() - start_time
            
            # 결과 저장
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
        
        # 중간 저장
        self.save_results()
        
        return result
    
    def save_results(self):
        """결과를 CSV로 저장"""
        df = pd.DataFrame(self.results)
        output_file = self.outputs_dir / "registry.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    def run_all(self, num_conversations=20):
        """전체 실험 실행"""
        print("=" * 60)
        print("마인드맵 생성 조합 실험실")
        print("=" * 60)
        
        # 대화 목록
        conv_files = list((self.data_dir / "conversations").glob("*.jsonl"))
        conv_ids = [f.stem for f in conv_files[:num_conversations]]
        
        # 조합 목록
        combinations = self.config["combinations"]
        
        total = len(conv_ids) * len(combinations)
        current = 0
        
        print(f"\n실험 규모: {len(conv_ids)}개 대화 × {len(combinations)}개 조합 = {total}회")
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 전체 실험
        for conv_id in conv_ids:
            for combination in combinations:
                current += 1
                progress = (current / total) * 100
                
                print(f"\n[{current}/{total}] 진행률: {progress:.1f}%")
                
                self.run_experiment(conv_id, combination)
        
        # 최종 결과
        print("\n" + "=" * 60)
        print("실험 완료!")
        print("=" * 60)
        print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"결과 파일: {self.outputs_dir / 'registry.csv'}")
        
        # 통계
        df = pd.DataFrame(self.results)
        success_rate = (df["status"] == "success").sum() / len(df) * 100
        avg_score = df[df["status"] == "success"]["total_score"].mean()
        
        print(f"\n성공률: {success_rate:.1f}%")
        print(f"평균 점수: {avg_score:.2f}")
        print(f"총 실험 시간: {df['elapsed_time'].sum():.1f}초")

if __name__ == "__main__":
    # API 키 확인
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("사용법: export OPENAI_API_KEY='your-key'")
        sys.exit(1)
    
    # 실험 실행
    lab = MindmapLab()
    lab.run_all(num_conversations=20)
