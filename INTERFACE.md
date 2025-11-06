# 🔗 모듈 간 인터페이스 정의

이 문서는 3개 Agent가 협업할 때 서로의 코드를 연동하기 위한 **표준 인터페이스**를 정의합니다.

---

## 📋 목차

1. [데이터 포맷 (JSON 스키마)](#데이터-포맷-json-스키마)
2. [파이프라인 함수 시그니처](#파이프라인-함수-시그니처)
3. [평가 함수 시그니처](#평가-함수-시그니처)
4. [에러 핸들링](#에러-핸들링)
5. [로깅 표준](#로깅-표준)
6. [테스트 데이터](#테스트-데이터)

---

## 1. 데이터 포맷 (JSON 스키마)

### 파이프라인 Stage별 입출력

```
[입력] raw_conversation.txt
  ↓
[Stage 0] GPT Preprocessing
  ↓
[출력] 0_turns.jsonl ← turns_schema.json
  ↓
[Stage 1] GPT Session Classification
  ↓
[출력] 1_session_split.json ← session_split_schema.json
  ↓
[Stage 2] GPT Context Analysis
  ↓
[출력] 2_context.json ← context_schema.json
  ↓
[Stage 3] GPT Keyword Extraction
  ↓
[출력] 3_keywords.json ← keywords_schema.json
  ↓
[Stage 4] GPT Layout Generation
  ↓
[출력] 4_graph.json ← graph_schema.json
  ↓
[Evaluation] 30 Metrics
  ↓
[출력] metrics_*.json ← metrics_*_schema.json
```

### 스키마 파일 위치

```
configs/schema/
├── turns_schema.json              # Stage 0 출력
├── session_split_schema.json      # Stage 1 출력
├── context_schema.json            # Stage 2 출력
├── keywords_schema.json           # Stage 3 출력
├── graph_schema.json              # Stage 4 출력
├── metrics_context_schema.json    # Context Rubric 출력
├── metrics_layout_schema.json     # Layout Rubric 출력
└── metrics_comprehensive_schema.json  # Comprehensive Rubric 출력
```

### 스키마 검증 방법

**모든 Agent는 출력 시 반드시 검증**:

```python
from agents.utils.schema_validator import validate_json

# Agent 1 (파이프라인) - 출력 검증
output_data = {...}
validate_json(output_data, "configs/schema/context_schema.json")
with open(output_path, 'w') as f:
    json.dump(output_data, f)

# Agent 2 (평가) - 입력 검증
with open(input_path) as f:
    input_data = json.load(f)
validate_json(input_data, "configs/schema/context_schema.json")
```

---

## 2. 파이프라인 함수 시그니처

### Stage 0: Preprocessing (Agent 1)

```python
def run(
    input_path: str,
    output_path: str,
    **kwargs
) -> dict:
    """
    원본 대화를 JSONL 형식으로 변환

    Args:
        input_path (str): 원본 대화 텍스트 파일 경로
        output_path (str): 출력 JSONL 파일 경로

    Returns:
        dict: {
            "status": "success" | "error",
            "output": "0_turns.jsonl",
            "metadata": {
                "turn_count": 10,
                "processing_time": 0.5
            }
        }
    """
```

### Stage 1: Session Classification (Agent 1)

```python
def run(
    input_path: str,
    output_path: str,
    session_id: str,
    **kwargs
) -> dict:
    """
    대화를 세션별로 분류

    Args:
        input_path (str): 0_turns.jsonl 경로
        output_path (str): 출력 JSON 파일 경로
        session_id (str): 세션 ID (예: "conv_001")

    Returns:
        dict: {
            "status": "success" | "error",
            "output": "1_session_split.json",
            "metadata": {
                "session_count": 3,
                "api_calls": 1,
                "processing_time": 2.3
            }
        }
    """
```

### Stage 2: Context Analysis (Agent 1)

```python
def run(
    input_path: str,
    output_path: str,
    turns_path: str,
    **kwargs
) -> dict:
    """
    대화 맥락 분석

    Args:
        input_path (str): 1_session_split.json 경로
        output_path (str): 출력 JSON 파일 경로
        turns_path (str): 0_turns.jsonl 경로 (참조용)

    Returns:
        dict: {
            "status": "success" | "error",
            "output": "2_context.json",
            "metadata": {
                "main_topic": "React Hook",
                "api_calls": 1,
                "processing_time": 3.1
            }
        }
    """
```

### Stage 3: Keyword Extraction (Agent 1)

```python
def run(
    input_path: str,
    output_path: str,
    turns_path: str,
    **kwargs
) -> dict:
    """
    키워드 추출

    Args:
        input_path (str): 2_context.json 경로
        output_path (str): 출력 JSON 파일 경로
        turns_path (str): 0_turns.jsonl 경로 (참조용)

    Returns:
        dict: {
            "status": "success" | "error",
            "output": "3_keywords.json",
            "metadata": {
                "keyword_count": 15,
                "api_calls": 1,
                "processing_time": 2.8
            }
        }
    """
```

### Stage 4: Layout Generation (Agent 1)

```python
def run(
    input_path: str,
    output_path: str,
    context_path: str,
    layout_type: str = "hierarchical",
    layout_direction: str = "top-down",
    **kwargs
) -> dict:
    """
    마인드맵 레이아웃 생성

    Args:
        input_path (str): 3_keywords.json 경로
        output_path (str): 출력 JSON 파일 경로
        context_path (str): 2_context.json 경로 (참조용)
        layout_type (str): 레이아웃 타입 ("hierarchical", "radial", "organic")
        layout_direction (str): 방향 ("top-down", "left-right", "radial")

    Returns:
        dict: {
            "status": "success" | "error",
            "output": "4_graph.json",
            "metadata": {
                "node_count": 20,
                "edge_count": 19,
                "api_calls": 1,
                "processing_time": 4.2
            }
        }
    """
```

---

## 3. 평가 함수 시그니처

### Context Rubric (Agent 2)

```python
def evaluate_context(
    context_json: str,
    embeddings_npy: str,
    session_split_json: str,
    golden_annotations: dict,
    processing_time: float,
    weights: Optional[Dict[str, float]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    맥락 루브릭 평가 (10개 메트릭)

    Args:
        context_json (str): 2_context.json 파일 경로
        embeddings_npy (str): 임베딩 파일 경로
        session_split_json (str): 1_session_split.json 파일 경로
        golden_annotations (dict): Golden Set 주석 데이터
        processing_time (float): Stage 2 처리 시간 (초)
        weights (dict, optional): 메트릭별 가중치

    Returns:
        dict: {
            "rubric_type": "context",
            "scores": {
                "semantic_coherence": {"score": 0.85, "details": {...}},
                "topic_coverage": {"score": 0.92, "details": {...}},
                ...  # 10개 메트릭
            },
            "weights": {
                "semantic_coherence": 0.15,
                "topic_coverage": 0.12,
                ...
            },
            "weighted_score": 0.8178
        }
    """
```

### Layout Rubric (Agent 2)

```python
def evaluate_layout(
    graph_json: str,
    keywords_json: str,
    golden_annotations: dict,
    processing_time: float,
    weights: Optional[Dict[str, float]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    레이아웃 루브릭 평가 (10개 메트릭)

    Args:
        graph_json (str): 4_graph.json 파일 경로
        keywords_json (str): 3_keywords.json 파일 경로
        golden_annotations (dict): Golden Set 주석 데이터
        processing_time (float): Stage 4 처리 시간 (초)
        weights (dict, optional): 메트릭별 가중치

    Returns:
        dict: {
            "rubric_type": "layout",
            "scores": {
                "tree_edit_distance": {"score": 0.78, "details": {...}},
                "depth_balance": {"score": 0.65, "details": {...}},
                ...  # 10개 메트릭
            },
            "weights": {...},
            "weighted_score": 0.5960
        }
    """
```

### Comprehensive Rubric (Agent 2)

```python
def evaluate_comprehensive(
    graph_json: str,
    context_score: float,
    layout_score: float,
    golden_annotations: dict,
    stage_results: Dict[str, str],
    user_ratings: List[float],
    total_time_sec: float,
    api_calls: int,
    error_count: int = 0,
    total_runs: int = 1,
    weights: Optional[Dict[str, float]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    종합 루브릭 평가 (10개 메트릭)

    Args:
        graph_json (str): 4_graph.json 파일 경로
        context_score (float): Context Rubric 점수
        layout_score (float): Layout Rubric 점수
        golden_annotations (dict): Golden Set 주석 데이터
        stage_results (dict): 각 Stage별 실행 결과 {"stage_1": "success", ...}
        user_ratings (list): 사용자 평점 리스트 [4.0, 4.5, 3.5, ...]
        total_time_sec (float): 전체 파이프라인 실행 시간 (초)
        api_calls (int): 총 API 호출 횟수
        error_count (int): 에러 발생 횟수
        total_runs (int): 총 실행 횟수 (재현성 테스트)
        weights (dict, optional): 메트릭별 가중치

    Returns:
        dict: {
            "rubric_type": "comprehensive",
            "scores": {
                "end_to_end_quality": {"score": 0.88, "details": {...}},
                "user_preference_alignment": {"score": 0.92, "details": {...}},
                ...  # 10개 메트릭
            },
            "weights": {...},
            "weighted_score": 0.9100
        }
    """
```

---

## 4. 에러 핸들링

### 표준 에러 응답 포맷

**모든 함수는 에러 시 동일한 포맷 반환**:

```python
def handle_error(error_type: str, message: str, details: dict = None) -> dict:
    """
    표준 에러 응답 생성

    Args:
        error_type: "ValidationError", "APIError", "FileNotFoundError", etc.
        message: 에러 메시지
        details: 추가 상세 정보

    Returns:
        {
            "status": "error",
            "error_type": "ValidationError",
            "message": "Schema validation failed for context.json",
            "details": {
                "failed_field": "session_id",
                "expected": "^conv_[0-9]{3}$",
                "actual": "test_conv_001"
            }
        }
    """
    return {
        "status": "error",
        "error_type": error_type,
        "message": message,
        "details": details or {}
    }
```

### 에러 타입 목록

| 에러 타입 | 설명 | 담당 |
|----------|------|------|
| `ValidationError` | JSON 스키마 검증 실패 | All |
| `APIError` | OpenAI API 호출 실패 | Agent 1 |
| `FileNotFoundError` | 입력 파일 없음 | All |
| `ProcessingError` | 데이터 처리 중 에러 | All |
| `MetricCalculationError` | 메트릭 계산 실패 | Agent 2 |
| `ConfigurationError` | 설정 오류 | All |

### 에러 핸들링 예시

```python
# Agent 1 (파이프라인)
try:
    output = process_data(input_data)
    validate_json(output, schema_path)
except ValidationError as e:
    return handle_error(
        "ValidationError",
        f"Output validation failed: {str(e)}",
        {"schema": schema_path, "data": output}
    )
except Exception as e:
    return handle_error(
        "ProcessingError",
        f"Unexpected error: {str(e)}",
        {"traceback": traceback.format_exc()}
    )

# Agent 2 (평가)
try:
    score = calculate_metric(data)
    if score is None:
        return handle_error(
            "MetricCalculationError",
            "Failed to calculate metric",
            {"metric_name": "semantic_coherence"}
        )
except Exception as e:
    return handle_error(
        "MetricCalculationError",
        f"Error in metric calculation: {str(e)}",
        {"metric_name": "semantic_coherence"}
    )
```

---

## 5. 로깅 표준

### 로깅 레벨

| 레벨 | 용도 | 예시 |
|------|------|------|
| `DEBUG` | 상세 디버깅 정보 | "Sending GPT request: {prompt}" |
| `INFO` | 일반 정보 | "Stage 2 processing started" |
| `WARNING` | 경고 (계속 실행 가능) | "Low confidence score: 0.3" |
| `ERROR` | 에러 (복구 시도) | "API call failed, retrying..." |
| `CRITICAL` | 치명적 에러 (중단) | "Configuration file missing" |

### 로깅 포맷

**모든 Agent는 동일한 포맷 사용**:

```python
import logging

# 모듈 로거 생성
logger = logging.getLogger(__name__)

# 로깅 예시
logger.debug(f"[Stage 2] Request payload: {payload}")
logger.info(f"[Stage 2] Processing file: {input_path}")
logger.warning(f"[Stage 2] Low confidence: {score:.2f}")
logger.error(f"[Stage 2] API error: {error_msg}")
logger.critical(f"[Stage 2] Fatal error: {error_msg}")
```

### 로깅 설정 (공통)

```python
# logging_config.py (공통 사용)
import logging

def setup_logging(log_level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler('logs/mindmap_lab.log'),
            logging.StreamHandler()
        ]
    )
```

---

## 6. 테스트 데이터

### Mock 데이터 위치

**모든 Agent가 공유하는 테스트 데이터**:

```
tests/fixtures/
├── mock_turns.jsonl              # Stage 0 출력
├── mock_session_split.json       # Stage 1 출력
├── mock_context.json             # Stage 2 출력
├── mock_keywords.json            # Stage 3 출력
├── mock_graph.json               # Stage 4 출력
├── mock_embeddings.json          # 임베딩 데이터
└── mock_golden_annotations.json  # Golden Set 주석
```

### Mock 데이터 사용법

```python
# Agent 1: 파이프라인 테스트
def test_context_analyzer():
    result = analyze_context(
        input_path="tests/fixtures/mock_session_split.json",
        output_path="/tmp/test_context.json",
        turns_path="tests/fixtures/mock_turns.jsonl"
    )
    assert result["status"] == "success"

    # 출력 검증
    with open("/tmp/test_context.json") as f:
        output = json.load(f)
    validate_json(output, "configs/schema/context_schema.json")

# Agent 2: 평가 테스트
def test_context_evaluation():
    result = evaluate_context(
        context_json="tests/fixtures/mock_context.json",
        embeddings_npy="tests/fixtures/mock_embeddings.npy",
        session_split_json="tests/fixtures/mock_session_split.json",
        golden_annotations=load_golden_annotations(),
        processing_time=2.5
    )
    assert result["weighted_score"] > 0.7

# Agent 3: E2E 테스트
def test_full_pipeline():
    # 전체 파이프라인 Mock 테스트
    results = run_pipeline(
        input_path="tests/fixtures/mock_turns.jsonl",
        use_mock=True
    )
    assert all(r["status"] == "success" for r in results)
```

### Mock 데이터 업데이트 규칙

1. **추가 시**: 새로운 Mock 데이터 추가 → 모든 Agent에게 알림
2. **수정 시**: 기존 Mock 데이터 수정 → PR에 명시 + 영향받는 테스트 확인
3. **삭제 시**: 사용하지 않는 Mock 데이터 삭제 → 의존성 체크 후 삭제

---

## 7. 유틸리티 함수 (공통)

### 파일 I/O (`agents/utils/file_io.py`)

```python
def load_json(file_path: str) -> dict:
    """JSON 파일 로드"""
    pass

def save_json(data: dict, file_path: str, validate_schema: str = None):
    """JSON 파일 저장 (스키마 검증 포함)"""
    pass

def load_jsonl(file_path: str) -> List[dict]:
    """JSONL 파일 로드"""
    pass

def save_jsonl(data: List[dict], file_path: str):
    """JSONL 파일 저장"""
    pass
```

### 스키마 검증 (`agents/utils/schema_validator.py`)

```python
def validate_json(data: dict, schema_path: str) -> bool:
    """
    JSON 데이터를 스키마와 대조하여 검증

    Raises:
        ValidationError: 검증 실패 시
    """
    pass

def load_schema(schema_path: str) -> dict:
    """스키마 파일 로드"""
    pass
```

### GPT 클라이언트 (`agents/utils/gpt_client.py`)

```python
def call_gpt(
    prompt: str,
    system_message: str = "",
    model: str = "gpt-4o",
    temperature: float = 0.0,
    max_tokens: int = 4096,
    response_format: dict = None
) -> dict:
    """
    GPT API 호출 (재시도 로직 포함)

    Returns:
        {
            "status": "success" | "error",
            "response": "...",
            "tokens": 1234,
            "cost": 0.05
        }
    """
    pass
```

---

## 8. 인터페이스 버전 관리

### 현재 버전: v1.0.0

**변경 시 규칙**:
- Major (v2.0.0): 호환성 깨지는 변경 (함수 시그니처 변경)
- Minor (v1.1.0): 기능 추가 (하위 호환성 유지)
- Patch (v1.0.1): 버그 수정

**변경 이력**:
- `v1.0.0` (2025-01-15): 초기 인터페이스 정의

---

## 9. 체크리스트

### Agent 1 (파이프라인) 체크리스트
- [ ] 모든 Stage 함수가 표준 시그니처 준수
- [ ] 출력 JSON이 스키마 검증 통과
- [ ] 에러 핸들링 구현
- [ ] 로깅 추가

### Agent 2 (평가) 체크리스트
- [ ] 모든 평가 함수가 표준 시그니처 준수
- [ ] 입력 JSON이 스키마 검증 통과
- [ ] 반환 포맷 일관성 유지
- [ ] 에러 핸들링 구현

### Agent 3 (통합) 체크리스트
- [ ] E2E 테스트가 모든 인터페이스 커버
- [ ] Mock 데이터 최신 상태 유지
- [ ] 통합 테스트 통과
- [ ] 문서화 최신화

---

**마지막 업데이트**: 2025-01-15
**버전**: v1.0.0
