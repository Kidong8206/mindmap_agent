"""
Prompt templates for all pipeline stages
"""

from typing import Dict, Any


# ===== Stage 0: Preprocessing =====

PREPROCESS_PROMPT = """당신은 대화 데이터 전처리 전문가입니다.

# 작업
다음 대화를 정제하고 표준 JSON 형식으로 변환하세요.

## 처리 규칙
1. **개인정보 마스킹**: 이름, 전화번호, 이메일, 주소 등을 [MASKED]로 대체
2. **불필요한 표현 제거**: 이모티콘, "음...", "아...", "어..." 등
3. **의미 보존**: 대화 내용의 핵심 의미는 반드시 유지
4. **타임스탬프**: ISO 8601 형식으로 정규화

# 입력 대화
{raw_conversation}

# 출력 형식 (반드시 JSON만 출력)
{{
  "session_id": "{session_id}",
  "turns": [
    {{
      "turn_id": 0,
      "role": "user",
      "text": "정제된 대화 내용",
      "timestamp": "2024-01-15T10:00:00Z"
    }},
    {{
      "turn_id": 1,
      "role": "assistant",
      "text": "정제된 응답 내용",
      "timestamp": "2024-01-15T10:00:05Z"
    }}
  ]
}}

# 중요
- 개인정보는 반드시 [MASKED]로 대체
- 대화의 문맥과 의미는 보존
- JSON 형식만 출력 (설명 없이)
- role은 반드시 "user" 또는 "assistant"
"""


# ===== Stage 1: Session Classification =====

SESSION_CLASSIFY_PROMPT = """당신은 대화 분석 전문가입니다.

# 작업
아래 대화에서 **주제가 전환되는 지점**을 찾아 세션으로 분리하세요.

## 세션 정의
- **세션**: 하나의 목적/주제를 가진 대화 단위
- **주제 전환 신호**: "그럼 이제...", "다른 얘기인데...", 문맥 급변 등

## 대화
{conversation_text}

## 출력 형식 (반드시 JSON만)
{{
  "session_id": "{session_id}",
  "algorithm": "gpt_session_classifier",
  "sessions": [
    {{
      "session_num": 0,
      "turn_range": [0, 15],
      "summary": "React Hook 개념 질문",
      "topic_label": "학습-질문",
      "boundary_confidence": 0.95
    }},
    {{
      "session_num": 1,
      "turn_range": [16, 30],
      "summary": "useState 예제 실습",
      "topic_label": "학습-실습",
      "boundary_confidence": 0.88
    }}
  ]
}}

## 규칙
- 세션은 최소 3턴 이상
- turn_range는 연속적이고 겹치지 않음
- boundary_confidence는 0-1 사이 (주제 전환의 명확도)
- summary는 10-20자 이내로 간결하게
- topic_label은 "카테고리-세부유형" 형식
"""


# ===== Stage 2: Context Analysis =====

CONTEXT_ANALYZE_PROMPT = """당신은 대화 구조 분석 전문가입니다.

# 작업
세션 내 대화에서 **메인 경로(Main Path)**와 **분기 경로(Side Paths)**를 구분하세요.

## 정의
- **Main Path**: 세션의 핵심 목적을 달성하는 주요 대화 흐름
- **Side Path**: 잠깐 다른 이야기로 샜다가 다시 돌아오는 보조 흐름

## 세션 정보
Session #{session_num}: {session_summary}
Turn Range: {turn_range}

## 대화
{session_turns_text}

## 출력 형식 (반드시 JSON만)
{{
  "session_num": {session_num},
  "main_path": {{
    "path_id": "main_{session_num}",
    "turns": [0, 2, 5, 7, 10, 12, 15],
    "topic": "React Hook 개념 이해",
    "keywords": ["hook", "useState", "함수형 컴포넌트"],
    "coherence_score": 0.89
  }},
  "side_paths": [
    {{
      "path_id": "side_{session_num}_1",
      "turns": [3, 4],
      "topic": "클래스 컴포넌트 비교",
      "keywords": ["클래스", "this.state"],
      "branch_from_turn": 2,
      "rejoin_turn": 5
    }}
  ]
}}

## 규칙
- main_path는 반드시 1개
- side_paths는 0개 이상 (없으면 빈 배열)
- turns는 오름차순 정렬
- side_path는 반드시 branch_from과 rejoin이 있어야 함
- coherence_score는 주관적 판단 (경로의 의미적 일관성)
"""


