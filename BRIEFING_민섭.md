# 🎯 민섭 (Agent 2) - Evaluation & Metrics Specialist

## 👋 환영합니다!

**담당**: 평가 시스템 전문가
**코드명**: Agent 2 (🟢)
**Git Branch**: `feature/evaluation`

---

## 📖 프로젝트 개요

### Mindmap Laboratory란?

**목표**: 대화 데이터 → GPT 파이프라인 → 마인드맵 자동 생성

**당신의 역할**: 생성된 마인드맵의 품질을 **30개 메트릭**으로 평가

### 왜 평가 시스템이 중요한가?

```
연구 목표: 100가지 조합 × 100개 대화 = 10,000회 실험
          ↓
    어떤 조합이 최고인가?
          ↓
    당신의 평가 시스템으로 측정!
          ↓
    데이터 기반 최적 조합 발견
```

### 평가 시스템 구조

```
파이프라인 출력 (민준이 생성)
  ↓
[Context Rubric] 맥락 평가 (10개 메트릭) ← 당신 담당
  ↓
[Layout Rubric] 레이아웃 평가 (10개 메트릭) ← 당신 담당
  ↓
[Comprehensive Rubric] 종합 평가 (10개 메트릭) ← 당신 담당
  ↓
최종 점수 (0.0 ~ 1.0)
```

---

## 🚀 당신의 역할: 평가 시스템 전문가

### 담당 범위

**당신이 책임지는 것**:
1. **30개 메트릭 구현** (이미 완료!) ✅
2. **저점수 메트릭 개선** (당신의 작업)
3. **Golden Set 비교 로직** 구현
4. **메트릭 가중치 학습** (Week 3-4)

**다른 사람 담당**:
- 파이프라인 (Stage 0-4) → 민준 (Agent 1)
- E2E 테스트, API, UI → 기동 (Agent 3)

---

## 📁 작업 디렉토리

```
당신이 담당하는 파일들:

agents/evaluate/
├── __init__.py
│
├── evaluate_context.py          # Context Rubric (10개 메트릭)
│   ├── semantic_coherence       # 의미 일관성
│   ├── topic_coverage           # 주제 커버리지
│   ├── session_segmentation     # 세션 분할
│   ├── context_embedding_sim    # 임베딩 유사도
│   ├── dialogue_type_accuracy   # 대화 유형 정확도
│   ├── key_points_extraction    # 핵심 포인트
│   ├── topic_stability          # 주제 안정성
│   ├── summary_path_consistency # 요약 일관성 ⚠️ 0.0점
│   ├── turn_level_coherence     # 턴 일관성
│   └── processing_latency       # 처리 시간
│
├── evaluate_layout.py           # Layout Rubric (10개 메트릭)
│   ├── tree_edit_distance       # 트리 편집 거리
│   ├── depth_balance            # 깊이 균형 ⚠️ 0.08점
│   ├── branching_factor         # 분기 계수
│   ├── edge_crossing            # 엣지 교차
│   ├── node_overlap             # 노드 겹침
│   ├── color_contrast           # 색상 대비 ⚠️ 0.0점
│   ├── font_readability         # 폰트 가독성
│   ├── spatial_distribution     # 공간 분포
│   ├── aspect_ratio             # 화면 비율
│   └── layout_aesthetics        # 레이아웃 미학
│
├── evaluate_comprehensive.py   # Comprehensive Rubric (10개 메트릭)
│   ├── end_to_end_quality       # 전체 품질
│   ├── user_preference_align    # 사용자 선호도 (가중치 0.25!)
│   ├── stage_stability          # 단계 안정성
│   ├── error_recovery           # 에러 복구
│   ├── output_reproducibility   # 재현성
│   ├── api_cost_efficiency      # API 비용
│   ├── total_latency            # 총 지연시간
│   ├── keyword_graph_alignment  # 키워드-그래프 정렬
│   ├── visual_info_density      # 정보 밀도
│   └── interaction_responsive   # 반응성 ⚠️ 0.0점
│
└── utils/                       # 평가 유틸리티
    ├── __init__.py
    ├── embeddings.py            # 임베딩 계산
    ├── graph_metrics.py         # 그래프 메트릭
    └── comparison.py            # 비교 함수
```

**절대 수정 금지**:
- `agents/ingest/`, `agents/session/`, 등 - 민준 담당
- `app/`, `scripts/` - 기동 담당

---

## 🎯 즉시 시작할 작업

### 우선순위 1: 프로젝트 이해 (30분)

