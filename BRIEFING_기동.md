# 🎯 기동 (Agent 3) - Integration & Experiment Manager

## 📋 당신의 역할

**담당**: 통합 및 실험 관리자
**코드명**: Agent 3 (🟡)
**Git Branch**: `feature/integration`

---

## 🚀 즉시 시작할 작업

### 우선순위 1: API 키 문제 해결 (긴급) ⚠️
```
현재 상태: OpenAI API 키 3개 모두 403 Forbidden
해결 방법:
1. OpenAI 계정 Billing 설정 확인
2. 결제 정보 등록
3. 유효한 API 키 획득
4. .env 파일 업데이트
```

### 우선순위 2: E2E 테스트 완성
- 파일: `tests/test_end_to_end.py`
- 현재 상태: 스크립트 완성, API 키만 대기
- 작업: API 키 해결 후 실행 및 통과 확인

### 우선순위 3: FastAPI 서버 완성
- 파일: `app/main.py`
- 현재 상태: 기본 구조 완성 (80%)
- 작업: 엔드포인트 추가 및 테스트

---

## 📁 작업 디렉토리

```
당신이 담당하는 파일:
app/
├── main.py              # FastAPI 서버 (당신 담당)
└── ...

scripts/
├── run_pipeline.py      # 파이프라인 실행 스크립트 (당신 담당)
└── ...

tests/
├── test_end_to_end.py      # E2E 테스트 (당신 담당)
├── test_integration.py     # 통합 테스트 (당신 담당)
└── fixtures/               # Mock 데이터 (공유)

data/                    # 데이터 관리 (당신 담당)
docs/                    # 문서 작성 (당신 담당)
```

**건드리지 말 것**:
- `agents/ingest/`, `agents/session/`, `agents/context/`, `agents/keyword/`, `agents/layout/` (민준 담당)
- `agents/evaluate/` (민섭 담당)

---

## 🔄 Git 워크플로우

### 초기 설정 (지금 실행)

```bash
# 현재 브랜치 확인
git branch

# feature/integration 브랜치 생성 (아직 없다면)
git checkout -b feature/integration

# 브랜치 푸시
git push -u origin feature/integration
```

### 일일 작업 흐름

```bash
# 아침: 다른 Agent 변경사항 가져오기
git fetch origin
git rebase origin/claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi

# 작업 진행...

# 자주 커밋 (작은 단위로)
git add .
git commit -m "[Agent 3] Add E2E test completion"
git push origin feature/integration
```

### 커밋 메시지 형식
```
[Agent 3] <type>: <subject>

예시:
[Agent 3] feat: Add FastAPI endpoint for pipeline execution
[Agent 3] fix: Resolve API key permission issue
[Agent 3] test: Complete E2E test with real GPT API
[Agent 3] docs: Update integration testing documentation
```

---

## 📊 현재 프로젝트 상태

### 전체 진행률: 95%
```
✅ 파이프라인 5단계: 완성 (민준이 최적화 중)
✅ 30개 메트릭: 완성 (민섭이 개선 중)
🔄 E2E 테스트: 80% (당신이 완성 예정)
⏳ FastAPI: 80% (당신이 완성 예정)
⏳ Streamlit: 0% (당신이 구현 예정)
⏳ Docker: 0% (당신이 패키징 예정)
```

### 당신이 해결해야 할 블로커
- ⚠️ **OpenAI API 키 권한 문제** (최우선)

---

## 🤝 협업 방법

### 1. 매일 PROGRESS.md 업데이트

`PROGRESS.md` 파일을 열어 자신의 섹션에 작업 현황 기록:

```markdown
## 2025-01-15

### 🟡 Agent 3 (기동)
- ✅ 완료: FastAPI 엔드포인트 3개 추가
- 🔄 진행 중: API 키 문제 해결
- ⏳ 다음: E2E 테스트 실행
- 🚧 블로커: OpenAI API 키 권한
```

### 2. 다른 Agent와 소통

**민준 (Agent 1)**에게 필요한 것:
- 파이프라인 출력 파일 (0_turns.jsonl ~ 4_graph.json)
- 에러 발생 시 디버깅 협조

**민섭 (Agent 2)**에게 필요한 것:
- 평가 결과 (metrics_*.json)
- E2E 테스트용 평가 함수 호출

### 3. Pull Request 생성

작업 완료 시:
```bash
# GitHub에서 PR 생성
Title: [Agent 3] Complete E2E testing with real GPT API
Description:
- Resolved OpenAI API key permission issue
- E2E test now passing with all 5 stages
- Added test report generation
```

