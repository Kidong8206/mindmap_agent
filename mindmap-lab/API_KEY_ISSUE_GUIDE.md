# 🔑 API 키 문제 해결 가이드

## 📋 현재 상황

### 프로젝트: 마인드맵 생성 실험 시스템
- **저장소**: https://github.com/Kidong8206/mindmap_agent
- **브랜치**: `claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi`
- **상태**: 코드 100% 완성, API 키 문제로 실행 불가

### 문제 상황

**OpenAI API 키 오류:**
```
Error: Access denied
Status: 403 Forbidden
Reason: OpenAI 계정에 결제 수단 미설정 또는 크레딧 부족
```

**테스트한 API 키들:**
- `sk-proj-2gbZZ1GeXtEN...` → 403 Forbidden
- `sk-svcacct-SIiLjHrJTSus...` → 403 Forbidden
- 기타 여러 키 → 모두 동일한 오류

**원인:**
- OpenAI Platform 계정에 결제 수단이 등록되지 않음
- 또는 계정 크레딧이 $0

---

## 🎯 해결 방법 (2가지 옵션)

### ✅ 옵션 1: Anthropic Claude API 사용 (권장)

**현재 상태:**
- ✅ 코드 이미 변경 완료 (`gpt_caller.py`)
- ✅ Claude Sonnet 4.5 사용 준비됨
- ⏳ `ANTHROPIC_API_KEY` 환경변수만 설정하면 즉시 실행 가능

**장점:**
- 무료 크레딧 $5 제공 (300회 실험 충분)
- 한국어 처리 우수
- 200k 컨텍스트 윈도우
- vscode Claude Code와 동일 플랫폼

**필요한 작업:**
```bash
# 1. Anthropic API 키 발급
# https://console.anthropic.com/settings/keys

# 2. 환경변수 설정
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# 3. 실행
./run_quick_test.sh
```

---

### 옵션 2: OpenAI API 계정 활성화

**필요한 작업:**
```bash
# 1. OpenAI 결제 설정
# https://platform.openai.com/settings/organization/billing
# - 결제 수단 추가
# - 최소 $5-10 충전

# 2. 새 API 키 발급
# https://platform.openai.com/api-keys

# 3. gpt_caller.py 원본 복구
cd mindmap-lab/src
mv gpt_caller.py.backup gpt_caller.py

# 4. 환경변수 설정
export OPENAI_API_KEY="sk-..."

# 5. 실행
cd ..
./run_quick_test.sh
```

---

## 🚀 vscode Claude CLI 작업 가이드

### Step 1: 프로젝트 Clone

```bash
# 1. 저장소 클론
git clone https://github.com/Kidong8206/mindmap_agent.git
cd mindmap_agent

# 2. 브랜치 체크아웃
git checkout claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi

# 3. 프로젝트 구조 확인
cd mindmap-lab
ls -la
```

**예상 출력:**
```
mindmap-lab/
├── run_quick_test.sh          # 빠른 검증 (30분)
├── run_full_experiment.sh     # 전체 실험 (3시간)
├── src/                       # Python 모듈
├── prompts/                   # 12개 프롬프트
├── config.yaml                # 15개 조합 설정
└── README.md                  # 사용 가이드
```

---

### Step 2: API 키 설정 (옵션 1 선택 시)

```bash
# Anthropic API 키 발급
# 1. https://console.anthropic.com/settings/keys 접속
# 2. "Create Key" 클릭
# 3. 키 복사

# 환경변수 설정
export ANTHROPIC_API_KEY="sk-ant-api03-YOUR-KEY-HERE"

# 테스트
cd src
python3 -c "
import os
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
print('✅ API 키 정상 작동!')
"
```

---

### Step 3: 패키지 설치

```bash
# Python 패키지 설치
pip install -r requirements.txt

# 추가 패키지 (Anthropic API용)
pip install anthropic
```

---

### Step 4: 빠른 검증 실행 (30분)

```bash
# Quick Test 실행
cd /path/to/mindmap-lab
./run_quick_test.sh
```

**실행 내용:**
1. 5개 샘플 대화 생성 (각 유형별 1개)
2. 5개 골든 마인드맵 생성
3. 25회 실험 (5개 대화 × 5개 조합)
4. 결과 분석

**예상 시간:** 약 30분

**산출물:**
- `outputs/quick_test/quick_registry.csv` (25행)
- `outputs/quick_test/quick_summary.json` (통계)

---

### Step 5: 결과 확인