# ===== Stage 3: Keyword Extraction =====

KEYWORD_EXTRACT_PROMPT = """당신은 키워드 추출 전문가입니다.

# 작업
경로(Path)별로 **핵심 키워드**를 5-10개 추출하세요.

## 경로 정보
Path ID: {path_id}
Topic: {path_topic}
Turn Indices: {path_turns}

## 경로 텍스트
{path_text}

## 출력 형식 (반드시 JSON만)
{{
  "path_id": "{path_id}",
  "keywords": [
    {{
      "word": "React Hook",
      "score": 0.95,
      "turns": [0, 2, 5, 7]
    }},
    {{
      "word": "useState",
      "score": 0.88,
      "turns": [2, 5, 10, 12]
    }},
    {{
      "word": "함수형 컴포넌트",
      "score": 0.85,
      "turns": [0, 7, 15]
    }}
  ]
}}

## 규칙
- 키워드는 5-10개 (중요도 순)
- score는 중요도 (0-1)
- turns는 해당 키워드가 등장한 턴 번호들
- 명사/명사구 위주 (동사/형용사는 제외)
- 중복 제거 (의미적으로 동일한 표현은 하나로 통합)
- 너무 일반적인 단어는 제외 ("것", "그것", "이것" 등)
"""


# ===== Stage 4: Layout Generation =====

LAYOUT_GENERATE_PROMPT = """당신은 마인드맵 디자이너입니다.

# 작업
키워드와 경로 구조를 바탕으로 **마인드맵 그래프**를 생성하세요.

## 입력 데이터

### 키워드 (경로별)
{keywords_json}

### 맥락 구조
{contexts_json}

## 출력 형식 (반드시 JSON만)
{{
  "session_id": "{session_id}",
  "algorithm": "{layout_algorithm}",
  "graph": {{
    "nodes": [
      {{
        "id": "node_0",
        "label": "React Hook",
        "type": "root",
        "path_id": "main_0",
        "depth": 0,
        "x": 500,
        "y": 50,
        "size": 30,
        "color": "#3498db"
      }},
      {{
        "id": "node_1",
        "label": "useState",
        "type": "main",
        "path_id": "main_0",
        "depth": 1,
        "x": 350,
        "y": 150,
        "size": 25,
        "color": "#2ecc71"
      }},
      {{
        "id": "node_2",
        "label": "클래스 컴포넌트",
        "type": "side",
        "path_id": "side_0_1",
        "depth": 2,
        "x": 600,
        "y": 150,
        "size": 20,
        "color": "#95a5a6"
      }}
    ],
    "edges": [
      {{
        "id": "edge_0_1",
        "source": "node_0",
        "target": "node_1",
        "type": "main",
        "weight": 0.88
      }},
      {{
        "id": "edge_1_2",
        "source": "node_1",
        "target": "node_2",
        "type": "side",
        "weight": 0.65
      }}
    ],
    "layout": {{
      "type": "{layout_type}",
      "direction": "{layout_direction}",
      "width": 1000,
      "height": 600
    }}
  }}
}}

## 레이아웃 타입별 배치 규칙

### hierarchical (계층형)
- Root 노드를 상단 중앙에 배치
- Main path는 위에서 아래로 수직 배치
- Side path는 옆으로 분기
- depth에 따라 y 좌표 증가

### radial (방사형)
- Root 노드를 중심에 배치
- Main path는 방사형으로 퍼짐
- Side path는 main 노드에서 추가 분기

### timeline (타임라인)
- 시간 순서대로 왼쪽에서 오른쪽으로
- Main path는 중앙 수평선
- Side path는 위/아래로 분기

## 규칙
- Root 노드는 1개 (세션의 주제)
- 노드 좌표는 겹치지 않게 배치 (최소 50px 간격)
- 색상 규칙:
  - root: #3498db (파란색)
  - main: #2ecc71 (초록색)
  - side: #95a5a6 (회색)
- size는 중요도에 비례 (20-30px)
- weight는 키워드 score 기반
"""


# ===== Prompt Builder =====

def build_prompt(template: str, **kwargs) -> str:
    """
    Build prompt from template with variable substitution

    Args:
        template: Prompt template string
        **kwargs: Variables to substitute

    Returns:
        Formatted prompt string
    """
    return template.format(**kwargs)
