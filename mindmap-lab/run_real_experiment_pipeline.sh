#!/bin/bash

################################################################################
# 실제 실험 결과 → 보고서 자료 자동 생성 스크립트
#
# 사용법:
#   1. Colab에서 experiments.csv, experiment_metadata.json 다운로드
#   2. Downloads 폴더에 파일이 있는지 확인
#   3. 이 스크립트 실행: bash run_real_experiment_pipeline.sh
#
# 생성 일시: 2025-11-08
################################################################################

set -e  # 에러 발생 시 즉시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 디렉토리
PROJECT_DIR="/home/user/mindmap_agent/mindmap-lab"
DATA_DIR="$PROJECT_DIR/outputs/mock_data"
DOWNLOAD_DIR="$HOME/Downloads"

echo -e "${BLUE}"
echo "======================================================================"
echo "📊 실제 실험 결과 → 보고서 자료 생성 파이프라인"
echo "======================================================================"
echo -e "${NC}"

################################################################################
# 1단계: 파일 존재 확인
################################################################################
echo -e "${YELLOW}[1/5] 다운로드 파일 확인 중...${NC}"

if [ ! -f "$DOWNLOAD_DIR/experiments.csv" ]; then
    echo -e "${RED}❌ 에러: $DOWNLOAD_DIR/experiments.csv 파일이 없습니다!${NC}"
    echo ""
    echo "해결 방법:"
    echo "  1. Colab에서 Cell 10 실행"
    echo "  2. experiments.csv 다운로드"
    echo "  3. 다운로드 폴더 확인: ls ~/Downloads/experiments.csv"
    exit 1
fi

if [ ! -f "$DOWNLOAD_DIR/experiment_metadata.json" ]; then
    echo -e "${RED}❌ 에러: $DOWNLOAD_DIR/experiment_metadata.json 파일이 없습니다!${NC}"
    echo ""
    echo "해결 방법:"
    echo "  1. Colab에서 Cell 10 실행"
    echo "  2. experiment_metadata.json 다운로드"
    echo "  3. 다운로드 폴더 확인: ls ~/Downloads/experiment_metadata.json"
    exit 1
fi

echo -e "${GREEN}✓ 다운로드 파일 확인 완료${NC}"
echo "  - experiments.csv: $(ls -lh $DOWNLOAD_DIR/experiments.csv | awk '{print $5}')"
echo "  - experiment_metadata.json: $(ls -lh $DOWNLOAD_DIR/experiment_metadata.json | awk '{print $5}')"

################################################################################
# 2단계: 기존 mock 데이터 백업 및 실제 데이터로 교체
################################################################################
echo ""
echo -e "${YELLOW}[2/5] 데이터 교체 중...${NC}"

# 백업 디렉토리 생성
BACKUP_DIR="$PROJECT_DIR/outputs/backup_mock_data_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 기존 데이터 백업
if [ -d "$DATA_DIR" ]; then
    echo "  기존 mock 데이터 백업: $BACKUP_DIR"
    cp -r "$DATA_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true
fi

# 실제 데이터 복사
echo "  실제 실험 데이터 복사 중..."
cp "$DOWNLOAD_DIR/experiments.csv" "$DATA_DIR/"
cp "$DOWNLOAD_DIR/experiment_metadata.json" "$DATA_DIR/"

# 파일 검증
TOTAL_LINES=$(wc -l < "$DATA_DIR/experiments.csv")
EXPECTED_LINES=301  # 헤더 1줄 + 데이터 300줄

if [ "$TOTAL_LINES" -ne "$EXPECTED_LINES" ]; then
    echo -e "${YELLOW}⚠️  경고: experiments.csv의 줄 수가 예상과 다릅니다.${NC}"
    echo "  예상: $EXPECTED_LINES줄 (헤더 1 + 데이터 300)"
    echo "  실제: $TOTAL_LINES줄"
    echo ""
    read -p "계속 진행하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ 사용자가 중단했습니다.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ 실험 데이터 검증 완료 ($TOTAL_LINES줄)${NC}"
fi

################################################################################
# 3단계: 기존 분석 파일 제거
################################################################################
echo ""
echo -e "${YELLOW}[3/5] 기존 분석 파일 제거 중...${NC}"

cd "$PROJECT_DIR"

