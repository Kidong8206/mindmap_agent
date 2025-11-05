# 🧠 Mindmap Laboratory

> **GPT API 기반 마인드맵 자동 생성 파이프라인**
>
> 대화 데이터를 분석하여 자동으로 마인드맵을 생성하는 연구 시스템

---

## 📋 프로젝트 개요

### 핵심 철학: "코딩은 최소화, GPT API는 최대화"

전통적인 NLP 알고리즘 구현 대신 **GPT-4o API**를 활용하여:
- ✅ 구현 시간 90% 단축 (6개월 → 2-3주)
- ✅ 100% JSON 출력 일관성 보장
- ✅ 한국어 맥락 이해 우수
- ✅ 유지보수 부담 최소화

### 5단계 파이프라인

```
Raw Conversation
      ↓
[Stage 0] GPT Preprocessing → 0_turns.jsonl
      ↓
[Stage 1] GPT Session Classification → 1_session_split.json
      ↓
[Stage 2] GPT Context Analysis → 2_context.json
      ↓
[Stage 3] GPT Keyword Extraction → 3_keywords.json
      ↓
[Stage 4] GPT Layout Generation → 4_graph.json
      ↓
[Visualization] NetworkX + Matplotlib → visualization.png
```

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 1. 저장소 클론
git clone <repository-url>
cd mindmap_agent

# 2. Python 환경 생성 (Python 3.10+)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 OPENAI_API_KEY 설정
```

### 2. OpenAI API 키 설정

`.env` 파일을 열고 다음을 수정:

```bash
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.0
```

### 3. 첫 마인드맵 생성

#### 샘플 대화 파일 생성

`data/raw/sample_conversation.txt`:
```
user: 안녕하세요, React Hook에 대해 알려주세요.
assistant: 안녕하세요! React Hook은 함수형 컴포넌트에서 상태와 생명주기 기능을 사용할 수 있게 해주는 기능입니다.
user: useState는 어떻게 사용하나요?
assistant: useState는 상태를 관리하는 Hook입니다. const [state, setState] = useState(initialValue) 형태로 사용합니다.
user: 예제 코드를 보여주세요.
assistant: 다음과 같이 사용할 수 있습니다...
```

#### 파이프라인 실행

```bash
python scripts/run_pipeline.py data/raw/sample_conversation.txt
```

#### 결과 확인

```
outputs/runs/run_20250115_143000_conv_001/
├── 0_turns.jsonl              # Stage 0 결과
├── 1_session_split.json       # Stage 1 결과
├── 2_context.json             # Stage 2 결과
├── 3_keywords.json            # Stage 3 결과
├── 4_graph.json               # Stage 4 결과
├── visualization.png          # 마인드맵 이미지
└── metadata.json              # 실행 메타데이터
```

---

## 📖 사용법

### CLI 사용

```bash
# 기본 실행 (hierarchical 레이아웃)
python scripts/run_pipeline.py data/raw/conversation.txt

# 레이아웃 지정
python scripts/run_pipeline.py data/raw/conversation.txt \
  --layout radial \
  --direction radial-out

# 세션 ID 지정
python scripts/run_pipeline.py data/raw/conversation.txt \
  --session-id conv_001

# 출력 디렉토리 지정
python scripts/run_pipeline.py data/raw/conversation.txt \
  --output outputs/my_experiment
```

### API 서버 사용

#### 1. 서버 시작

```bash
# 개발 모드
python app/main.py

# 또는 uvicorn 직접 사용
uvicorn app.main:app --reload --port 8000
```

#### 2. API 호출

**파이프라인 실행**:
```bash
curl -X POST "http://localhost:8000/pipeline/run" \
  -F "file=@data/raw/conversation.txt" \
  -F "layout_type=hierarchical" \
  -F "layout_direction=top-down"
```

**결과 조회**:
```bash
# 메타데이터
curl "http://localhost:8000/results/{run_id}/metadata"

# 그래프 JSON
curl "http://localhost:8000/results/{run_id}/graph"

# 시각화 이미지
curl "http://localhost:8000/results/{run_id}/visualization" -o mindmap.png

# 최근 실행 목록
curl "http://localhost:8000/results/list?limit=10"
```

#### 3. API 문서

브라우저에서 `http://localhost:8000/docs` 접속

---

## 🏗️ 아키텍처

### 디렉토리 구조

```
mindmap_agent/
├── agents/                      # 파이프라인 모듈
│   ├── ingest/                  # Stage 0: 전처리
│   │   └── gpt_preprocessor.py
│   ├── session/                 # Stage 1: 세션 분류
│   │   └── gpt_session_classifier.py
│   ├── context/                 # Stage 2: 맥락 분석
│   │   └── gpt_context_analyzer.py
│   ├── keyword/                 # Stage 3: 키워드 추출
│   │   └── gpt_keyword_extractor.py
│   ├── layout/                  # Stage 4: 레이아웃 생성
│   │   └── gpt_layout_generator.py
│   ├── prompts/                 # 프롬프트 템플릿
│   │   └── templates.py
│   ├── utils/                   # 유틸리티
│   │   ├── gpt_client.py        # GPT API 래퍼
│   │   ├── schema_validator.py  # JSON 검증
│   │   └── file_io.py           # 파일 I/O
│   └── visualizer.py            # 시각화
│
├── app/                         # FastAPI 백엔드
│   └── main.py
│
├── configs/                     # 설정 파일
│   └── schema/                  # JSON 스키마 (8개)
│       ├── turns_schema.json
│       ├── session_split_schema.json
│       ├── context_schema.json
│       ├── keywords_schema.json
│       └── graph_schema.json
│
├── scripts/                     # 실행 스크립트
│   └── run_pipeline.py
│
├── data/                        # 데이터 저장소
│   ├── raw/                     # 원본 대화
│   ├── golden/                  # 골든 데이터셋
│   └── processed/               # 처리된 데이터
│
├── outputs/                     # 실험 결과
│   └── runs/                    # 실행 결과 디렉토리
│
└── cache/                       # GPT 응답 캐시
    └── gpt_responses/
```

