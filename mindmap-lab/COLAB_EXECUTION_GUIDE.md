# 🚀 Colab 실험 실행 가이드

이 문서는 Claude API와 GPT-4 API를 사용한 마인드맵 생성 실험을 Google Colab에서 실행하는 방법을 안내합니다.

---

## 📋 실험 개요

| 항목 | Claude 실험 | GPT-4 실험 |
|------|-------------|------------|
| **실험 수** | 300회 (20 대화 × 15 조합) | 300회 (20 대화 × 15 조합) |
| **API** | Anthropic Claude Sonnet 4.5 | OpenAI GPT-4 Turbo |
| **예상 시간** | 3-5시간 | 2-4시간 |
| **예상 비용** | $5-8 | $15-25 |
| **출력 파일** | `experiments.csv`<br>`experiment_metadata.json` | `experiments_gpt.csv`<br>`experiment_metadata_gpt.json` |

---

## 1️⃣ Claude 실험 실행하기

### Step 1: Colab 노트북 열기

**방법 A: GitHub에서 직접 열기**

1. 아래 링크로 이동:
   ```
   https://github.com/Kidong8206/mindmap_agent/blob/claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi/mindmap-lab/Mindmap_Experiment_Colab.ipynb
   ```

2. 노트북 미리보기 상단에서 "Open in Colab" 버튼 클릭

**방법 B: Colab에서 GitHub 가져오기**

1. https://colab.research.google.com/ 접속
2. `파일` → `노트 열기` → `GitHub` 탭 선택
3. Repository 입력: `Kidong8206/mindmap_agent`
4. Branch 선택: `claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi`
5. `Mindmap_Experiment_Colab.ipynb` 선택

### Step 2: API 키 준비

1. Anthropic Console에 접속: https://console.anthropic.com/settings/keys
2. 로그인 후 `+ Create Key` 클릭
3. API 키 복사 (sk-ant-로 시작)
4. **중요**: API 키는 한 번만 표시되므로 안전한 곳에 보관

**비용 정보**:
- 신규 계정: $5 무료 크레딧 제공
- 추가 결제: https://console.anthropic.com/settings/billing
- 이 실험 예상 비용: $5-8

### Step 3: 노트북 실행

**실행 순서** (셀을 위에서 아래로 순차적으로 실행):

1. **Cell 1-2**: 패키지 설치
   ```
   ▶ 실행 → 완료될 때까지 대기 (약 30초)
   ```

2. **Cell 3**: 라이브러리 import
   ```
   ▶ 실행 → "✅ 라이브러리 import 완료" 확인
   ```

3. **Cell 5**: API 키 입력
   ```
   ▶ 실행 → 비밀번호 입력창에 API 키 붙여넣기
   → "✅ API 연결 성공!" 확인
   ```

   **⚠️ 주의**: "❌ API 연결 실패" 나올 경우:
   - API 키 형식 확인 (sk-ant-로 시작)
   - 계정에 크레딧 잔액 확인
   - 인터넷 연결 확인

4. **Cell 7**: 실험 설정
   ```
   ▶ 실행 → "✅ 실험 설정 완료" 확인
   → "총 실험: 300회" 표시
   ```

5. **Cell 9**: 프롬프트 파일 로드
   ```
   ▶ 실행 → GitHub에서 자동으로 clone
   → "✅ 프롬프트 파일 로드 완료" 확인
   → "파일 수: XX개" 표시
   ```

6. **Cell 11**: 함수 정의
   ```
   ▶ 실행 → "✅ 실험 함수 정의 완료" 확인
   ```

7. **Cell 13**: 🚀 **실험 실행** (가장 중요!)
   ```
   ▶ 실행 → 진행률 바 표시
   → 예상 시간: 3-5시간
   ```

   **실행 중 화면 예시**:
   ```
   🚀 실험 시작: 2025-11-08 14:30:00
   총 300회 실험 예정

   Experiments: 45/300 [15%] [00:42<03:45, 1.23it/s]
   ```

   **⚠️ 중요 사항**:
   - 노트북을 닫아도 실험은 계속 실행됩니다
   - 50개마다 중간 저장됨 (`experiments_progress.csv`)
   - 실패 시 재실행하면 처음부터 다시 시작
   - **Colab 세션 유지**: 12시간 제한 (Pro는 24시간)

8. **Cell 15**: 결과 저장
   ```
   ▶ 실행 → CSV 및 JSON 파일 생성
   → "✅ 결과 파일 저장 완료" 확인
   ```

9. **Cell 17**: 파일 다운로드
   ```
   ▶ 실행 → 브라우저 다운로드 시작
   → experiments.csv 다운로드
   → experiment_metadata.json 다운로드
   ```

### Step 4: 결과 확인