```bash
# 1. 필수 문서 읽기
cat README.md
cat COLLABORATION.md
cat INTERFACE.md
cat PROGRESS.md

# 2. 평가 시스템 코드 확인
ls -la agents/evaluate/
cat agents/evaluate/evaluate_context.py
cat agents/evaluate/evaluate_layout.py
cat agents/evaluate/evaluate_comprehensive.py

# 3. 현재 점수 확인
cat INTEGRATION_TEST_REPORT.md
# Context: 0.8178 (81.78%)
# Layout: 0.5960 (59.60%)
# Comprehensive: 0.9100 (91.00%)
# Overall: 0.7746 (77.46%)
```

### 우선순위 2: Git 브랜치 생성

```bash
# 현재 브랜치 확인
git branch

# feature/evaluation 브랜치 생성
git checkout -b feature/evaluation

# 브랜치 푸시
git push -u origin feature/evaluation

# 최신 상태로 업데이트
git fetch origin
git rebase origin/claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi
```

### 우선순위 3: 저점수 메트릭 개선

**개선이 필요한 메트릭** (⚠️ 표시):

1. **summary_path_consistency: 0.0000**
   - 위치: `agents/evaluate/evaluate_context.py`
   - 문제: Golden keywords 데이터 부족
   - 해결: Mock 데이터로 우선 테스트 로직 개선

2. **depth_balance: 0.0794**
   - 위치: `agents/evaluate/evaluate_layout.py`
   - 문제: Mock graph의 깊이 분포가 불균형
   - 해결: 계산 로직 재검토

3. **color_contrast: 0.0000**
   - 위치: `agents/evaluate/evaluate_layout.py`
   - 문제: Mock data의 색상이 유사
   - 해결: 색상 대비 계산 로직 개선

4. **interaction_responsiveness: 0.0000**
   - 위치: `agents/evaluate/evaluate_comprehensive.py`
   - 문제: 계산 로직 오류
   - 해결: 코드 리뷰 및 수정

---

## 📊 현재 프로젝트 상태

### 전체 진행률: 95%

```
✅ 파이프라인 5단계: 100% (민준 담당)
✅ 30개 메트릭: 100% 구현 (당신 담당)
🔄 메트릭 개선: 50% (당신이 완성 예정)
🔄 E2E 테스트: 80% (기동 담당)
⏳ Golden Set: 0% (Week 3-4 계획)
```

### 당신의 작업 현황

```
✅ Context Rubric (10개): 완성
   ├─ 9개 메트릭: 정상 작동 ✅
   └─ 1개 메트릭: 개선 필요 ⚠️ summary_path_consistency

✅ Layout Rubric (10개): 완성
   ├─ 8개 메트릭: 정상 작동 ✅
   └─ 2개 메트릭: 개선 필요 ⚠️ depth_balance, color_contrast

✅ Comprehensive Rubric (10개): 완성
   ├─ 9개 메트릭: 정상 작동 ✅
   └─ 1개 메트릭: 개선 필요 ⚠️ interaction_responsiveness

현재 점수: 0.7746 (77.46%)
목표 점수: 0.8500 (85.00%)
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
# 2. 메트릭 코드 수정
vim agents/evaluate/evaluate_context.py

# 3. 테스트 실행
pytest tests/test_context_rubric.py -v

# 4. 자주 커밋
git add agents/evaluate/evaluate_context.py
git commit -m "[Agent 2] fix: Improve summary_path_consistency calculation"
git push origin feature/evaluation

# === 작업 완료 시 ===
# 5. PROGRESS.md 업데이트
vim PROGRESS.md
git add PROGRESS.md
git commit -m "[Agent 2] docs: Update progress for metric improvements"
git push origin feature/evaluation
```

### 커밋 메시지 형식

```
[Agent 2] <type>: <subject>

Type:
- feat: 새 기능
- fix: 버그 수정
- refactor: 코드 리팩토링
- test: 테스트 추가
- docs: 문서 수정

예시:
[Agent 2] fix: Correct depth_balance metric calculation
[Agent 2] feat: Add Golden Set comparison logic
[Agent 2] test: Add unit test for color_contrast metric
[Agent 2] refactor: Simplify embedding similarity calculation
```

---

## 🔗 인터페이스 표준 (필수 준수!)

### 1. 평가 함수 시그니처 통일

**모든 평가 함수는 동일한 반환 형식**:

```python
def evaluate_*(
    # 필수 입력
    required_json: str,
    golden_annotations: dict,

    # 선택 입력
    weights: Optional[Dict[str, float]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Returns:
        {
            "rubric_type": "context" | "layout" | "comprehensive",
            "scores": {
                "metric_1": {
                    "score": 0.85,
                    "details": {...}
                },
                "metric_2": {
                    "score": 0.92,
                    "details": {...}
                },
                ...
            },
            "weights": {
                "metric_1": 0.12,
                "metric_2": 0.15,
                ...
            },
            "weighted_score": 0.8178
        }
    """
```

