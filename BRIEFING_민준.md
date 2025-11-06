# 🎯 민준 (Agent 1) - Core Pipeline Developer

## 👋 환영합니다!

**담당**: 파이프라인 핵심 개발자
**코드명**: Agent 1 (🔵)
**Git Branch**: `feature/pipeline`

---

## 📖 프로젝트 개요

### Mindmap Laboratory란?

**목표**: 대화 데이터를 자동으로 마인드맵으로 변환하는 GPT 기반 시스템

**핵심 철학**: "코딩은 최소화, GPT API는 최대화"
- 전통적인 NLP 알고리즘 대신 GPT-4o API 활용
- 구현 시간 90% 단축
- 100% JSON 출력 일관성

### 시스템 구조

```
원본 대화 (text)
  ↓
[Stage 0] Preprocessing → 0_turns.jsonl
  ↓
[Stage 1] Session Classification → 1_session_split.json
  ↓
[Stage 2] Context Analysis → 2_context.json
  ↓
[Stage 3] Keyword Extraction → 3_keywords.json
  ↓
[Stage 4] Layout Generation → 4_graph.json
  ↓
[Visualization] NetworkX → visualization.png
  ↓
[Evaluation] 30 Metrics → 점수
```

### 연구 목표

- **100가지 알고리즘 조합** × **100개 대화** = **10,000회 실험**
- 대화 유형별 최적 조합 발견
- 데이터 기반 추천 시스템 구축

---

## 🚀 당신의 역할: 파이프라인 개발자

### 담당 범위

**당신이 책임지는 것**:
1. **Stage 0-4 파이프라인** 구현 및 최적화
2. **GPT 프롬프트** 작성 및 개선
3. **시각화 시스템** (NetworkX)
4. **파이프라인 테스트** 작성

**다른 사람 담당**:
- 평가 시스템 (30개 메트릭) → 민섭 (Agent 2)
- E2E 테스트, API, UI → 기동 (Agent 3)

---

## 📁 작업 디렉토리

```
당신이 담당하는 파일들:

agents/
├── ingest/
│   ├── __init__.py
│   └── gpt_preprocessor.py          # Stage 0: 전처리
│
├── session/
│   ├── __init__.py
│   └── gpt_session_classifier.py    # Stage 1: 세션 분류
│
├── context/
│   ├── __init__.py
│   └── gpt_context_analyzer.py      # Stage 2: 맥락 분석
│
├── keyword/
│   ├── __init__.py
│   └── gpt_keyword_extractor.py     # Stage 3: 키워드 추출
│
├── layout/
│   ├── __init__.py
│   └── gpt_layout_generator.py      # Stage 4: 레이아웃 생성
│
├── prompts/
│   ├── __init__.py
│   └── templates.py                 # GPT 프롬프트 템플릿
│
├── utils/                           # 공유 유틸리티
│   ├── __init__.py
│   ├── gpt_client.py               # GPT API 클라이언트
│   ├── schema_validator.py         # JSON 검증
│   └── file_io.py                  # 파일 I/O
│
└── visualizer.py                    # 시각화 (마인드맵 그리기)
```

**절대 수정 금지**:
- `agents/evaluate/` - 민섭 담당
- `app/`, `scripts/`, `tests/test_end_to_end.py` - 기동 담당

---

## 🎯 즉시 시작할 작업

### 우선순위 1: 파이프라인 현황 파악 (30분)

```bash
# 1. 프로젝트 클론 (이미 되어 있다면 skip)
cd /home/user/mindmap_agent

# 2. 필수 문서 읽기 (순서대로)
cat README.md
cat COLLABORATION.md
cat INTERFACE.md
cat PROGRESS.md

# 3. 파이프라인 코드 확인
ls -la agents/session/
cat agents/session/gpt_session_classifier.py
cat agents/prompts/templates.py
```

### 우선순위 2: Git 브랜치 생성

```bash
# 현재 브랜치 확인
git branch

# feature/pipeline 브랜치 생성
git checkout -b feature/pipeline

# 브랜치 푸시
git push -u origin feature/pipeline

# 작업 시작 전 최신 상태로
git fetch origin
git rebase origin/claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi
```

### 우선순위 3: 프롬프트 v1 최적화 시작