다운로드된 파일:
- `experiments.csv`: 300개 실험 결과 (성공/실패, 점수, 실행시간 등)
- `experiment_metadata.json`: 실험 메타데이터 (시작/종료 시간, 성공률 등)

**성공 확인**:
```
✅ 실험 완료!
   시작: 2025-11-08 14:30:00
   종료: 2025-11-08 18:15:00
   소요 시간: 3.75시간
   성공: 290
   실패: 10
```

**예상 성공률**: 95% 이상 (285개 이상 성공)

---

## 2️⃣ GPT-4 실험 실행하기

### Step 1: Colab 노트북 열기

**방법 A: GitHub에서 직접 열기**

1. 아래 링크로 이동:
   ```
   https://github.com/Kidong8206/mindmap_agent/blob/claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi/mindmap-lab/Mindmap_Experiment_GPT_Colab.ipynb
   ```

2. 노트북 미리보기 상단에서 "Open in Colab" 버튼 클릭

**방법 B: Colab에서 GitHub 가져오기**

1. https://colab.research.google.com/ 접속
2. `파일` → `노트 열기` → `GitHub` 탭 선택
3. Repository 입력: `Kidong8206/mindmap_agent`
4. Branch 선택: `claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi`
5. `Mindmap_Experiment_GPT_Colab.ipynb` 선택

### Step 2: API 키 준비

1. OpenAI Platform에 접속: https://platform.openai.com/api-keys
2. 로그인 후 `+ Create new secret key` 클릭
3. API 키 복사 (sk-로 시작)
4. **중요**: API 키는 한 번만 표시되므로 안전한 곳에 보관

**비용 정보**:
- 신규 계정: 무료 크레딧 없음 (결제 정보 등록 필수)
- 결제 설정: https://platform.openai.com/account/billing
- 이 실험 예상 비용: $15-25
- **비용 제한 설정 권장**: Settings → Limits에서 월 최대 사용 금액 설정

### Step 3: 노트북 실행

**실행 순서** (Claude와 동일, Cell 번호만 참고):

1. **Cell 1-2**: 패키지 설치 (openai 패키지)
2. **Cell 3**: 라이브러리 import
3. **Cell 5**: API 키 입력
   - "✅ API 연결 성공!" 확인
   - "모델: gpt-4-turbo-..." 표시
4. **Cell 7**: 실험 설정 (Claude와 동일한 300개 실험)
5. **Cell 9**: 프롬프트 파일 로드 (Claude와 동일한 파일 사용)
6. **Cell 11**: 함수 정의 (`call_gpt` 함수 사용)
7. **Cell 13**: 🚀 **실험 실행**
   - 예상 시간: 2-4시간 (Claude보다 빠름)
   - 진행률: `GPT Experiments: XX/300`
8. **Cell 15**: 결과 저장
9. **Cell 17**: 파일 다운로드
   - `experiments_gpt.csv`
   - `experiment_metadata_gpt.json`

### Step 4: 결과 확인

다운로드된 파일:
- `experiments_gpt.csv`: 300개 실험 결과
- `experiment_metadata_gpt.json`: 실험 메타데이터

**성공 확인**:
```
✅ 실험 완료!
   시작: 2025-11-08 19:00:00
   종료: 2025-11-08 22:30:00
   소요 시간: 3.50시간
   성공: 295
   실패: 5
```

---

## 3️⃣ 실험 후 비교 분석

두 실험이 모두 완료되면:

### Step 1: 결과 파일 정리

로컬 컴퓨터에서:

```bash
cd /path/to/mindmap_agent/mindmap-lab

# 다운로드한 파일을 적절한 폴더로 이동
mkdir -p results/claude results/gpt

mv ~/Downloads/experiments.csv results/claude/
mv ~/Downloads/experiment_metadata.json results/claude/

mv ~/Downloads/experiments_gpt.csv results/gpt/
mv ~/Downloads/experiment_metadata_gpt.json results/gpt/
```

### Step 2: 비교 분석 실행

```bash
# analyze_comparison.py 실행
python3 analyze_comparison.py

# 또는 경로 지정
python3 analyze_comparison.py \
  --claude results/claude/experiments.csv \
  --gpt results/gpt/experiments_gpt.csv
```

### Step 3: 생성된 파일 확인

분석 완료 후 생성되는 파일:

```
outputs/comparison/
├── comparison_summary.json       # 요약 통계
├── statistical_tests.json        # 통계 검정 결과
├── comparison_report.md          # 📊 비교 보고서 (마크다운)
├── score_distribution.png        # 점수 분포 시각화
├── combination_comparison.png    # 조합별 성능 비교
└── conversation_type_comparison.png  # 대화 유형별 성능
```

### Step 4: 보고서 확인

```bash
# 마크다운 보고서 읽기
cat outputs/comparison/comparison_report.md

# 또는 VS Code에서 미리보기
code outputs/comparison/comparison_report.md
```

