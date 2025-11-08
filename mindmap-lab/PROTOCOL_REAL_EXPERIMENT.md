# 실제 실험 결과 → 보고서 자료 생성 프로토콜

## 📋 개요
Colab에서 실제 실험(300회)이 완료되면, 이 프로토콜을 따라 보고서 표와 그림을 자동 생성합니다.

---

## ⏰ 실행 시점
- Colab 실험 완료 후 (예상: 내일 아침)
- "✅ 모든 실험 완료! experiments.csv 다운로드 준비 완료" 메시지 확인 후

---

## 🔄 전체 워크플로우

```
[1단계] Colab 결과 다운로드
   ↓
[2단계] 실제 데이터로 교체
   ↓
[3단계] 분석 파일 생성
   ↓
[4단계] 보고서 자료 생성
   ↓
[5단계] 검증 및 커밋
```

---

## 📝 단계별 실행 가이드

### 1단계: Colab 결과 다운로드

#### 1.1 Colab에서 확인할 사항
```python
# Colab 마지막 셀 실행 결과 확인
✅ 총 실험: 300회
✅ 성공: XXX회
✅ 실패: XXX회
✅ 파일 생성 완료:
   - experiments.csv
   - experiment_metadata.json
```

#### 1.2 다운로드 방법 (Colab Cell 10)
```python
from google.colab import files

# 결과 파일 다운로드
files.download('experiments.csv')
files.download('experiment_metadata.json')
```

#### 1.3 다운로드 위치 확인
- 브라우저 다운로드 폴더: `~/Downloads/experiments.csv`
- 브라우저 다운로드 폴더: `~/Downloads/experiment_metadata.json`

---

### 2단계: 실제 데이터로 교체

#### 2.1 기존 mock 데이터 백업
```bash
cd /home/user/mindmap_agent/mindmap-lab
mkdir -p outputs/backup_mock_data
cp -r outputs/mock_data/* outputs/backup_mock_data/
```

#### 2.2 실제 실험 결과 복사
```bash
# 다운로드한 파일을 프로젝트로 복사
cp ~/Downloads/experiments.csv outputs/mock_data/
cp ~/Downloads/experiment_metadata.json outputs/mock_data/
```

#### 2.3 데이터 검증
```bash
# 실험 개수 확인 (300개여야 함)
wc -l outputs/mock_data/experiments.csv
# 출력: 301 (헤더 1줄 + 데이터 300줄)

# 파일 크기 확인 (최소 50KB 이상)
ls -lh outputs/mock_data/experiments.csv
ls -lh outputs/mock_data/experiment_metadata.json
```

---

### 3단계: 분석 파일 생성

#### 3.1 기존 분석 파일 제거
```bash
cd /home/user/mindmap_agent/mindmap-lab
rm outputs/mock_data/combination_performance.json
rm outputs/mock_data/stage_performance.json
rm outputs/mock_data/conversation_type_analysis.json
rm outputs/mock_data/statistical_tests.json
rm outputs/mock_data/item_scores.json
rm outputs/mock_data/item_correlations.json
rm outputs/mock_data/execution_time_analysis.json
rm outputs/mock_data/failure_analysis.json
rm outputs/mock_data/summary_statistics.json
rm outputs/mock_data/visualization_data.json
```

#### 3.2 실제 데이터 분석 실행
```bash
cd /home/user/mindmap_agent/mindmap-lab
python3 analyze_results.py
```

#### 3.3 예상 출력
```
======================================================================
📊 Analyzing Experiment Results
======================================================================

[Loading Data]
✓ Loaded 300 experiments from experiments.csv
✓ Success: XXX experiments (XX.X%)
✓ Failed: XXX experiments (XX.X%)

[Analyzing Performance]
✓ Combination performance analyzed
✓ Stage performance analyzed
✓ Conversation type analysis complete

[Statistical Tests]
✓ ANOVA: F=XX.XX, p<0.001
✓ Post-hoc tests complete

[Generating Output Files]
✓ combination_performance.json
✓ stage_performance.json
✓ conversation_type_analysis.json
✓ statistical_tests.json
✓ item_scores.json
✓ item_correlations.json
✓ execution_time_analysis.json
✓ failure_analysis.json
✓ summary_statistics.json
✓ visualization_data.json

======================================================================
✅ Analysis Complete!
======================================================================
```

