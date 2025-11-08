# Claude vs GPT-4 비교 연구 방법론

## 📋 목차

1. [연구 배경](#1-연구-배경)
2. [연구 목적](#2-연구-목적)
3. [비교 설계](#3-비교-설계)
4. [통제 변수](#4-통제-변수)
5. [실험 변수](#5-실험-변수)
6. [데이터 수집](#6-데이터-수집)
7. [분석 방법](#7-분석-방법)
8. [예상 결과](#8-예상-결과)

---

## 1. 연구 배경

### 1.1 문제 정의

대화형 AI를 활용한 마인드맵 자동 생성 시스템 개발 시, **어떤 LLM API를 사용하는 것이 최적인가?**

### 1.2 기존 연구의 한계

- 대부분의 연구는 단일 LLM만 사용
- API 간 성능 비교 연구가 부족
- 특히 **구조화된 출력** (JSON) 생성 능력 비교 부족
- 비용-성능 트레이드오프 분석 부족

### 1.3 연구의 필요성

1. **실용적 필요성**
   - API 선택에 따른 성능 차이 파악
   - 비용 대비 효율성 평가
   - 최적 API 선택 기준 마련

2. **학술적 기여**
   - LLM 간 구조화 출력 능력 비교
   - 마인드맵 생성 품질 비교
   - 실패율 및 에러 패턴 분석

---

## 2. 연구 목적

### 2.1 주요 연구 질문 (Research Questions)

**RQ1**: Claude와 GPT-4는 마인드맵 생성 품질에 유의미한 차이가 있는가?

**RQ2**: 알고리즘 조합에 따라 API 간 성능 차이가 달라지는가?

**RQ3**: 대화 유형에 따라 최적 API가 다른가?

**RQ4**: 실행 시간 및 실패율에서 API 간 차이가 있는가?

**RQ5**: 비용 대비 효율성은 어떤 API가 우수한가?

### 2.2 연구 가설 (Hypotheses)

**H1**: Claude와 GPT-4의 평균 마인드맵 품질 점수는 유의미한 차이가 있다.
- H1-1 (양측): μ_claude ≠ μ_gpt
- H1-2 (단측): μ_claude > μ_gpt (또는 반대)

**H2**: 알고리즘 조합과 API 간 상호작용 효과가 존재한다.
- Combination × API interaction effect 유의

**H3**: 대화 유형에 따라 API별 성능이 다르게 나타난다.
- Conversation Type × API interaction effect 유의

**H4**: Claude와 GPT-4의 실행 시간은 유의미한 차이가 있다.

**H5**: Claude와 GPT-4의 실패율은 유의미한 차이가 있다.

---

## 3. 비교 설계

### 3.1 연구 설계 유형

**Between-Subjects Design (피험자 간 설계)**

- 각 대화-조합 쌍에 대해 Claude 또는 GPT 중 하나만 사용
- 동일한 조건(대화, 조합)을 두 API에 모두 적용
- 총 600회 실험 (Claude 300 + GPT 300)

**장점:**
- ✅ 학습 효과 배제
- ✅ API 간 간섭 없음
- ✅ 독립성 보장

**단점:**
- ❌ 실험 횟수 2배

### 3.2 실험 구조

```
                    ┌─────────────┐
                    │  20 대화    │
                    └──────┬──────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
     ┌──────▼──────┐              ┌──────▼──────┐
     │ Claude API  │              │  GPT-4 API  │
     └──────┬──────┘              └──────┬──────┘
            │                             │
     ┌──────▼──────┐              ┌──────▼──────┐
     │ 15개 조합   │              │ 15개 조합   │
     │ 300회 실험  │              │ 300회 실험  │
     └──────┬──────┘              └──────┬──────┘
            │                             │
     ┌──────▼──────┐              ┌──────▼──────┐
     │experiments_ │              │experiments_ │
     │  claude.csv │              │   gpt.csv   │
     └─────────────┘              └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  통계 분석  │
                    │  비교 보고서 │
                    └─────────────┘
```

### 3.3 실험 일정

| 단계 | 설명 | 소요 시간 |
|-----|------|----------|
| Phase 1 | Claude 실험 (300회) | 3-5시간 |
| Phase 2 | GPT 실험 (300회) | 2-4시간 |
| Phase 3 | 데이터 전처리 | 30분 |
| Phase 4 | 통계 분석 | 1시간 |
| Phase 5 | 보고서 작성 | 2시간 |
| **Total** | | **8-12시간** |

---

## 4. 통제 변수

두 실험에서 **완전히 동일하게** 유지하는 변수들:

### 4.1 입력 데이터
- ✅ 대화 데이터 (20개, 동일)
- ✅ 알고리즘 조합 (15개, 동일)
- ✅ 프롬프트 템플릿 (동일 파일 사용)

### 4.2 실험 조건
- ✅ Random seed: 42
- ✅ Temperature: 0.0 (결정론적)
- ✅ Max tokens: 4096
- ✅ 평가 함수 (동일 코드)
- ✅ 평가 지표 (동일 가중치)

### 4.3 환경
- ✅ 플랫폼: Google Colab
- ✅ Python 버전: 3.11
- ✅ 라이브러리 버전: 동일

### 4.4 평가 방법
- ✅ 노드 개수 적절성 (30%)
- ✅ 키워드 정확성 (40%)
- ✅ 구조 깊이 적절성 (30%)
- ✅ Golden 마인드맵 (동일)

---

## 5. 실험 변수

### 5.1 독립 변수 (Independent Variables)

#### 주요 독립 변수
**API 종류** (2 levels)
- Claude API (claude-sonnet-4-5-20250929)
- GPT-4 API (gpt-4-turbo)

#### 부차 독립 변수
1. **알고리즘 조합** (15 levels)
   - comb_01 ~ comb_15

2. **대화 유형** (5 levels)
   - learning_short (4개)
   - learning_medium (4개)
   - learning_long (4개)
   - brainstorming (4개)
   - info_search (4개)

### 5.2 종속 변수 (Dependent Variables)

#### 주요 종속 변수
1. **마인드맵 품질 점수** (0-100)
   - 노드 점수 (0-30)
   - 키워드 점수 (0-40)
   - 깊이 점수 (0-30)

#### 부차 종속 변수
2. **실행 시간** (초)
3. **성공/실패 여부** (binary)
4. **에러 유형** (categorical)
5. **노드 개수** (count)
6. **구조 깊이** (count)

---

## 6. 데이터 수집

### 6.1 Claude 데이터

**파일:**
- `experiments_claude.csv` (300 rows × 19 columns)
- `experiment_metadata_claude.json`

**수집 방법:**
- Colab 노트북: `Mindmap_Experiment_Colab.ipynb`
- API: Anthropic Claude API
- 모델: claude-sonnet-4-5-20250929

**예상 성공률:** 90-95%

### 6.2 GPT 데이터

**파일:**
- `experiments_gpt.csv` (300 rows × 19 columns)
- `experiment_metadata_gpt.json`

**수집 방법:**
- Colab 노트북: `Mindmap_Experiment_GPT_Colab.ipynb`
- API: OpenAI GPT-4 API
- 모델: gpt-4-turbo

**예상 성공률:** 90-95%

### 6.3 데이터 형식

**CSV 컬럼 (동일):**
```
timestamp, conversation_id, conversation_type, conversation_turns,
combination_id, combination_name,
stage1_session, stage2_context, stage3_keyword, stage4_layout,
status, error,
node_count, node_score, keyword_overlap, max_depth, depth_score, total_score,
execution_time_sec
```

**메타데이터 (차이점):**
- api_used: "anthropic_claude" vs "openai_gpt"
- model: "claude-sonnet-4-5-20250929" vs "gpt-4-turbo"

---

## 7. 분석 방법

### 7.1 기술 통계 (Descriptive Statistics)

#### 7.1.1 중심 경향성
- 평균 (Mean)
- 중앙값 (Median)
- 최빈값 (Mode)

#### 7.1.2 산포도
- 표준편차 (SD)
- 분산 (Variance)
- 범위 (Range)
- 사분위수 (Q1, Q3)
- IQR (Interquartile Range)

#### 7.1.3 분포 형태
- 왜도 (Skewness)
- 첨도 (Kurtosis)

### 7.2 추론 통계 (Inferential Statistics)

#### 7.2.1 전체 비교 (Overall Comparison)

**Independent Samples t-test**
- H0: μ_claude = μ_gpt
- H1: μ_claude ≠ μ_gpt
- α = 0.05

```python
from scipy import stats

claude_scores = df_claude['total_score']
gpt_scores = df_gpt['total_score']

t_stat, p_value = stats.ttest_ind(claude_scores, gpt_scores)

if p_value < 0.05:
    print("유의미한 차이 있음")
```

**Effect Size (Cohen's d)**
```python
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

d = cohens_d(claude_scores, gpt_scores)
```

**해석:**
- |d| < 0.2: 작은 효과
- 0.2 ≤ |d| < 0.5: 중간 효과
- |d| ≥ 0.8: 큰 효과

#### 7.2.2 조합별 비교

**Two-Way ANOVA**
- Factor 1: API (Claude vs GPT)
- Factor 2: Combination (15 levels)
- 상호작용 효과: API × Combination

```python
import statsmodels.api as sm
from statsmodels.formula.api import ols

# 데이터 병합
df_combined = pd.concat([
    df_claude.assign(api='Claude'),
    df_gpt.assign(api='GPT')
])

# Two-Way ANOVA
model = ols('total_score ~ C(api) + C(combination_id) + C(api):C(combination_id)',
            data=df_combined).fit()
anova_table = sm.stats.anova_lm(model, typ=2)

print(anova_table)
```

#### 7.2.3 대화 유형별 비교

**Repeated Measures ANOVA (Mixed Design)**
- Within-subject factor: Conversation Type (5 levels)
- Between-subject factor: API (2 levels)

```python
for conv_type in ['learning_short', 'learning_medium', 'learning_long',
                  'brainstorming', 'info_search']:
    claude_type = df_claude[df_claude['conversation_type'] == conv_type]['total_score']
    gpt_type = df_gpt[df_gpt['conversation_type'] == conv_type]['total_score']

    t_stat, p_value = stats.ttest_ind(claude_type, gpt_type)
    print(f"{conv_type}: t={t_stat:.3f}, p={p_value:.4f}")
```

#### 7.2.4 실행 시간 비교

**Mann-Whitney U Test (비모수)**
- 실행 시간은 정규 분포가 아닐 수 있음
- 비모수 검정 사용

```python
u_stat, p_value = stats.mannwhitneyu(
    df_claude['execution_time_sec'],
    df_gpt['execution_time_sec'],
    alternative='two-sided'
)
```

#### 7.2.5 실패율 비교

**Chi-Square Test (카이제곱 검정)**
- 범주형 데이터 (성공/실패)

```python
contingency_table = pd.crosstab(
    df_combined['api'],
    df_combined['status']
)

chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
```

### 7.3 시각화 (Visualization)

#### 7.3.1 비교 그래프

1. **박스플롯 (Boxplot)**
   - API별 점수 분포 비교
   ```python
   import seaborn as sns
   sns.boxplot(data=df_combined, x='api', y='total_score')
   ```

2. **바이올린 플롯 (Violin Plot)**
   - 분포 형태 상세 비교
   ```python
   sns.violinplot(data=df_combined, x='api', y='total_score')
   ```

3. **히트맵 (Heatmap)**
   - 조합별 API 성능 비교
   ```python
   pivot = df_combined.pivot_table(
       values='total_score',
       index='combination_id',
       columns='api',
       aggfunc='mean'
   )
   sns.heatmap(pivot, annot=True, fmt='.2f')
   ```

4. **산점도 (Scatter Plot)**
   - 직접 비교 (Claude vs GPT per combination)
   ```python
   plt.scatter(claude_means, gpt_means)
   plt.plot([0, 100], [0, 100], 'r--')  # 45도 선
   ```

#### 7.3.2 분포 그래프

1. **히스토그램 (Histogram)**
   ```python
   plt.hist(claude_scores, alpha=0.5, label='Claude', bins=20)
   plt.hist(gpt_scores, alpha=0.5, label='GPT', bins=20)
   plt.legend()
   ```

2. **Q-Q 플롯 (Q-Q Plot)**
   - 정규성 검정
   ```python
   from scipy.stats import probplot
   probplot(claude_scores, dist="norm", plot=plt)
   ```

### 7.4 비용 분석

#### 7.4.1 API 비용 계산

**Claude 비용:**
- Input: $3 / 1M tokens
- Output: $15 / 1M tokens

**GPT-4 Turbo 비용:**
- Input: $10 / 1M tokens
- Output: $30 / 1M tokens

```python
# 예상 토큰 수 (실험당)
avg_input_tokens = 2000
avg_output_tokens = 500

# Claude 비용
claude_cost = (
    (avg_input_tokens * 300 * 3 / 1_000_000) +
    (avg_output_tokens * 300 * 15 / 1_000_000)
)

# GPT 비용
gpt_cost = (
    (avg_input_tokens * 300 * 10 / 1_000_000) +
    (avg_output_tokens * 300 * 30 / 1_000_000)
)

print(f"Claude: ${claude_cost:.2f}")
print(f"GPT: ${gpt_cost:.2f}")
```

#### 7.4.2 비용-성능 비율

**Cost-Performance Ratio**
```python
# 점수당 비용 ($/점)
claude_cpp = claude_cost / claude_scores.mean()
gpt_cpp = gpt_cost / gpt_scores.mean()

print(f"Claude: ${claude_cpp:.4f} per point")
print(f"GPT: ${gpt_cpp:.4f} per point")
```

---

## 8. 예상 결과

### 8.1 예상 시나리오

#### 시나리오 1: Claude 우세
```
평균 점수: Claude 82.5 > GPT 79.3
t-test: p < 0.001
Cohen's d: 0.65 (중간 효과)
비용: Claude $8 < GPT $18
결론: Claude가 성능과 비용 모두 우수
```

#### 시나리오 2: GPT 우세
```
평균 점수: GPT 83.1 > Claude 80.2
t-test: p < 0.001
Cohen's d: 0.58 (중간 효과)
비용: GPT $18 > Claude $8
결론: GPT가 성능 우수하나 비용 높음
```

#### 시나리오 3: 차이 없음
```
평균 점수: Claude 81.2 ≈ GPT 81.5
t-test: p = 0.42 (유의하지 않음)
Cohen's d: 0.06 (작은 효과)
결론: 성능 차이 없으므로 저렴한 Claude 선택
```

#### 시나리오 4: 상호작용 효과
```
Simple 조합: Claude > GPT
Detailed 조합: GPT > Claude
Strict 조합: GPT > Claude
결론: 조합에 따라 최적 API 다름
```

### 8.2 예상 보고서 구조

```markdown
# Chapter X: API 비교 분석

## X.1 전체 비교
- 평균 점수: Claude XX.X, GPT XX.X
- t-test: t=X.XX, p=0.XXX
- Cohen's d: X.XX (중간/큰 효과)

## X.2 조합별 비교
- [표] 15개 조합별 Claude vs GPT 점수
- [그림] 조합별 성능 비교 히트맵
- Two-Way ANOVA 결과

## X.3 대화 유형별 비교
- [표] 5개 유형별 API 성능
- [그림] 유형별 바이올린 플롯

## X.4 실행 시간 및 실패율
- [표] API별 평균 실행 시간, 실패율
- Mann-Whitney U test, Chi-Square test 결과

## X.5 비용-성능 분석
- [표] API별 총 비용, 점수당 비용
- ROI 분석

## X.6 결론 및 권장사항
- 최적 API 선택 기준
- 사용 시나리오별 권장 API
```

---

## 9. 한계점 및 향후 연구

### 9.1 현재 연구의 한계

1. **샘플 크기**
   - 각 조합당 20개 대화만 (작을 수 있음)
   - 더 많은 대화로 재검증 필요

2. **모델 버전**
   - Claude Sonnet 4.5 vs GPT-4 Turbo
   - 다른 모델 버전(Opus, GPT-4o) 미포함

3. **평가 방법**
   - 자동 평가만 사용
   - 인간 평가 미포함

4. **일반화**
   - 마인드맵 생성 태스크에만 국한
   - 다른 NLP 태스크로 일반화 제한

### 9.2 향후 연구 방향

1. **모델 확장**
   - Claude Opus 추가
   - GPT-4o 추가
   - Gemini Pro 추가

2. **평가 확장**
   - 인간 평가자 추가
   - 더 정교한 평가 지표

3. **태스크 확장**
   - 요약, Q&A 등 다른 태스크

4. **프롬프트 최적화**
   - API별 최적 프롬프트 탐색
   - Few-shot 예시 추가

---

**문서 버전:** 1.0
**작성 일자:** 2025-11-08
**작성자:** Claude AI (Mindmap Agent Project)