---

## 📌 자주 묻는 질문 (FAQ)

### Q1: 실험 중간에 Colab 세션이 끊어졌어요!

**A**: 진행 상황은 50개마다 자동 저장됩니다.
- 저장 파일: `experiments_progress.csv` (Claude) 또는 `experiments_gpt_progress.csv` (GPT)
- 하지만 **노트북을 다시 실행하면 처음부터** 시작됩니다
- **예방책**: Colab Pro 사용 (24시간 세션) 또는 실험 시작 전에 브라우저 설정 확인

### Q2: API 비용이 예상보다 많이 나올 수 있나요?

**A**: 예상 비용은 보수적으로 계산되었습니다.
- Claude: 실제 $5-8 (최대 $10)
- GPT-4: 실제 $15-25 (최대 $30)
- **OpenAI는 비용 제한 설정을 반드시 하세요!**

### Q3: 두 실험을 동시에 실행해도 되나요?

**A**: 가능합니다! 두 개의 Colab 탭을 열어서 동시 실행 가능합니다.
- 각 탭은 독립적인 런타임 사용
- 단, 무료 Colab은 동시 실행 제한이 있을 수 있음
- Colab Pro 권장

### Q4: 실패율이 너무 높아요!

**A**: 예상 실패율은 5% 미만입니다.

**Claude 실험**:
- 실패율 >10%: API 키 크레딧 확인
- 실패 메시지 "parse_error": 이미 수정됨 (최신 버전 사용 확인)
- 실패 메시지 "rate_limit": API 요청 제한 (자동 재시도 포함)

**GPT-4 실험**:
- 실패율 >10%: API 키 결제 정보 확인
- 실패 메시지 "insufficient_quota": 크레딧 부족

### Q5: 실험 시간을 단축할 수 있나요?

**A**: 현재 설정이 최적화되어 있습니다.
- Temperature=0.0 (재현성 보장)
- Retry 로직 포함 (안정성)
- 시간 단축하려면 실험 수를 줄여야 함 (비권장)

### Q6: 프롬프트 파일을 수정하고 싶어요!

**A**: 가능하지만 권장하지 않습니다.
- 프롬프트 변경 시 Claude/GPT 비교가 불공정해짐
- 수정하려면: GitHub에서 `mindmap-lab/prompts/` 폴더의 .txt 파일 수정

---

## ⚠️ 주의사항

### 실험 전 체크리스트

- [ ] API 키 준비 완료 (Claude 또는 GPT)
- [ ] API 계정 크레딧/결제 정보 확인
- [ ] Colab 브라우저 탭이 닫히지 않도록 설정
- [ ] 인터넷 연결 안정성 확인
- [ ] 예상 비용 확인 (Claude $5-8, GPT $15-25)

### 실험 중 주의사항

- 🚫 노트북 탭을 닫지 마세요 (Colab 세션 유지)
- 🚫 셀을 중복 실행하지 마세요 (중복 실험 방지)
- 🚫 실험 중 Cell 13을 다시 실행하지 마세요
- ✅ 진행률 바를 주기적으로 확인하세요
- ✅ 50개마다 중간 저장 메시지 확인

### 실험 후 주의사항

- 반드시 두 파일 모두 다운로드: CSV + JSON
- 파일명 변경하지 말 것 (분석 스크립트가 파일명으로 인식)
- 원본 파일 백업 권장

---

## 🎯 다음 단계

1. ✅ Claude 실험 완료 → `experiments.csv` 다운로드
2. ✅ GPT-4 실험 완료 → `experiments_gpt.csv` 다운로드
3. 🔄 `python3 analyze_comparison.py` 실행
4. 📊 `comparison_report.md` 확인
5. 📝 Chapter 5에 결과 작성

---

## 💡 팁

### 비용 절약

- Claude 실험만 먼저 실행해서 결과 확인 ($5-8)
- 만족스러우면 GPT-4 실험 진행 ($15-25)

### 시간 절약

- Colab Pro 사용 (더 빠른 GPU, 긴 세션)
- 두 실험 동시 실행 (각 3-5시간 → 총 3-5시간)

### 결과 검증

- `experiment_metadata.json`에서 성공률 먼저 확인
- 성공률 <90%면 원인 파악 후 재실행 고려

---

## 📞 문제 해결

문제가 발생하면:

1. **먼저 확인**: 위 FAQ 섹션
2. **로그 확인**: Colab 셀 출력 메시지 읽기
3. **파일 확인**: `experiments_progress.csv`로 어디까지 진행됐는지 확인
4. **GitHub Issues**: https://github.com/Kidong8206/mindmap_agent/issues

---

**마지막 업데이트**: 2025-11-08
**작성자**: Claude Code Agent
**버전**: v2.0 (67% 실패율 버그 수정 완료)