### 데이터 플로우

```
입력 (Raw Conversation)
  ↓
[GPT] 개인정보 마스킹, 정제 → turns.jsonl
  ↓
[GPT] 주제 경계 탐지 → sessions (주제별 분할)
  ↓
[GPT] Main/Side Path 구분 → contexts (경로 구조)
  ↓
[GPT] 키워드 추출 (5-10개) → keywords (경로별)
  ↓
[GPT] 노드 좌표 계산 → graph (x, y, color, size)
  ↓
[NetworkX] PNG 렌더링 → visualization.png
```

---

## 🎛️ 레이아웃 옵션

### 1. Hierarchical (계층형) - 기본값

```bash
python scripts/run_pipeline.py input.txt \
  --layout hierarchical \
  --direction top-down
```

- **특징**: 트리 구조, 루트에서 아래로 확장
- **적합**: 명확한 주제 계층이 있는 대화

### 2. Radial (방사형)

```bash
python scripts/run_pipeline.py input.txt \
  --layout radial \
  --direction radial-out
```

- **특징**: 중심에서 바깥으로 확장
- **적합**: 하나의 중심 주제에서 여러 하위 주제로 분기

### 3. Timeline (타임라인)

```bash
python scripts/run_pipeline.py input.txt \
  --layout timeline \
  --direction chronological
```

- **특징**: 시간 순서대로 수평 배치
- **적합**: 순차적 진행이 중요한 대화

### 4. Force Directed (물리 시뮬레이션)

```bash
python scripts/run_pipeline.py input.txt \
  --layout force_directed \
  --direction top-down
```

- **특징**: 노드 간 힘 기반 자동 배치
- **적합**: 복잡한 연결 관계

---

## 💾 캐싱 시스템

### GPT 응답 캐싱

동일한 프롬프트 재호출 시 비용 절감:

```python
# 자동 캐싱 (기본 활성화)
response = cached_gpt_call(prompt)  # 첫 호출: API 요청
response = cached_gpt_call(prompt)  # 두 번째: 캐시 사용 (무료!)
```

### 캐시 관리

```bash
# 캐시 디렉토리 확인
ls cache/gpt_responses/

# 캐시 삭제 (비용 재발생 주의!)
rm -rf cache/gpt_responses/*
```

---

## 📊 비용 계산

### 1회 대화 처리 비용 (GPT-4o 기준)

| Stage | 토큰 수 | 비용 |
|-------|---------|------|
| Stage 0: Preprocessing | ~1,000 | $0.02 |
| Stage 1: Session | ~2,000 | $0.04 |
| Stage 2: Context | ~3,000 | $0.06 |
| Stage 3: Keyword | ~1,500 | $0.03 |
| Stage 4: Layout | ~2,500 | $0.05 |
| **Total** | **~10,000** | **~$0.20** |

### 캐싱 효과

- 첫 실행: $0.20
- 재실행 (캐시 적중): $0.00
- **비용 절감: 100%**

---

## 🔧 고급 설정

### 환경 변수 (.env)

```bash
# GPT API
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.0  # 일관성 보장
OPENAI_MAX_TOKENS=4096

# 재시도 설정
MAX_RETRIES=3
RETRY_DELAY=2

# 캐싱
CACHE_ENABLED=true
CACHE_TTL=604800  # 7일

# 로깅
LOG_LEVEL=INFO
```

### 프롬프트 커스터마이징

`agents/prompts/templates.py`에서 프롬프트 수정:

```python
SESSION_CLASSIFY_PROMPT = """
당신의 커스텀 프롬프트...
"""
```

---

## 🧪 테스트

```bash
# 단위 테스트 실행
pytest tests/

# 특정 모듈 테스트
pytest tests/test_agents/test_preprocessor.py

# 커버리지 확인
pytest --cov=agents tests/
```

---

## 🐛 문제 해결

### 1. OpenAI API 에러

**증상**: `RateLimitError: Rate limit exceeded`

**해결**:
```bash
# .env에서 재시도 설정 증가
MAX_RETRIES=5
RETRY_DELAY=4
```

### 2. JSON 파싱 에러

**증상**: `JSONDecodeError: Expecting value`

**해결**:
- GPT가 잘못된 형식 반환 시 자동 재시도 (최대 3회)
- 프롬프트 재검토: `response_format={"type": "json_object"}` 확인

### 3. 메모리 부족

**증상**: 대화가 매우 긴 경우 (>500 턴)

**해결**:
```bash
# 최대 토큰 수 증가
OPENAI_MAX_TOKENS=8192
```

---

## 📚 참고 문서

- [OpenAI API 문서](https://platform.openai.com/docs)
- [NetworkX 문서](https://networkx.org/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)

---

## 🤝 기여

이 프로젝트는 강원과학고 R&E 프로젝트입니다.

---

## 📝 라이선스

MIT License

---

## 🎓 인용

```bibtex
@software{mindmap_laboratory,
  title={Mindmap Laboratory: GPT-based Mindmap Generation Pipeline},
  author={Your Name},
  year={2025},
  url={https://github.com/your-username/mindmap_agent}
}
```

---

## 📧 문의

- 이슈: [GitHub Issues](https://github.com/your-username/mindmap_agent/issues)
- 이메일: your.email@example.com

---

**Happy Mindmapping! 🧠✨**