**현재 상태**: 파이프라인 5단계 모두 구현 완료 (100%)
**당신의 작업**: 프롬프트 개선하여 출력 품질 향상

**작업 파일**: `agents/prompts/templates.py`

```python
# 예시: Session Classification 프롬프트 개선
SYSTEM_SESSION_CLASSIFIER = """
당신은 대화를 주제별 세션으로 분류하는 전문가입니다.
...
[프롬프트 내용을 읽고 개선점 찾기]
"""
```

---

## 📊 현재 프로젝트 상태

### 전체 진행률: 95%

```
✅ 파이프라인 5단계: 100% 구현 완료
✅ 30개 메트릭: 100% 구현 완료 (민섭 담당)
🔄 E2E 테스트: 80% (기동이 API 키 해결 중)
⏳ 프롬프트 v1: 80% (당신이 완성 예정)
⏳ FastAPI: 80% (기동 담당)
```

### 당신의 작업 현황

```
✅ Stage 0 (Preprocessing): 완성
✅ Stage 1 (Session Classification): 완성
✅ Stage 2 (Context Analysis): 완성
✅ Stage 3 (Keyword Extraction): 완성
✅ Stage 4 (Layout Generation): 완성
✅ Visualizer: 완성
🔄 Prompts v1: 개선 중 (당신의 작업)
⏳ Stage별 개별 테스트: 추가 필요
```

---

## 🔄 Git 워크플로우

### 일일 작업 흐름

```bash
# === 아침 ===
# 1. 다른 Agent 변경사항 가져오기
git fetch origin
git rebase origin/claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi

# === 작업 중 ===
# 2. 프롬프트 수정
vim agents/prompts/templates.py

# 3. 테스트
python tests/test_integration.py

# 4. 자주 커밋 (작은 단위)
git add agents/prompts/templates.py
git commit -m "[Agent 1] refactor: Improve session classification prompt"
git push origin feature/pipeline

# === 작업 완료 시 ===
# 5. PROGRESS.md 업데이트
vim PROGRESS.md
git add PROGRESS.md
git commit -m "[Agent 1] docs: Update progress for prompt optimization"
git push origin feature/pipeline
```

### 커밋 메시지 형식

```
[Agent 1] <type>: <subject>

Type:
- feat: 새 기능
- fix: 버그 수정
- refactor: 코드 리팩토링
- test: 테스트 추가
- docs: 문서 수정

예시:
[Agent 1] refactor: Improve context analysis prompt clarity
[Agent 1] feat: Add retry logic to GPT API calls
[Agent 1] test: Add unit test for keyword extraction
[Agent 1] fix: Resolve JSON schema validation error
```

---

## 🔗 인터페이스 표준 (필수 준수!)

### 1. 함수 시그니처 통일

**모든 Stage 함수는 동일한 형식**:

```python
def run(
    input_path: str,
    output_path: str,
    **kwargs
) -> dict:
    """
    Args:
        input_path: 입력 파일 경로
        output_path: 출력 파일 경로
        **kwargs: 추가 파라미터

    Returns:
        {
            "status": "success" | "error",
            "output": "output_path",
            "metadata": {
                "processing_time": 2.3,
                "api_calls": 1,
                ...
            }
        }
    """
```

### 2. JSON 스키마 검증 (필수!)

**모든 출력은 반드시 스키마 검증**:

```python
from agents.utils.schema_validator import validate_json

# Stage 실행
output_data = {...}

# 스키마 검증 (필수!)
validate_json(output_data, "configs/schema/context_schema.json")

# 파일 저장
with open(output_path, 'w') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
```

### 3. 에러 핸들링 표준

```python
try:
    # 작업 수행
    result = process_data(input_data)
except ValidationError as e:
    return {
        "status": "error",
        "error_type": "ValidationError",
        "message": f"Schema validation failed: {str(e)}",
        "details": {"schema": schema_path}
    }
except Exception as e:
    return {
        "status": "error",
        "error_type": "ProcessingError",
        "message": f"Unexpected error: {str(e)}",
        "details": {}
    }
```

### 4. 로깅 표준

