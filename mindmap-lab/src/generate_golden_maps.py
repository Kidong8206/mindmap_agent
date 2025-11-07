#!/usr/bin/env python3
"""골든 마인드맵 자동 생성 모듈"""
import os
import sys
import json
from pathlib import Path
from gpt_caller import GPTCaller
from utils import load_jsonl, save_json

GOLDEN_PROMPT = """이 대화의 이상적인 마인드맵을 만드세요.

대화 내용:
{conversation_text}

요구사항:
1. 루트 노드 1개: 전체 주제를 대표
2. Level 1 노드: 주요 개념 5-10개
3. Level 2 노드: 세부 내용 5-15개
4. 레이블: 간결하게 1-4단어
5. 계층 구조 명확하게

출력 JSON 형식:
{{
  "conversation_id": "{conv_id}",
  "layout": "hierarchical",
  "graph": {{
    "nodes": [
      {{"id": "n0", "label": "주제", "level": 0, "position": {{"x": 400, "y": 50}}}},
      {{"id": "n1", "label": "개념1", "level": 1, "position": {{"x": 300, "y": 170}}}},
      {{"id": "n2", "label": "개념2", "level": 1, "position": {{"x": 500, "y": 170}}}}
    ],
    "edges": [
      {{"from": "n0", "to": "n1", "type": "hierarchy"}},
      {{"from": "n0", "to": "n2", "type": "hierarchy"}}
    ]
  }}
}}

위치 규칙:
- 루트: (400, 50)
- Level 1: y=170, x는 200~600 사이 균등 분배
- Level 2: y=290, 부모 노드 근처

중요: 최소 10개, 최대 30개 노드를 생성하세요.
"""

class GoldenMapGenerator:
    def __init__(self):
        self.gpt = GPTCaller()
        self.conv_dir = Path("../data/conversations")
        self.output_dir = Path("../data/golden_maps")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_one(self, conv_id):
        """1개 골든 맵 생성"""
        print(f"\n생성 중: {conv_id}_golden.json")
        
        # 대화 로드
        conv_file = self.conv_dir / f"{conv_id}.jsonl"
        if not conv_file.exists():
            print(f"  ✗ 대화 파일 없음: {conv_file}")
            return False
        
        conversation = load_jsonl(conv_file)
        
        # 대화 텍스트 요약 (너무 길면 GPT 토큰 초과)
        conv_text = ""
        for turn in conversation[:50]:  # 최대 50턴만 사용
            role = turn["role"]
            content = turn["content"][:200]  # 각 턴도 200자 제한
            conv_text += f"[{role}] {content}\n"
        
        # GPT 호출
        prompt = GOLDEN_PROMPT.format(
            conversation_text=conv_text,
            conv_id=conv_id
        )
        
        try:
            response = self.gpt.client.chat.completions.create(
                model=self.gpt.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # 검증
            assert "graph" in result, "graph 키 없음"
            assert "nodes" in result["graph"], "nodes 없음"
            assert "edges" in result["graph"], "edges 없음"
            
            node_count = len(result["graph"]["nodes"])
            assert 10 <= node_count <= 30, f"노드 수 이상: {node_count}"
            
            # 저장
            output_file = self.output_dir / f"{conv_id}_golden.json"
            save_json(result, output_file)
            
            print(f"  ✓ 완료: {node_count}개 노드 → {output_file}")
            return True
            
        except Exception as e:
            print(f"  ✗ 실패: {e}")
            return False
    
    def generate_all(self):
        """전체 20개 생성"""
        print("=" * 60)
        print("골든 마인드맵 자동 생성 (20개)")
        print("=" * 60)
        
        # 대화 파일 목록
        conv_files = sorted(self.conv_dir.glob("conv_*.jsonl"))
        conv_ids = [f.stem for f in conv_files]
        
        print(f"\n발견된 대화: {len(conv_ids)}개")
        
        success = 0
        for i, conv_id in enumerate(conv_ids, 1):
            print(f"\n[{i}/{len(conv_ids)}]", end=" ")
            if self.generate_one(conv_id):
                success += 1
        
        print("\n" + "=" * 60)
        print(f"완료: {success}/{len(conv_ids)}개 생성 성공")
        print("=" * 60)

if __name__ == "__main__":
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠ OPENAI_API_KEY 필요")
        sys.exit(1)
    
    generator = GoldenMapGenerator()
    generator.generate_all()
