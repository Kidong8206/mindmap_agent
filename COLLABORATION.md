# 🤝 3-Agent 협동 개발 가이드

## 📋 역할 분담

### 🔵 Agent 1: Core Pipeline Developer
**담당**: 파이프라인 핵심 개발

**작업 디렉토리**:
```
agents/ingest/
agents/session/
agents/context/
agents/keyword/
agents/layout/
agents/prompts/
agents/visualizer.py
```

**Git Branch**: `feature/pipeline`

**책임**:
- Stage 0-4 파이프라인 구현 및 개선
- GPT 프롬프트 최적화
- 시각화 기능 개선
- 파이프라인 개별 테스트 작성

---

### 🟢 Agent 2: Evaluation & Metrics Specialist
**담당**: 평가 시스템 전문가

**작업 디렉토리**:
```
agents/evaluate/
tests/test_*_rubric.py
configs/schema/metrics_*.json
```

**Git Branch**: `feature/evaluation`

**책임**:
- 30개 메트릭 개선 및 최적화
- Golden Set 비교 로직 구현
- 메트릭 테스트 강화
- 평가 유틸리티 개선

---

### 🟡 Agent 3: Integration & Experiment Manager
**담당**: 통합 및 실험 관리

**작업 디렉토리**:
```
app/
scripts/
tests/test_end_to_end.py
tests/test_integration.py
data/
docs/
```

**Git Branch**: `feature/integration`

**책임**:
- E2E 테스트 완성
- FastAPI 서버 구현
- Streamlit 대시보드
- Docker 패키징
- 문서 작성

---

## 🔄 Git 워크플로우

### 1. 초기 설정

각 Agent는 자신의 브랜치 생성:

```bash
# Agent 1
git checkout -b feature/pipeline
git push -u origin feature/pipeline

# Agent 2
git checkout -b feature/evaluation
git push -u origin feature/evaluation

# Agent 3
git checkout -b feature/integration
git push -u origin feature/integration
```

### 2. 일일 작업 흐름

```bash
# 아침: 메인 브랜치 최신화
git fetch origin main
git rebase origin/main

# 작업 진행
# ... 코드 수정 ...

# 작은 단위로 자주 커밋
git add .
git commit -m "[Agent 1] Add session classifier tests"
git push origin feature/pipeline
```

### 3. 동기화 (하루에 1-2회)

```bash
# 다른 Agent의 변경사항 가져오기
git fetch origin
git merge origin/feature/evaluation  # 필요시
git merge origin/feature/integration # 필요시
```

### 4. Pull Request 생성

작업 완료 시:
1. GitHub에서 PR 생성
2. Title: `[Agent 1] Implement session classifier improvements`
3. Description: 변경사항 상세 설명
4. Reviewer: 다른 Agent 지정 (또는 사용자)

---

## 🔗 인터페이스 표준

### JSON 스키마 준수 (필수)

**파이프라인 출력 검증 (Agent 1)**:
```python
from agents.utils.schema_validator import validate_json

# 출력 시 항상 검증
output_data = {...}
validate_json(output_data, "configs/schema/context_schema.json")
```

**평가 입력 검증 (Agent 2)**:
```python
# 입력 시 항상 검증
context_data = load_json("2_context.json")
validate_json(context_data, "configs/schema/context_schema.json")
```

### 함수 시그니처 표준

**모든 Stage 함수**:
```python
def run(
    input_path: str,
    output_path: str,
    **kwargs
) -> dict:
    """
    Args:
        input_path: 입력 파일 경로 (절대 경로 또는 상대 경로)
        output_path: 출력 파일 경로
        **kwargs: 추가 파라미터 (Stage별로 다름)

    Returns:
        {
            "status": "success" | "error",
            "output": "output_path",
            "metadata": {...}
        }
    """
    pass
```

**모든 평가 함수**:
```python
def evaluate_*(
    # 필수 파라미터
    required_json: str,
    golden_annotations: dict,

    # 선택 파라미터
    weights: Optional[Dict[str, float]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Returns:
        {
            "rubric_type": "context" | "layout" | "comprehensive",
            "scores": {
                "metric_1": {"score": 0.85, "details": {...}},
                "metric_2": {"score": 0.92, "details": {...}},
                ...
            },
            "weights": {...},
            "weighted_score": 0.8178
        }
    """
    pass
```

### 에러 핸들링 표준

**모든 에러는 일관된 포맷으로**:
```python
def handle_error(error_type: str, message: str, details: dict = None):
    return {
        "status": "error",
        "error_type": error_type,  # "ValidationError", "APIError", etc.
        "message": message,
        "details": details or {}
    }
```

### 로깅 표준

**모든 모듈에서 일관된 로깅**:
```python
import logging

logger = logging.getLogger(__name__)

# 정보 로그
logger.info(f"[Stage 2] Processing file: {input_path}")

# 경고 로그
logger.warning(f"[Stage 2] Low confidence score: {score}")

# 에러 로그
logger.error(f"[Stage 2] Failed to process: {error_msg}")
```

---

## 📝 커밋 메시지 컨벤션

**형식**: `[Agent N] <type>: <subject>`