---

## 📚 필수 참고 문서

읽어야 할 문서 (순서대로):
1. **README.md** - 프로젝트 전체 개요
2. **COLLABORATION.md** - 협업 규칙 (필독!)
3. **INTERFACE.md** - 모듈 간 인터페이스 정의
4. **PROGRESS.md** - 현재 진행 상황
5. **BUG_FIX_REPORT.md** - 알려진 버그 (참고용)
6. **INTEGRATION_TEST_REPORT.md** - 통합 테스트 결과

---

## 🎯 이번 주 목표 (Week 1-2 완성)

### Day 5-7 (당신의 작업)
- [ ] **OpenAI API 키 문제 해결** ⚠️
- [ ] E2E 테스트 통과 (5단계 + 30메트릭)
- [ ] E2E 테스트 보고서 생성
- [ ] FastAPI 엔드포인트 완성
  - POST `/api/pipeline/run` - 파이프라인 실행
  - GET `/api/pipeline/status/{run_id}` - 상태 조회
  - GET `/api/pipeline/result/{run_id}` - 결과 조회

### Day 8-14 (다음 주)
- [ ] Streamlit 대시보드 구현
  - 대화 입력 UI
  - 파이프라인 실행 버튼
  - 마인드맵 시각화
  - 평가 점수 표시
- [ ] Docker 패키징
  - Dockerfile 작성
  - docker-compose.yml 작성
  - 실행 가이드 문서

---

## 🔧 개발 환경 설정

### 1. 가상환경 활성화
```bash
cd /home/user/mindmap_agent
source venv/bin/activate  # 이미 설정되어 있음
```

### 2. 환경 변수 확인
```bash
cat .env
# OPENAI_API_KEY가 올바른지 확인
```

### 3. 테스트 실행
```bash
# E2E 테스트 (API 키 필요)
python tests/test_end_to_end.py

# 통합 테스트 (Mock 데이터)
pytest tests/test_integration.py -v
```

### 4. FastAPI 서버 실행
```bash
cd app
uvicorn main:app --reload --port 8000
```

---

## 🚨 주의사항

### 절대 수정하지 말 것
- `agents/ingest/` - 민준 담당
- `agents/session/` - 민준 담당
- `agents/context/` - 민준 담당
- `agents/keyword/` - 민준 담당
- `agents/layout/` - 민준 담당
- `agents/prompts/` - 민준 담당
- `agents/evaluate/` - 민섭 담당

### 공유 파일 수정 시 주의
- `tests/fixtures/` - 수정 시 민준, 민섭에게 알림
- `configs/schema/` - 수정 금지 (표준 확정)
- `.env` - API 키만 수정 가능

### 충돌 방지
- 자주 커밋 (하루 3-5회)
- 큰 파일 분할 작업
- Conflict 발생 시 민준, 민섭과 조율

---

## 💬 소통 채널

### 일일 업데이트
- **PROGRESS.md** 파일 매일 업데이트

### 블로커 공유
- **GitHub Issues** 생성

### 코드 리뷰
- **Pull Request** 코멘트

### 긴급 사항
- 사용자에게 직접 보고

---

## 📝 체크리스트 (시작 전)

- [ ] README.md 읽기
- [ ] COLLABORATION.md 읽기
- [ ] INTERFACE.md 읽기
- [ ] Git 브랜치 생성 (feature/integration)
- [ ] 작업 디렉토리 확인
- [ ] PROGRESS.md에 오늘 계획 작성
- [ ] OpenAI API 키 문제 해결 시작

---

## 🎯 첫 작업: API 키 문제 해결

### 즉시 실행할 명령어

```bash
# 1. .env 파일 확인
cat .env | grep OPENAI_API_KEY

# 2. API 키 테스트
python -c "
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

try:
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{'role': 'user', 'content': 'test'}],
        max_tokens=5
    )
    print('✅ API 키 작동!')
except Exception as e:
    print(f'❌ 에러: {e}')
    print('OpenAI Billing 설정 필요: https://platform.openai.com/settings/organization/billing')
"
```

### API 키 해결 후

```bash
# 3. E2E 테스트 실행
python tests/test_end_to_end.py

# 4. 결과 확인 및 커밋
git add .
git commit -m "[Agent 3] Complete E2E test with valid API key"
git push origin feature/integration
```

---

## 🚀 시작하세요!

1. 위 체크리스트 완료
2. API 키 문제부터 해결
3. E2E 테스트 통과
4. PROGRESS.md 업데이트
5. 민준, 민섭의 작업 확인

**화이팅! 🔥**