#### 3.4 생성된 파일 검증
```bash
ls -lh outputs/mock_data/*.json | wc -l
# 출력: 13 (분석 파일 10개 + rubric_weights.json + pilot_vs_midscale_analysis.json + conversation_type_anova.json)
```

---

### 4단계: 보고서 자료 생성

#### 4.1 보고서 자료 생성 스크립트 실행
```bash
cd /home/user/mindmap_agent/mindmap-lab
python3 generate_report_assets.py
```

#### 4.2 예상 출력
```
======================================================================
📊 Generating Report Assets
======================================================================

[Loading Data]
✓ All data loaded

[Generating Tables]
  Generating Table 5.1: Rubric Weights...
  Generating Table 5.2: Pilot Top 5...
  Generating Table 5.3: Pilot Bottom 3...
  ...
✓ Generated 16 tables

[Generating Figures]
  Generating Figure 5.1: Weight Distribution...
  Generating Figure 5.2: Combination Performance...
  ...
✓ Generated 7 figures

[Generating Summary Document]
✓ Generated summary document

======================================================================
✅ Report Assets Generation Complete!
======================================================================
```

#### 4.3 생성된 자료 확인
```bash
# 표 파일 확인 (48개: 16 tables × 3 formats)
ls report_assets/tables/ | wc -l
# 출력: 48

# 그림 파일 확인 (14개: 7 figures × 2 formats)
ls report_assets/figures/ | wc -l
# 출력: 14
```

---

### 5단계: 검증 및 커밋

#### 5.1 주요 통계 확인
```bash
cat report_assets/README.md
```

**확인 사항:**
- [ ] 총 실험 수: 300회
- [ ] 성공률: 95% 이상
- [ ] 최고 성능 조합 3개 표시
- [ ] ANOVA p-value < 0.05 (통계적 유의성)

#### 5.2 샘플 표 확인
```bash
cat report_assets/tables/table_5_1_weights.md
```

**확인 사항:**
- [ ] 10개 평가 항목 모두 표시
- [ ] 가중치 합계 = 1.0 (±0.01)
- [ ] 한글 깨짐 없음

#### 5.3 샘플 그림 확인
```bash
# 이미지 뷰어로 열기
open report_assets/figures/figure_5_1_weight_distribution.png
# 또는
xdg-open report_assets/figures/figure_5_1_weight_distribution.png
```

**확인 사항:**
- [ ] 그래프 제목, 축 라벨 정상 표시
- [ ] 데이터 값이 합리적 범위 내
- [ ] 해상도 충분 (300dpi)

#### 5.4 Git 커밋
```bash
cd /home/user/mindmap_agent

# 변경사항 확인
git status

# 전체 추가
git add -A

# 커밋
git commit -m "$(cat <<'EOF'
feat: generate report assets from real experiment results

Generated report assets from 300 real experiments conducted on Colab:
- 16 tables in 3 formats (Markdown, LaTeX, Excel)
- 7 figures in 2 formats (PNG 300dpi, PDF vector)
- Summary document with key statistics

Results:
- Total experiments: 300
- Success rate: XX.X%
- Top combination: XXXXX (score: XX.XX)
- ANOVA p-value: X.XXX (statistically significant)

All assets are ready for direct copy-paste into academic report.
EOF
)"

# 푸시
git push -u origin claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi
```

---

## 🚨 문제 해결