### 2. JSON 스키마 검증 (필수!)

**입력 데이터 검증**:

```python
from agents.utils.schema_validator import validate_json

# 입력 파일 로드
with open(context_json) as f:
    context_data = json.load(f)

# 스키마 검증 (필수!)
validate_json(context_data, "configs/schema/context_schema.json")

# 평가 진행
score = calculate_metric(context_data)
```

### 3. 에러 핸들링

```python
def calculate_metric(data: dict) -> float:
    try:
        # 메트릭 계산
        score = compute(data)

        # 유효성 검증
        if score is None or not (0 <= score <= 1):
            logger.warning(f"Invalid score: {score}, returning 0.0")
            return 0.0

        return score

    except Exception as e:
        logger.error(f"Metric calculation failed: {e}")
        return 0.0  # 에러 시 0점
```

### 4. 로깅

```python
import logging

logger = logging.getLogger(__name__)

# 메트릭 계산 시작
logger.info(f"[Context Rubric] Calculating semantic_coherence")

# 중간 결과
logger.debug(f"[Context Rubric] Intermediate score: {score}")

# 경고
logger.warning(f"[Context Rubric] Low score detected: {score}")

# 최종 결과
logger.info(f"[Context Rubric] Final weighted score: {weighted_score:.4f}")
```

---

## 🧪 테스트 작성

### Mock 데이터로 테스트

```python
# tests/test_context_rubric.py

def test_summary_path_consistency():
    """summary_path_consistency 메트릭 테스트"""
    from agents.evaluate.evaluate_context import evaluate_context

    # Mock 데이터 로드
    result = evaluate_context(
        context_json="tests/fixtures/mock_context.json",
        embeddings_npy="tests/fixtures/mock_embeddings.npy",
        session_split_json="tests/fixtures/mock_session_split.json",
        golden_annotations=load_golden_annotations(),
        processing_time=2.5
    )

    # 점수 확인
    score = result["scores"]["summary_path_consistency"]["score"]

    # 개선 목표: 0.0 → 0.7+
    assert score > 0.7, f"Expected > 0.7, got {score}"
```

---

## 🤝 협업 방법

### 1. 매일 PROGRESS.md 업데이트

```markdown
## 2025-01-15

### 🟢 Agent 2 (민섭)
- ✅ 완료: summary_path_consistency 메트릭 개선
- 🔄 진행 중: depth_balance 로직 재검토
- ⏳ 다음: color_contrast 개선
- 🚧 블로커: 없음
```

### 2. 다른 Agent와 소통

**민준 (Agent 1)**과 협업:
- 민준이 생성한 파이프라인 출력을 당신이 평가
- 점수가 낮으면 → 민준에게 피드백
- 점수가 높으면 → 민준의 프롬프트 개선 효과 확인

**기동 (Agent 3)**과 협업:
- 기동이 E2E 테스트할 때 당신의 평가 함수 사용
- 에러 발생 시 디버깅 협조
- 전체 점수 향상 확인

### 3. Conflict 방지

- 자주 커밋 (하루 3-5회)
- `agents/evaluate/` 외부 수정 금지
- 공유 파일 수정 시 알림

---

## 📚 필수 참고 문서

읽어야 할 순서:
1. ✅ **README.md** - 프로젝트 전체 개요
2. ✅ **COLLABORATION.md** - 협업 규칙 (필독!)
3. ✅ **INTERFACE.md** - 인터페이스 표준 (필독!)
4. ✅ **PROGRESS.md** - 현재 진행 상황
5. **INTEGRATION_TEST_REPORT.md** - 30개 메트릭 결과 (참고!)
6. **configs/schema/metrics_*.json** - 평가 스키마

---

## 🎯 이번 주 목표 (Week 1-2 완성)

### Day 5-7 (당신의 작업)

- [ ] **저점수 메트릭 개선**
  - [ ] summary_path_consistency: 0.00 → 0.70+
  - [ ] depth_balance: 0.08 → 0.60+
  - [ ] color_contrast: 0.00 → 0.70+
  - [ ] interaction_responsiveness: 0.00 → 0.60+

- [ ] **Golden Set 비교 로직 추가**
  - [ ] Golden keywords 비교 함수
  - [ ] Golden graph 비교 함수
  - [ ] 유사도 계산 개선

