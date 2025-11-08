# 🚀 Google Colab 실험 가이드

## 📋 목차
1. [준비사항](#준비사항)
2. [Colab 노트북 열기](#colab-노트북-열기)
3. [실험 실행](#실험-실행)
4. [결과 다운로드 및 적용](#결과-다운로드-및-적용)
5. [문제 해결](#문제-해결)

---

## 1️⃣ 준비사항

### ✅ 필수 항목
- [ ] Google 계정
- [ ] Anthropic API 키
  - https://console.anthropic.com/settings/keys 에서 발급
  - 신규 계정은 **$5 무료 크레딧** 제공
- [ ] 시간: 3-5시간 (자는 동안 실행 가능)
- [ ] 비용: $5-10 (300회 API 호출)

### 💳 Anthropic API 키 발급 방법

1. https://console.anthropic.com 접속
2. 회원가입 (이메일 인증)
3. Settings → API Keys 메뉴
4. "Create Key" 버튼 클릭
5. 키 이름 입력 (예: "mindmap-experiment")
6. **생성된 키 복사** (다시 볼 수 없음!)

---

## 2️⃣ Colab 노트북 열기

### 방법 1: GitHub에서 직접 열기 ⭐ (추천)

```
1. 브라우저에서 아래 URL 접속:
   https://colab.research.google.com/github/Kidong8206/mindmap_agent/blob/claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi/mindmap-lab/Mindmap_Experiment_Colab.ipynb

2. Google 계정으로 로그인

3. "Copy to Drive" 클릭 (내 드라이브에 복사)
```

### 방법 2: 수동 업로드

```
1. GitHub에서 Mindmap_Experiment_Colab.ipynb 다운로드

2. https://colab.research.google.com 접속

3. File → Upload notebook

4. 다운로드한 .ipynb 파일 선택
```

---

## 3️⃣ 실험 실행

### Step 1: 런타임 설정

```
1. Colab 노트북 상단 메뉴
   Runtime → Change runtime type

2. Hardware accelerator: None (CPU만 사용)

3. Save 클릭
```

### Step 2: 셀 실행 (순서대로)

#### 📦 Cell 1-2: 환경 설정
```python
# 자동으로 패키지 설치
!pip install anthropic pandas numpy scipy tqdm -q
```
**예상 시간**: 30초

#### 🔑 Cell 3: API 키 입력
```python
# 프롬프트가 나타나면 Anthropic API 키 입력
api_key = getpass('Anthropic API Key: ')
```
**중요**: 키는 화면에 표시되지 않습니다 (안전)

#### ⚙️ Cell 4-5: 실험 설정
```python
# 15개 조합, 20개 대화 설정
TOTAL_EXPERIMENTS = 300
```
**예상 시간**: 5초

#### 🚀 Cell 6: 실험 실행 (메인)
```python
# 300회 실험 자동 실행
# 진행률 표시 포함
```
**예상 시간**: 3-5시간
**비용**: $5-10

**⚠️ 주의사항:**
- Colab 탭을 닫아도 실행은 계속됩니다
- 하지만 12시간 후 자동 종료됩니다
- 50개마다 중간 저장됩니다 (`experiments_progress.csv`)

#### 💾 Cell 7-8: 결과 저장 및 다운로드
```python
# experiments.csv 다운로드
# experiment_metadata.json 다운로드
```
**예상 시간**: 10초

---

## 4️⃣ 결과 다운로드 및 적용

### 다운로드된 파일:
- `experiments.csv` (약 50KB)
- `experiment_metadata.json` (약 350B)

### 로컬 적용 방법:

```bash
# Step 1: 다운로드한 파일을 results/ 폴더로 복사
cp ~/Downloads/experiments.csv mindmap-lab/results/
cp ~/Downloads/experiment_metadata.json mindmap-lab/results/

# Step 2: 분석 스크립트 실행
cd mindmap-lab
python analyze_results.py

# Step 3: 생성된 모든 파일을 outputs/mock_data/로 복사
cp results/*.json outputs/mock_data/
cp results/experiments.csv outputs/mock_data/

# Step 4: Git commit & push
git add -A
git commit -m "feat: replace mock data with real experiment results

Completed 300 real experiments using Anthropic Claude API
Success rate: XX%, Mean score: XX.XX"

git push origin claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi
```

---

## 5️⃣ 문제 해결

### ❌ API 키 오류
```
Error: Invalid API key
```
**해결:**
- API 키를 다시 확인
- https://console.anthropic.com/settings/keys 에서 새 키 발급

### ❌ 크레딧 부족
```
Error: Your credit balance is too low
```
**해결:**
- Anthropic Console에서 결제 수단 추가
- 또는 새 계정 생성 ($5 무료 크레딧)

### ❌ Rate Limit 에러
```
Error: Rate limit exceeded
```
**해결:**
- 노트북이 자동으로 5초 대기 후 재시도
- 계속 발생 시 Tier 1 플랜 업그레이드

### ❌ Timeout 에러
```
Error: Request timeout
```
**해결:**
- 자동으로 재시도 (최대 3회)
- 실패한 실험은 `status: failed`로 기록됨
- 정상적인 현상 (2-3% 예상)

### ❌ Colab 세션 종료
```
Runtime disconnected
```
**해결:**
- `experiments_progress.csv` 파일 다운로드
- 노트북 재실행
- 이전 진행 상황부터 재개 가능 (코드 수정 필요)

---

## 📊 실행 중 모니터링

### 진행 상황 확인
```python
# Cell에서 실행 중인 경우
# 진행률 바가 표시됨:
Experiments: 45%|████▌     | 135/300 [1:23:45<1:42:15, 37.23s/it]
```

### 중간 결과 확인
```python
# 50개마다 저장되는 파일 확인
!head -20 experiments_progress.csv
```

### 예상 완료 시간
```
평균 실험 시간: 8-12초/회
총 300회 = 40-60분 예상

실제로는:
- API 응답 시간 변동
- Rate limit 대기
- 재시도 포함
→ 3-5시간 소요
```

---

## 🎯 성공 체크리스트

실험이 성공적으로 완료되었는지 확인:

- [ ] `experiments.csv` 파일 다운로드됨 (약 50KB)
- [ ] `experiment_metadata.json` 다운로드됨
- [ ] experiments.csv 열어보면 300줄 (또는 295-300줄)
- [ ] 성공률 90% 이상 (270개 이상 성공)
- [ ] 평균 점수가 70-90 범위
- [ ] `analyze_results.py` 실행 시 11개 JSON 파일 생성
- [ ] Mock 데이터와 동일한 파일 구조

---

## 💡 팁

### 🌙 밤에 실행하기
```
1. 저녁에 노트북 실행
2. 자러 가기 전에 진행 상황 확인
3. 아침에 일어나서 결과 다운로드
```

### 🔍 부분 실험 먼저 해보기
```python
# Cell 6을 수정:
# 전체 300회 대신 30회만 테스트
conversations = conversations[:3]  # 3개 대화만
combinations = combinations[:10]   # 10개 조합만
# → 30회 실험 (약 5-10분)
```

### 💰 비용 절약
```
- 테스트는 30회로 ($0.5)
- 문제 없으면 전체 300회 실행
- 신규 계정 $5 크레딧으로 충분
```

---

## 📞 도움이 필요하신가요?

- GitHub Issues: https://github.com/Kidong8206/mindmap_agent/issues
- Anthropic Support: https://support.anthropic.com

---

**🎉 실험 성공을 기원합니다!**
