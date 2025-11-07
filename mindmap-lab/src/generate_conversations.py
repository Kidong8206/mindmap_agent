#!/usr/bin/env python3
"""대화 자동 생성 모듈 - 20개 시나리오 → 20개 JSONL"""
import os
import sys
import json
from pathlib import Path
from gpt_caller import GPTCaller

# 20개 시나리오 정의
SCENARIOS = [
    # 학습 짧음 (3개)
    {"id": "conv_001", "topic": "양자역학 기초", "turns": 38, "type": "learning_short"},
    {"id": "conv_002", "topic": "프랑스혁명", "turns": 36, "type": "learning_short"},
    {"id": "conv_003", "topic": "프로그래밍 기초 (Python)", "turns": 40, "type": "learning_short"},
    
    # 학습 중간 (4개)
    {"id": "conv_004", "topic": "딥러닝과 신경망", "turns": 80, "type": "learning_medium"},
    {"id": "conv_005", "topic": "르네상스 미술", "turns": 75, "type": "learning_medium"},
    {"id": "conv_006", "topic": "기후변화와 환경", "turns": 85, "type": "learning_medium"},
    {"id": "conv_007", "topic": "세포와 유전학", "turns": 90, "type": "learning_medium"},
    
    # 학습 긴 (3개)
    {"id": "conv_008", "topic": "인공지능 전반", "turns": 140, "type": "learning_long"},
    {"id": "conv_009", "topic": "세계사 흐름", "turns": 130, "type": "learning_long"},
    {"id": "conv_010", "topic": "화학 원리와 응용", "turns": 150, "type": "learning_long"},
    
    # 브레인스토밍 (5개)
    {"id": "conv_011", "topic": "학교 축제 아이디어", "turns": 60, "type": "brainstorming"},
    {"id": "conv_012", "topic": "환경 캠페인 기획", "turns": 65, "type": "brainstorming"},
    {"id": "conv_013", "topic": "미래 교육 시스템", "turns": 70, "type": "brainstorming"},
    {"id": "conv_014", "topic": "플라스틱 문제 해결", "turns": 55, "type": "brainstorming"},
    {"id": "conv_015", "topic": "효율적 시간 관리", "turns": 58, "type": "brainstorming"},
    
    # 정보검색 (5개)
    {"id": "conv_016", "topic": "노벨상 수상자들", "turns": 45, "type": "info_search"},
    {"id": "conv_017", "topic": "태양계 행성들", "turns": 50, "type": "info_search"},
    {"id": "conv_018", "topic": "Python vs JavaScript", "turns": 42, "type": "info_search"},
    {"id": "conv_019", "topic": "민주주의 발전", "turns": 48, "type": "info_search"},
    {"id": "conv_020", "topic": "전기차 브랜드 비교", "turns": 38, "type": "info_search"}
]

PROMPT_TEMPLATE = """당신은 고등학생과 AI의 학습 대화를 생성하는 전문가입니다.

주제: {topic}
목표 턴 수: {turns}
대화 유형: {conv_type}

규칙:
1. user와 assistant가 정확히 교대로 나타남 (user 시작)
2. 자연스러운 대화 흐름 (학생의 호기심, 질문, 이해 확인)
3. 2-4번의 주제 전환 포함 ("그럼 이제...", "다시 본론으로...", "추가로...")
4. 분기 대화 포함 ("잠깐, 이건?", "근데 궁금한데...")
5. user는 짧게 (1-3문장), assistant는 상세하게 (3-8문장)
6. 턴 수는 정확히 {turns}개

출력 형식 (JSON 배열):
[
  {{"turn_id": 0, "role": "user", "content": "..."}},
  {{"turn_id": 1, "role": "assistant", "content": "..."}},
  ...
]

중요: 정확히 {turns}개의 턴을 생성하세요. turn_id는 0부터 시작합니다.
"""

class ConversationGenerator:
    def __init__(self):
        self.gpt = GPTCaller()
        self.output_dir = Path("../data/conversations")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_one(self, scenario):
        """1개 대화 생성"""
        conv_id = scenario["id"]
        topic = scenario["topic"]
        turns = scenario["turns"]
        conv_type = scenario["type"]
        
        print(f"\n생성 중: {conv_id} - {topic} ({turns}턴)")
        
        # GPT 호출 (JSON 모드)
        prompt = PROMPT_TEMPLATE.format(
            topic=topic,
            turns=turns,
            conv_type=conv_type
        )
        
        try:
            # JSON 배열로 받기
            response = self.gpt.client.chat.completions.create(
                model=self.gpt.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,  # 다양성을 위해 약간 높임
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # 배열 추출
            if "conversation" in result:
                conversation = result["conversation"]
            elif "turns" in result:
                conversation = result["turns"]
            elif isinstance(result, list):
                conversation = result
            else:
                # 첫 번째 배열 찾기
                for key in result:
                    if isinstance(result[key], list):
                        conversation = result[key]
                        break
            
            # 검증
            assert len(conversation) >= turns * 0.9, f"턴 수 부족: {len(conversation)} < {turns * 0.9}"
            assert conversation[0]["role"] == "user", "첫 턴이 user가 아님"
            
            # JSONL 저장
            output_file = self.output_dir / f"{conv_id}.jsonl"
            with open(output_file, 'w', encoding='utf-8') as f:
                for turn in conversation:
                    f.write(json.dumps(turn, ensure_ascii=False) + '\n')
            
            print(f"  ✓ 완료: {len(conversation)}턴 생성 → {output_file}")
            return True
            
        except Exception as e:
            print(f"  ✗ 실패: {e}")
            return False
    
    def generate_all(self):
        """전체 20개 생성"""
        print("=" * 60)
        print("대화 자동 생성 시작 (20개 시나리오)")
        print("=" * 60)
        
        success = 0
        for i, scenario in enumerate(SCENARIOS, 1):
            print(f"\n[{i}/20]", end=" ")
            if self.generate_one(scenario):
                success += 1
        
        print("\n" + "=" * 60)
        print(f"완료: {success}/20개 생성 성공")
        print("=" * 60)

if __name__ == "__main__":
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠ OPENAI_API_KEY 필요")
        sys.exit(1)
    
    generator = ConversationGenerator()
    generator.generate_all()
