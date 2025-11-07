#!/bin/bash
set -e

echo "============================================================"
echo "  마인드맵 생성 조합 실험실 - 전체 자동 실행"
echo "============================================================"

# API 키 확인
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠ 오류: OPENAI_API_KEY 환경변수가 설정되지 않았습니다."
    echo "사용법: export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

echo ""
echo "실험 단계:"
echo "  1. 대화 생성 (20개, 약 10분)"
echo "  2. 골든 맵 생성 (20개, 약 5분)"
echo "  3. 실험 실행 (300회, 약 2-3시간)"
echo "  4. 결과 분석 (약 2분)"
echo ""
echo "총 예상 시간: 약 3시간"
echo ""
read -p "계속하시겠습니까? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "취소되었습니다."
    exit 0
fi

cd src

echo ""
echo "============================================================"
echo "[1/4] 대화 생성 중..."
echo "============================================================"
python3 generate_conversations.py
if [ $? -ne 0 ]; then
    echo "⚠ 대화 생성 실패"
    exit 1
fi

echo ""
echo "============================================================"
echo "[2/4] 골든 마인드맵 생성 중..."
echo "============================================================"
python3 generate_golden_maps.py
if [ $? -ne 0 ]; then
    echo "⚠ 골든 맵 생성 실패"
    exit 1
fi

echo ""
echo "============================================================"
echo "[3/4] 실험 실행 중 (300회)..."
echo "  시간이 오래 걸립니다 (2-3시간)"
echo "  중간에 중단하려면 Ctrl+C"
echo "============================================================"
python3 lab.py
if [ $? -ne 0 ]; then
    echo "⚠ 실험 실패 (일부만 완료되었을 수 있음)"
    # 실패해도 분석은 계속
fi

echo ""
echo "============================================================"
echo "[4/4] 결과 분석 중..."
echo "============================================================"
python3 analyze_results.py

echo ""
echo "============================================================"
echo "  ✅ 전체 실험 완료!"
echo "============================================================"
echo ""
echo "결과 파일:"
echo "  - outputs/registry.csv (300개 실험 결과)"
echo "  - outputs/summary.json (전체 통계)"
echo "  - outputs/top_combinations.json (조합 순위)"
echo "  - outputs/by_type.json (유형별 분석)"
echo ""
echo "확인 방법:"
echo "  cat ../outputs/summary.json"
echo "  cat ../outputs/top_combinations.json | head -20"
echo ""