### 문제 1: experiments.csv 파일이 비어있음
**원인**: Colab 실험이 제대로 완료되지 않음
**해결**:
```bash
# Colab에서 Cell 9 다시 실행 (중간 저장본 확인)
ls -lh experiment_results_*.csv
# 가장 최근 파일 다운로드
```

### 문제 2: analyze_results.py 실행 시 KeyError
**원인**: 실험 결과 파일 형식 불일치
**해결**:
```bash
# CSV 헤더 확인
head -1 outputs/mock_data/experiments.csv

# 필수 컬럼 확인:
# experiment_id,combination_id,conversation_type,status,total_score,...
```

### 문제 3: 한글 깨짐 (그림)
**원인**: matplotlib 한글 폰트 미설정
**해결**:
```bash
# 이미 generate_report_assets.py에 설정되어 있음
# 문제 지속 시:
pip install fonttools
```

### 문제 4: 통계 검정 실패
**원인**: 성공한 실험 수가 너무 적음 (< 100개)
**해결**:
```bash
# 성공 실험 수 확인
grep -c "success" outputs/mock_data/experiments.csv

# 100개 미만이면 Colab에서 실험 재실행 필요
```

---

## 📊 예상 결과물

### 생성되는 파일 목록

```
report_assets/
├── README.md                                      # 요약 통계
├── tables/                                        # 48개 파일
│   ├── table_5_1_weights.md
│   ├── table_5_1_weights.tex
│   ├── table_5_1_weights.xlsx
│   ├── table_5_2_pilot_top5.md
│   ├── table_5_2_pilot_top5.tex
│   ├── table_5_2_pilot_top5.xlsx
│   └── ... (42개 더)
└── figures/                                       # 14개 파일
    ├── figure_5_1_weight_distribution.png
    ├── figure_5_1_weight_distribution.pdf
    ├── figure_5_2_combination_boxplot.png
    ├── figure_5_2_combination_boxplot.pdf
    └── ... (10개 더)
```

---

## ⚡ 빠른 실행 스크립트

모든 단계를 자동으로 실행하려면:

```bash
cd /home/user/mindmap_agent/mindmap-lab

# 실제 데이터로 교체 (다운로드 후)
cp ~/Downloads/experiments.csv outputs/mock_data/
cp ~/Downloads/experiment_metadata.json outputs/mock_data/

# 분석 및 보고서 자료 생성
python3 analyze_results.py && python3 generate_report_assets.py

# 결과 확인
cat report_assets/README.md

# Git 커밋 (메시지는 직접 수정)
git add -A
git commit -m "feat: generate report assets from real experiments"
git push -u origin claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi
```

---

## ✅ 체크리스트

실험 결과 나온 후 순서대로 체크:

- [ ] **1단계**: Colab에서 experiments.csv, experiment_metadata.json 다운로드
- [ ] **2단계**: 파일을 outputs/mock_data/로 복사
- [ ] **2단계**: 파일 검증 (300줄, 50KB 이상)
- [ ] **3단계**: analyze_results.py 실행
- [ ] **3단계**: 13개 JSON 파일 생성 확인
- [ ] **4단계**: generate_report_assets.py 실행
- [ ] **4단계**: 48개 표 + 14개 그림 생성 확인
- [ ] **5단계**: README.md 통계 확인
- [ ] **5단계**: 샘플 표 1개 확인 (한글 정상)
- [ ] **5단계**: 샘플 그림 1개 확인 (품질 정상)
- [ ] **5단계**: Git 커밋 및 푸시

---

## 📞 문제 발생 시

1. 에러 메시지 전체 복사
2. 실패한 단계 번호 기록
3. 다음 명령 실행:
   ```bash
   ls -lh outputs/mock_data/
   head -5 outputs/mock_data/experiments.csv
   ```
4. 위 정보와 함께 도움 요청

---

**생성 일시**: 2025-11-08
**목적**: 실제 Colab 실험 결과 → 보고서 자료 자동 생성
**예상 소요 시간**: 5-10분