```python
import logging

logger = logging.getLogger(__name__)

# 정보 로그
logger.info(f"[Stage 2] Processing file: {input_path}")

# 경고 로그
logger.warning(f"[Stage 2] Low confidence score: {score}")

# 에러 로그
logger.error(f"[Stage 2] API call failed: {error_msg}")
```

---

## 🧪 테스트 작성

### Mock 데이터로 테스트

**공유 Mock 데이터**: `tests/fixtures/`

```python
# tests/test_session_classifier.py (예시)

def test_session_classifier():
    """Stage 1: Session Classification 테스트"""
    from agents.session.gpt_session_classifier import run

    # Mock 데이터 사용
    result = run(
        input_path="tests/fixtures/mock_turns.jsonl",
        output_path="/tmp/test_session.json",
        session_id="conv_001"
    )

    # 성공 확인
    assert result["status"] == "success"

    # 출력 파일 확인
    with open("/tmp/test_session.json") as f:
        output = json.load(f)

    # 스키마 검증
    validate_json(output, "configs/schema/session_split_schema.json")

    # 세션 수 확인
    assert len(output["sessions"]) > 0
```

---

## 🤝 협업 방법

### 1. 매일 PROGRESS.md 업데이트

```markdown
## 2025-01-15

### 🔵 Agent 1 (민준)
- ✅ 완료: Session classifier 프롬프트 개선
- 🔄 진행 중: Context analyzer 프롬프트 최적화
- ⏳ 다음: Keyword extractor 개선
- 🚧 블로커: 없음
```

### 2. 다른 Agent와 소통

**기동 (Agent 3)**과 협업:
- 기동이 E2E 테스트를 실행할 때 당신의 파이프라인이 사용됨
- 에러 발생 시 디버깅 협조
- 출력 파일 형식 확인

**민섭 (Agent 2)**과 협업:
- 민섭이 평가할 데이터를 당신의 파이프라인이 생성
- JSON 스키마 준수 필수
- 출력 품질 향상 → 평가 점수 향상

### 3. Conflict 방지

- 자주 커밋 (하루 3-5회)
- 다른 Agent 디렉토리 절대 수정 금지
- 공유 파일 (`tests/fixtures/`) 수정 시 알림

---

## 📚 필수 참고 문서