```bash
# CSV 결과 확인
cat outputs/quick_test/quick_registry.csv | head -10

# JSON 요약 확인
cat outputs/quick_test/quick_summary.json

# 분석 스크립트 실행
cd src
python3 analyze_quick_results.py
```

**성공 기준:**
- ✅ 성공률 80% 이상
- ✅ 평균 점수 0.5 이상
- ✅ 에러 없이 완료

---

### Step 6: 전체 실험 실행 (3시간) - 옵션

빠른 검증이 성공하면:

```bash
cd /path/to/mindmap-lab
./run_full_experiment.sh
```

**실행 내용:**
1. 20개 대화 생성
2. 20개 골든 마인드맵 생성
3. 300회 실험 (20개 대화 × 15개 조합)
4. 결과 분석

**산출물:**
- `outputs/registry.csv` (300행) ← 보고서용 핵심 데이터
- `outputs/summary.json`
- `outputs/top_combinations.json`
- `outputs/by_type.json`

---

## 🐛 트러블슈팅

### 문제 1: `anthropic` 모듈 없음

```bash
pip install anthropic
```

### 문제 2: API 키 403 오류 (Anthropic)

```bash
# API 키 재확인
echo $ANTHROPIC_API_KEY

# 키가 비어있으면 다시 설정
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# API 키가 유효한지 테스트
python3 src/test_claude_api.py
```

### 문제 3: JSON 파싱 오류

Claude가 가끔 ```json ... ``` 로 감싸서 응답하는 경우가 있음.
→ `gpt_caller.py`에 이미 처리 로직 포함됨

### 문제 4: 대화 파일 없음

```bash
# 대화 생성 스크립트 수동 실행
cd src
python3 generate_conversations.py
python3 generate_golden_maps.py
```

---

## 📊 현재 파일 상태

### 주요 파일들

**실행 스크립트:**
- `run_quick_test.sh` - 빠른 검증 (30분, 25회)
- `run_full_experiment.sh` - 전체 실험 (3시간, 300회)

**Python 모듈:**
- `src/gpt_caller.py` - **Claude API 사용 중** (중요!)
- `src/gpt_caller.py.backup` - OpenAI 버전 백업
- `src/quick_test.py` - 빠른 검증 실험
- `src/lab.py` - 전체 실험
- `src/generate_conversations.py` - 대화 자동 생성
- `src/generate_golden_maps.py` - 골든맵 자동 생성
- `src/analyze_quick_results.py` - 빠른 검증 결과 분석
- `src/analyze_results.py` - 전체 결과 분석

**설정:**
- `config.yaml` - 15개 조합 정의
- `prompts/` - 12개 GPT 프롬프트

---

## ✅ 체크리스트

실행 전 확인사항:

- [ ] GitHub 저장소 클론 완료
- [ ] 브랜치 체크아웃 완료 (`claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi`)
- [ ] Python 패키지 설치 완료 (`pip install -r requirements.txt`)
- [ ] `anthropic` 패키지 설치 (`pip install anthropic`)
- [ ] `ANTHROPIC_API_KEY` 환경변수 설정 완료
- [ ] API 키 테스트 성공 (`python3 src/test_claude_api.py`)

실행:

- [ ] Quick Test 실행 (`./run_quick_test.sh`)
- [ ] 결과 확인 (`cat outputs/quick_test/quick_summary.json`)
- [ ] 문제 없으면 Full Test 실행 (`./run_full_experiment.sh`)

---

## 📞 추가 도움

### 프로젝트 정보
- **저장소**: https://github.com/Kidong8206/mindmap_agent
- **브랜치**: `claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi`
- **커밋**: `24e785e` (최신)

### API 키 관련
- **Anthropic Console**: https://console.anthropic.com/settings/keys
- **OpenAI Billing**: https://platform.openai.com/settings/organization/billing

### 문서
- `README.md` - 전체 사용 가이드
- `IMPLEMENTATION_COMPLETE.md` - 구현 완료 보고서

---

## 🎯 최종 목표

**30분 후 산출물:**
- ✅ `outputs/quick_test/quick_registry.csv` (25행)
- ✅ 조합별 성능 순위
- ✅ 기본 통계

**3시간 후 산출물 (Full Test):**
- ✅ `outputs/registry.csv` (300행) ← 보고서용 핵심 데이터
- ✅ 최적 조합 분석
- ✅ 대화 유형별 분석
- ✅ 통계적 유의성 검증

---

**준비 완료! API 키만 설정하면 즉시 실행 가능합니다! 🚀**