# 기존 분석 파일 삭제 (rubric_weights.json, pilot_vs_midscale_analysis.json,
# conversation_type_anova.json은 유지)
rm -f "$DATA_DIR/combination_performance.json"
rm -f "$DATA_DIR/stage_performance.json"
rm -f "$DATA_DIR/conversation_type_analysis.json"
rm -f "$DATA_DIR/statistical_tests.json"
rm -f "$DATA_DIR/item_scores.json"
rm -f "$DATA_DIR/item_correlations.json"
rm -f "$DATA_DIR/execution_time_analysis.json"
rm -f "$DATA_DIR/failure_analysis.json"
rm -f "$DATA_DIR/summary_statistics.json"
rm -f "$DATA_DIR/visualization_data.json"

echo -e "${GREEN}✓ 기존 분석 파일 제거 완료${NC}"

################################################################################
# 4단계: 실제 데이터 분석
################################################################################
echo ""
echo -e "${YELLOW}[4/5] 실제 데이터 분석 중...${NC}"
echo ""

python3 analyze_results.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 에러: analyze_results.py 실행 실패!${NC}"
    echo ""
    echo "문제 해결:"
    echo "  1. 에러 메시지 확인"
    echo "  2. CSV 형식 검증: head outputs/mock_data/experiments.csv"
    echo "  3. 필수 컬럼 확인: experiment_id, combination_id, status, total_score"
    exit 1
fi

# 생성된 JSON 파일 개수 확인
JSON_COUNT=$(ls -1 "$DATA_DIR"/*.json 2>/dev/null | wc -l)
EXPECTED_JSON=13

if [ "$JSON_COUNT" -lt "$EXPECTED_JSON" ]; then
    echo -e "${YELLOW}⚠️  경고: 생성된 JSON 파일이 예상보다 적습니다.${NC}"
    echo "  예상: $EXPECTED_JSON개"
    echo "  실제: $JSON_COUNT개"
else
    echo -e "${GREEN}✓ 분석 파일 생성 완료 ($JSON_COUNT개 JSON 파일)${NC}"
fi

################################################################################
# 5단계: 보고서 자료 생성
################################################################################
echo ""
echo -e "${YELLOW}[5/5] 보고서 자료 생성 중...${NC}"
echo ""

python3 generate_report_assets.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 에러: generate_report_assets.py 실행 실패!${NC}"
    echo ""
    echo "문제 해결:"
    echo "  1. 에러 메시지 확인"
    echo "  2. 필수 JSON 파일 확인: ls outputs/mock_data/*.json"
    exit 1
fi

# 생성된 자료 검증
TABLE_COUNT=$(ls -1 report_assets/tables/* 2>/dev/null | wc -l)
FIGURE_COUNT=$(ls -1 report_assets/figures/* 2>/dev/null | wc -l)

echo -e "${GREEN}✓ 보고서 자료 생성 완료${NC}"
echo "  - 표 파일: $TABLE_COUNT개"
echo "  - 그림 파일: $FIGURE_COUNT개"

################################################################################
# 완료 및 다음 단계 안내
################################################################################
echo ""
echo -e "${BLUE}"
echo "======================================================================"
echo "✅ 파이프라인 실행 완료!"
echo "======================================================================"
echo -e "${NC}"

echo ""
echo -e "${GREEN}📊 생성된 자료:${NC}"
echo "  위치: $PROJECT_DIR/report_assets/"
echo ""
echo "  📁 tables/  - $TABLE_COUNT개 파일 (Markdown, LaTeX, Excel)"
echo "  📁 figures/ - $FIGURE_COUNT개 파일 (PNG, PDF)"
echo "  📄 README.md - 요약 통계 및 사용법"
echo ""

echo -e "${GREEN}📈 주요 결과 요약:${NC}"
cat report_assets/README.md | grep -A 10 "## 전체 통계"
echo ""

echo -e "${YELLOW}📝 다음 단계:${NC}"
echo "  1. 결과 확인:"
echo "     cat report_assets/README.md"
echo ""
echo "  2. 샘플 표 확인:"
echo "     cat report_assets/tables/table_5_1_weights.md"
echo ""
echo "  3. 그림 확인:"
echo "     open report_assets/figures/figure_5_1_weight_distribution.png"
echo ""
echo "  4. Git 커밋:"
echo "     cd /home/user/mindmap_agent"
echo "     git add -A"
echo "     git commit -m \"feat: generate report assets from real experiments\""
echo "     git push -u origin claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi"
echo ""

echo -e "${GREEN}✅ 준비 완료! 이제 보고서에 복사-붙여넣기 하세요!${NC}"
echo ""
