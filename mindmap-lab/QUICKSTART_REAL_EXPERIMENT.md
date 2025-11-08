# 🚀 빠른 시작: 실제 실험 결과 → 보고서 자료 생성

## ⏱️ 소요 시간: 5분

---

## 📋 준비물

1. ✅ Colab 실험 완료 (300회)
2. ✅ `experiments.csv` 다운로드 완료
3. ✅ `experiment_metadata.json` 다운로드 완료
4. ✅ 두 파일이 `~/Downloads/` 폴더에 있음

---

## 🎯 원클릭 실행

### 방법 1: 자동화 스크립트 (추천)

```bash
cd /home/user/mindmap_agent/mindmap-lab
bash run_real_experiment_pipeline.sh
```

이게 끝입니다! 스크립트가 자동으로:
- ✅ 다운로드 파일 확인
- ✅ 기존 mock 데이터 백업
- ✅ 실제 데이터로 교체
- ✅ 분석 파일 생성
- ✅ 보고서 표/그림 생성

완료 후 `report_assets/` 폴더에 모든 자료가 준비됩니다!

---

### 방법 2: 수동 단계별 실행

Colab에서 다운로드 후:

```bash
cd /home/user/mindmap_agent/mindmap-lab

# 1. 데이터 교체
cp ~/Downloads/experiments.csv outputs/mock_data/
cp ~/Downloads/experiment_metadata.json outputs/mock_data/

# 2. 분석 + 보고서 자료 생성 (한 번에)
python3 analyze_results.py && python3 generate_report_assets.py

# 3. 결과 확인
cat report_assets/README.md
```

---

## 📊 생성 결과 확인

### 요약 통계 보기
```bash
cat report_assets/README.md
```

### 샘플 표 보기
```bash
cat report_assets/tables/table_5_1_weights.md
```

### 그림 열기
```bash
# Linux
xdg-open report_assets/figures/figure_5_1_weight_distribution.png

# Mac
open report_assets/figures/figure_5_1_weight_distribution.png
```

---

## 💾 Git 커밋

모든 것이 정상이면:

```bash
cd /home/user/mindmap_agent

git add -A
git commit -m "feat: generate report assets from real experiment results (300 trials)"
git push -u origin claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi
```

---

## 📁 생성되는 파일

```
report_assets/
├── README.md                              # 📄 요약 통계
├── tables/                                # 📊 48개 표 파일
│   ├── table_5_1_weights.md              # Markdown
│   ├── table_5_1_weights.tex             # LaTeX
│   ├── table_5_1_weights.xlsx            # Excel
│   └── ... (45개 더)
└── figures/                               # 📈 14개 그림 파일
    ├── figure_5_1_weight_distribution.png  # 고해상도 PNG
    ├── figure_5_1_weight_distribution.pdf  # 벡터 PDF
    └── ... (12개 더)
```

---

## 🚨 에러 발생 시

### "experiments.csv 파일이 없습니다"
→ Colab Cell 10에서 다운로드 다시 실행

### "줄 수가 예상과 다릅니다"
→ Colab 실험이 300회 완료되었는지 확인

### "analyze_results.py 실행 실패"
→ CSV 형식 확인:
```bash
head outputs/mock_data/experiments.csv
```

### 기타 에러
→ 전체 프로토콜 참고:
```bash
cat PROTOCOL_REAL_EXPERIMENT.md
```

---

## ✅ 완료 체크리스트

- [ ] Colab 실험 300회 완료
- [ ] experiments.csv 다운로드 (~/Downloads/)
- [ ] experiment_metadata.json 다운로드 (~/Downloads/)
- [ ] `bash run_real_experiment_pipeline.sh` 실행
- [ ] report_assets/ 폴더 생성 확인
- [ ] README.md 통계 확인
- [ ] 샘플 표/그림 확인
- [ ] Git 커밋 및 푸시

---

**🎉 완료되면 보고서에 바로 복사-붙여넣기 하세요!**
