#!/bin/bash
set -e

echo "============================================================"
echo "  빠른 검증 실험 (5개 대화 × 5개 조합 = 25회)"
echo "============================================================"

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠ 오류: OPENAI_API_KEY 환경변수가 설정되지 않았습니다."
    echo "사용법: export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

echo ""
echo "실험 규모: 5개 대화 × 5개 조합 = 25회"
echo "예상 시간: 약 30분"
echo ""

cd src

echo "============================================================"
echo "[1/4] 샘플 대화 생성 중 (5개)..."
echo "============================================================"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from generate_conversations import ConversationGenerator, SCENARIOS

# 5개만 생성
quick_scenarios = [SCENARIOS[0], SCENARIOS[3], SCENARIOS[7], SCENARIOS[10], SCENARIOS[15]]
gen = ConversationGenerator()
for scenario in quick_scenarios:
    gen.generate_one(scenario)
print(f"\n✓ {len(quick_scenarios)}개 대화 생성 완료")
PYEOF

echo ""
echo "============================================================"
echo "[2/4] 골든 맵 생성 중 (5개)..."
echo "============================================================"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from generate_golden_maps import GoldenMapGenerator

quick_ids = ["conv_001", "conv_004", "conv_008", "conv_011", "conv_016"]
gen = GoldenMapGenerator()
for conv_id in quick_ids:
    gen.generate_one(conv_id)
print(f"\n✓ {len(quick_ids)}개 골든 맵 생성 완료")
PYEOF

echo ""
echo "============================================================"
echo "[3/4] 축소 실험 실행 중 (25회, 약 30분)..."
echo "============================================================"
python3 quick_test.py

echo ""
echo "============================================================"
echo "[4/4] 결과 분석 중..."
echo "============================================================"
python3 analyze_quick_results.py

echo ""
echo "============================================================"
echo "  ✅ 빠른 검증 완료!"
echo "============================================================"
echo ""
echo "결과 파일:"
echo "  - outputs/quick_test/quick_registry.csv (25개 실험 결과)"
echo "  - outputs/quick_test/quick_summary.json (통계 요약)"
echo ""
echo "다음 단계:"
echo "  결과가 정상이면 전체 실험 실행:"
echo "  ./run_full_experiment.sh"
echo ""