**Type**:
- `feat`: 새 기능
- `fix`: 버그 수정
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅
- `chore`: 기타 작업

**예시**:
```
[Agent 1] feat: Add retry logic to GPT API calls
[Agent 2] fix: Correct depth_balance metric calculation
[Agent 3] test: Add E2E test for full pipeline
[Agent 1] refactor: Simplify session classification prompt
[Agent 2] docs: Update evaluation metrics documentation
```

---

## 🧪 테스트 전략

### Mock 데이터 활용

**공유 Mock 데이터** (`tests/fixtures/`):
- `mock_turns.jsonl` - 입력 대화
- `mock_session_split.json` - Stage 1 출력
- `mock_context.json` - Stage 2 출력
- `mock_keywords.json` - Stage 3 출력
- `mock_graph.json` - Stage 4 출력

**각 Agent의 테스트**:
```python
# Agent 1: 파이프라인 테스트
def test_session_classifier():
    result = classify_sessions(
        input_path="tests/fixtures/mock_turns.jsonl",
        output_path="/tmp/test_session.json",
        session_id="conv_001"
    )
    assert result["status"] == "success"

# Agent 2: 평가 테스트
def test_context_evaluation():
    result = evaluate_context(
        context_json="tests/fixtures/mock_context.json",
        ...
    )
    assert result["weighted_score"] > 0.7

# Agent 3: 통합 테스트
def test_full_pipeline():
    # 전체 파이프라인 실행 및 검증
    pass
```

---

## 📊 진행 상황 트래킹

### 일일 체크인 (Stand-up)

각 Agent는 PROGRESS.md를 매일 업데이트:

```markdown
## 2025-01-15

### 🔵 Agent 1
- ✅ 완료: Session classifier 테스트 추가
- 🔄 진행 중: Context analyzer 프롬프트 최적화
- ⏳ 다음: Keyword extractor 개선
- 🚧 블로커: 없음

### 🟢 Agent 2
- ✅ 완료: depth_balance 메트릭 수정
- 🔄 진행 중: Golden Set 비교 로직 구현
- ⏳ 다음: color_contrast 메트릭 개선
- 🚧 블로커: Golden data 필요 (Week 3-4)

### 🟡 Agent 3
- ✅ 완료: E2E 테스트 스크립트 작성
- 🔄 진행 중: FastAPI 엔드포인트 구현
- ⏳ 다음: Streamlit 대시보드
- 🚧 블로커: OpenAI API 키 권한 문제
```

---

## 🔍 코드 리뷰 체크리스트

PR 생성 시 확인사항:

- [ ] 모든 테스트 통과
- [ ] JSON 스키마 검증 추가
- [ ] 로깅 추가
- [ ] 에러 핸들링 구현
- [ ] 함수 docstring 작성
- [ ] 타입 힌트 추가
- [ ] 커밋 메시지 컨벤션 준수
- [ ] 중복 코드 제거
- [ ] 주석으로 복잡한 로직 설명

---

## 🚨 충돌 해결 프로토콜

### Merge Conflict 발생 시:

1. **파악**: 어떤 파일에서 충돌이 발생했는지 확인
   ```bash
   git status
   ```

2. **조정**: 충돌하는 Agent와 소통
   - 같은 함수를 수정했는가?
   - 누가 merge할 것인가?

3. **해결**: 수동으로 충돌 해결
   ```bash
   # 충돌 파일 편집
   git add <resolved-file>
   git commit -m "[Agent N] Resolve merge conflict with feature/X"
   ```

4. **테스트**: 병합 후 모든 테스트 실행
   ```bash
   pytest tests/
   ```

---

## 📚 필수 문서

각 Agent가 작업 시 참고할 문서:

1. **README.md** - 프로젝트 전체 개요
2. **COLLABORATION.md** (이 문서) - 협업 가이드
3. **configs/schema/*.json** - 데이터 스키마 정의
4. **BUG_FIX_REPORT.md** - 알려진 버그 및 수정사항
5. **INTEGRATION_TEST_REPORT.md** - 통합 테스트 결과

---

## 🎯 현재 우선순위 (Week 1-2)

### 🔵 Agent 1 (파이프라인)
1. 프롬프트 v1 완성
2. Stage별 개별 테스트 추가
3. 에러 핸들링 강화

### 🟢 Agent 2 (평가)
1. 저점수 메트릭 개선
2. Golden Set 준비
3. 메트릭 문서화

### 🟡 Agent 3 (통합)
1. **API 키 문제 해결** ⚠️
2. E2E 테스트 완성
3. FastAPI 엔드포인트 구현
4. Docker 패키징

---

## 💬 소통 채널

**일일 업데이트**: PROGRESS.md 파일
**블로커 공유**: GitHub Issues
**코드 리뷰**: Pull Request Comments
**긴급 사항**: (사용자와 직접 소통)

---

## ✅ 협업 성공 기준

- [ ] 모든 Agent의 브랜치가 충돌 없이 병합
- [ ] 전체 테스트 커버리지 > 80%
- [ ] E2E 테스트 통과
- [ ] 모든 JSON 스키마 검증 통과
- [ ] Week 1-2 목표 100% 달성