읽어야 할 순서:
1. ✅ **README.md** - 프로젝트 전체 개요
2. ✅ **COLLABORATION.md** - 협업 규칙 (필독!)
3. ✅ **INTERFACE.md** - 인터페이스 표준 (필독!)
4. ✅ **PROGRESS.md** - 현재 진행 상황
5. **BUG_FIX_REPORT.md** - 알려진 버그 (참고)
6. **configs/schema/*.json** - JSON 스키마 정의

---

## 🎯 이번 주 목표 (Week 1-2 완성)

### Day 5-7 (당신의 작업)

- [ ] **프롬프트 v1 최적화**
  - [ ] Stage 1: Session Classification 프롬프트 개선
  - [ ] Stage 2: Context Analysis 프롬프트 개선
  - [ ] Stage 3: Keyword Extraction 프롬프트 개선
  - [ ] Stage 4: Layout Generation 프롬프트 개선

- [ ] **Stage별 개별 테스트 추가**
  - [ ] `tests/test_stage0_preprocessing.py`
  - [ ] `tests/test_stage1_session.py`
  - [ ] `tests/test_stage2_context.py`
  - [ ] `tests/test_stage3_keyword.py`
  - [ ] `tests/test_stage4_layout.py`

- [ ] **에러 핸들링 강화**
  - [ ] GPT API 재시도 로직 개선
  - [ ] 타임아웃 처리
  - [ ] 유효성 검증 강화

### Day 8-14 (다음 주)

- [ ] **프롬프트 v2 준비**
  - [ ] 다양한 프롬프트 변형 생성
  - [ ] A/B 테스트 준비

- [ ] **캐싱 시스템 개선**
  - [ ] SHA256 기반 캐싱 확인
  - [ ] 캐시 히트율 측정

---

## 🔧 개발 환경 설정

### 1. Python 환경

```bash
# 가상환경 확인
which python
# /home/user/mindmap_agent/venv/bin/python 이어야 함

# 패키지 설치 확인
pip list | grep openai
pip list | grep pydantic
```

### 2. 환경 변수

```bash
# .env 파일 확인
cat .env | grep OPENAI_API_KEY
# OPENAI_API_KEY=sk-... 형식
```

### 3. 테스트 실행

```bash
# Stage별 테스트 (아직 작성 안 됨 - 당신이 작성 예정)
pytest tests/test_stage1_session.py -v

# 통합 테스트 (이미 작성됨)
pytest tests/test_integration.py -v
```

---

## 🚨 주의사항

### 절대 수정하지 말 것

❌ **금지**:
- `agents/evaluate/` - 민섭 전용
- `app/main.py` - 기동 전용
- `scripts/run_pipeline.py` - 기동 전용
- `tests/test_end_to_end.py` - 기동 전용

✅ **허용**:
- `agents/ingest/` - 당신 담당
- `agents/session/` - 당신 담당
- `agents/context/` - 당신 담당
- `agents/keyword/` - 당신 담당
- `agents/layout/` - 당신 담당
- `agents/prompts/` - 당신 담당
- `agents/visualizer.py` - 당신 담당
- `agents/utils/` - 공유 (조심히 수정)

### 공유 파일 수정 시

- `tests/fixtures/` - Mock 데이터 수정 시 기동, 민섭에게 알림
- `configs/schema/` - **수정 금지** (표준 확정)
- `agents/utils/` - 수정 시 PR 필수

---

## 💡 프롬프트 개선 팁

### 좋은 프롬프트의 특징

1. **명확한 지시**: 무엇을 해야 하는지 정확히
2. **출력 형식 명시**: JSON 스키마 예시 포함
3. **예시 제공**: Few-shot learning
4. **제약 조건**: 하지 말아야 할 것 명시
5. **한국어 최적화**: 문화적 맥락 고려

### 프롬프트 개선 프로세스

```
1. 현재 프롬프트 분석
   ↓
2. 출력 품질 확인 (민섭의 평가 점수 참고)
   ↓
3. 개선 아이디어 도출
   ↓
4. 새 프롬프트 작성
   ↓
5. 테스트 실행
   ↓
6. 점수 비교
   ↓
7. 더 나은 프롬프트 채택
```

---

## 📝 체크리스트 (시작 전)

- [ ] README.md 읽기
- [ ] COLLABORATION.md 읽기 (필수!)
- [ ] INTERFACE.md 읽기 (필수!)
- [ ] PROGRESS.md 확인
- [ ] Git 브랜치 생성 (feature/pipeline)
- [ ] 파이프라인 코드 확인
- [ ] 프롬프트 파일 열기
- [ ] PROGRESS.md에 오늘 계획 작성

---

## 🎯 첫 작업: 프롬프트 분석

### 즉시 실행할 명령어

```bash
# 1. 프롬프트 파일 열기
cat agents/prompts/templates.py

# 2. 각 Stage 프롬프트 읽기
# - SYSTEM_SESSION_CLASSIFIER
# - SYSTEM_CONTEXT_ANALYZER
# - SYSTEM_KEYWORD_EXTRACTOR
# - SYSTEM_LAYOUT_GENERATOR

# 3. 개선점 찾기
# - 불명확한 지시
# - 부족한 예시
# - 애매한 출력 형식

# 4. PROGRESS.md에 계획 작성
vim PROGRESS.md

# 5. 첫 커밋
git add PROGRESS.md
git commit -m "[Agent 1] docs: Add initial work plan for prompt optimization"
git push origin feature/pipeline
```

---

## 🚀 시작하세요!

**당신의 임무**:
1. 프롬프트 v1 완성 → 출력 품질 향상
2. Stage별 테스트 추가 → 안정성 확보
3. 에러 핸들링 강화 → 견고성 향상

**기대 효과**:
- 평가 점수 향상 (현재 77% → 목표 85%+)
- 대화 유형별 최적 조합 발견
- 연구 목표 달성

---

## 🤝 협업 시작!

**기동 (Agent 3)**은 E2E 테스트와 API 개발
**민섭 (Agent 2)**은 평가 메트릭 개선
**민준 (당신)**은 파이프라인 품질 향상

→ 3명이 협력하여 Week 1-2 완성! 🔥

**화이팅!** 💪
