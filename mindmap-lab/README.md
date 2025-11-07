# 🧪 마인드맵 생성 조합 실험실

GPT-4o API 기반 마인드맵 자동 생성 시스템 - 20개 대화 × 15개 조합 = 300회 실험

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
