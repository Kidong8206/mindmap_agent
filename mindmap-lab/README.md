# 🧪 마인드맵 생성 조합 실험실

Claude vs GPT-4 API 비교 연구 - 20개 대화 × 15개 조합 = 300회 실험

---

## 🚀 Google Colab 실험 (권장)

### 📓 Claude 실험 노트북

**Colab에서 바로 열기:**
```
https://colab.research.google.com/github/Kidong8206/mindmap_agent/blob/claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi/mindmap-lab/Mindmap_Experiment_Colab.ipynb
```

- **API**: Anthropic Claude Sonnet 4.5
- **비용**: $5-8 | **시간**: 3-5시간 | **실험 수**: 300회

### 📓 GPT-4 실험 노트북

**Colab에서 바로 열기:**
```
https://colab.research.google.com/github/Kidong8206/mindmap_agent/blob/claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi/mindmap-lab/Mindmap_Experiment_GPT_Colab.ipynb
```

- **API**: OpenAI GPT-4 Turbo
- **비용**: $15-25 | **시간**: 2-4시간 | **실험 수**: 300회

### 📊 결과 분석 노트북

**Colab에서 바로 열기:**
```
https://colab.research.google.com/github/Kidong8206/mindmap_agent/blob/claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi/mindmap-lab/Analyze_Results_Colab.ipynb
```

- **기능**: CSV 업로드 → 자동 분석 → 그래프/표 생성 → 다운로드
- **입력**: `experiments.csv` 또는 `experiments_gpt.csv`
- **출력**: 6개 파일 (그래프 4개 + 통계표 2개)

### 📖 상세 실행 가이드

**[COLAB_EXECUTION_GUIDE.md](./COLAB_EXECUTION_GUIDE.md)** - API 키 발급, 단계별 실행 방법, FAQ 등

---

## 🔗 Repository 정보 (Colab GitHub 검색용)

Colab에서 `파일` → `노트 열기` → `GitHub` 탭에서 아래 정보 입력:

```
Owner: Kidong8206
Repository: mindmap_agent
Branch: claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi
```

**파일 선택:**
- Claude 실험: `mindmap-lab/Mindmap_Experiment_Colab.ipynb`
- GPT-4 실험: `mindmap-lab/Mindmap_Experiment_GPT_Colab.ipynb`
- 결과 분석: `mindmap-lab/Analyze_Results_Colab.ipynb`

---

## 📊 비교 연구 설계

이 프로젝트는 **Claude API vs GPT-4 API** 성능 비교를 위해 설계되었습니다.

| 항목 | Claude | GPT-4 |
|------|--------|-------|
| **모델** | claude-sonnet-4-5-20250929 | gpt-4-turbo |
| **비용** | $5-8 | $15-25 |
| **시간** | 3-5시간 | 2-4시간 |
| **API 키** | [console.anthropic.com](https://console.anthropic.com/settings/keys) | [platform.openai.com](https://platform.openai.com/api-keys) |

**비교 방법론**: [COMPARISON_METHODOLOGY.md](./COMPARISON_METHODOLOGY.md)

---

## 📁 프로젝트 구조

```
mindmap-lab/
├── data/              # 데이터
│   ├── conversations/ # 대화 파일 (JSONL)
│   ├── golden_maps/   # 정답 마인드맵 (JSON)
│   ├── sessions/      # Stage 1 출력
│   ├── contexts/      # Stage 2 출력
│   ├── keywords/      # Stage 3 출력
│   └── graphs/        # Stage 4 출력
├── prompts/           # 12개 프롬프트 파일
├── src/               # Python 소스코드
│   ├── lab.py         # 메인 실험 루프
│   ├── gpt_caller.py  # GPT API 래퍼
│   ├── validator.py   # JSON 검증
│   ├── evaluator.py   # 3-metric 평가
│   └── utils.py       # 유틸리티
├── outputs/           # 실험 결과
│   └── registry.csv   # 300회 결과 레지스트리
├── config.yaml        # 15개 조합 정의
└── requirements.txt   # 패키지 의존성
```

## 🚀 빠른 시작

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. API 키 설정
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. 실험 실행
```bash
cd src
python lab.py
```

## 📊 5단계 파이프라인

1. **Stage 1**: 세션 분류 (v1_simple, v2_detailed, v3_strict)
2. **Stage 2**: 맥락 분류 (v1_simple, v2_detailed, v3_strict)
3. **Stage 3**: 키워드 추출 (v1_simple, v2_detailed, v3_strict)
4. **Stage 4**: 마인드맵 생성 (hierarchical, radial, timeline)
5. **Stage 5**: 평가 (node_count 30% + keyword_overlap 40% + depth 30%)

## 🎯 15가지 조합

- **Simple 계열** (3개): simple_hierarchical, simple_radial, simple_timeline
- **Detailed 계열** (3개): detailed_hierarchical, detailed_radial, detailed_timeline
- **Strict 계열** (3개): strict_hierarchical, strict_radial, strict_timeline
- **Hybrid 계열** (6개): 다양한 버전 믹스

## 📈 평가 지표

- **노드 개수** (30%): 최적 10-30개
- **키워드 중복도** (40%): Golden set 대비
- **구조 깊이** (30%): 최적 2-5 레벨

## 📝 데이터 형식

### 대화 파일 (JSONL)
```jsonl
{"turn_id": 0, "role": "user", "content": "마인드맵이 뭐야?"}
{"turn_id": 1, "role": "assistant", "content": "마인드맵은..."}
```

### Golden Map (JSON)
```json
{
  "conversation_id": "conv_001",
  "layout": "hierarchical",
  "graph": {
    "nodes": [...],
    "edges": [...]
  }
}
```

## ⚙️ 주요 특징

- **Temperature 0.0**: 결정적 출력
- **JSON 강제 모드**: 파싱 보장
- **자동 재시도**: 실패 시 1회 재시도
- **중간 저장**: 실험마다 CSV 업데이트
- **검증 시스템**: 각 단계 출력 검증

## 📄 License

MIT