- [ ] **메트릭 문서화**
  - [ ] 각 메트릭의 계산 방법 문서
  - [ ] 개선 전후 비교 리포트

### Day 8-14 (다음 주)

- [ ] **가중치 학습 준비**
  - [ ] 사용자 평점 데이터 수집 방법
  - [ ] Spearman 상관계수 계산
  - [ ] 최적 가중치 학습 알고리즘

---

## 🔧 개발 환경 설정

### 1. Python 환경

```bash
# 가상환경 확인
which python

# 패키지 확인
pip list | grep numpy
pip list | grep scipy
pip list | grep networkx
pip list | grep sentence-transformers
```

### 2. 테스트 실행

```bash
# Context Rubric 테스트
pytest tests/test_context_rubric.py -v

# Layout Rubric 테스트
pytest tests/test_layout_rubric.py -v

# Comprehensive Rubric 테스트
pytest tests/test_comprehensive_rubric.py -v

# 전체 평가 테스트
pytest tests/test_integration.py -v
```

### 3. 개별 메트릭 디버깅

```python
# Python 대화형 모드에서 테스트
python

>>> from agents.evaluate.evaluate_context import evaluate_context
>>> result = evaluate_context(...)
>>> print(result["scores"]["summary_path_consistency"])
```

---

## 🚨 주의사항

### 절대 수정하지 말 것

❌ **금지**:
- `agents/ingest/` - 민준 전용
- `agents/session/` - 민준 전용
- `agents/context/` - 민준 전용
- `agents/keyword/` - 민준 전용
- `agents/layout/` - 민준 전용
- `app/`, `scripts/` - 기동 전용

✅ **허용**:
- `agents/evaluate/` - 당신 전용
- `tests/test_*_rubric.py` - 당신 전용
- `configs/schema/metrics_*.json` - 당신 담당

### 공유 파일 수정 시

- `tests/fixtures/` - Mock 데이터 수정 시 민준, 기동에게 알림
- `agents/utils/` - 수정 시 PR 필수

---

## 💡 메트릭 개선 팁

### 좋은 메트릭의 특징

1. **측정 가능**: 명확한 수치로 표현
2. **재현 가능**: 동일 입력 → 동일 출력
3. **의미 있음**: 사용자 만족도와 상관관계
4. **정규화**: 0.0 ~ 1.0 범위
5. **견고함**: 예외 상황 처리

### 메트릭 개선 프로세스

```
1. 현재 점수 확인 (예: 0.0)
   ↓
2. 코드 리뷰 및 문제점 파악
   ↓
3. 계산 로직 개선
   ↓
4. Mock 데이터로 테스트
   ↓
5. 점수 재확인 (목표: 0.7+)
   ↓
6. 문서화 및 커밋
```

---

## 📝 체크리스트 (시작 전)

- [ ] README.md 읽기
- [ ] COLLABORATION.md 읽기 (필수!)
- [ ] INTERFACE.md 읽기 (필수!)
- [ ] INTEGRATION_TEST_REPORT.md 확인
- [ ] Git 브랜치 생성 (feature/evaluation)
- [ ] 평가 코드 확인
- [ ] 저점수 메트릭 목록 작성
- [ ] PROGRESS.md에 오늘 계획 작성

---

## 🎯 첫 작업: 저점수 메트릭 분석

### 즉시 실행할 명령어

```bash
# 1. Context Rubric 코드 열기
cat agents/evaluate/evaluate_context.py | grep -A 20 "summary_path_consistency"

# 2. 문제점 파악
# - Golden keywords 데이터가 없음
# - 비교 로직이 None 반환

# 3. 개선 계획 작성
vim PROGRESS.md

# 4. 코드 수정 시작
vim agents/evaluate/evaluate_context.py

# 5. 테스트
pytest tests/test_context_rubric.py::test_summary_path_consistency -v

# 6. 커밋
git add .
git commit -m "[Agent 2] fix: Improve summary_path_consistency metric"
git push origin feature/evaluation
```

---

## 🚀 시작하세요!

**당신의 임무**:
1. 저점수 메트릭 개선 → 전체 점수 향상
2. Golden Set 비교 로직 → 정확도 향상
3. 메트릭 문서화 → 이해도 향상

**기대 효과**:
- 전체 점수: 77% → 85%+
- 최적 조합 발견의 정확도 향상
- 연구 목표 달성

---

## 🤝 협업 시작!

**민준 (Agent 1)**은 파이프라인 품질 향상
**기동 (Agent 3)**은 E2E 테스트와 API 개발
**민섭 (당신)**은 평가 정확도 향상

→ 3명이 협력하여 Week 1-2 완성! 🔥

**화이팅!** 💪
