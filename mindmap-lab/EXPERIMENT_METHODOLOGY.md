# 실험 방법론: Google Colab 기반 대규모 마인드맵 생성 실험

## 📋 목차

1. [실험 개요](#1-실험-개요)
2. [실험 환경](#2-실험-환경)
3. [실험 설계](#3-실험-설계)
4. [알고리즘 조합](#4-알고리즘-조합)
5. [대화 데이터 구성](#5-대화-데이터-구성)
6. [실험 절차](#6-실험-절차)
7. [평가 방법](#7-평가-방법)
8. [데이터 수집 및 저장](#8-데이터-수집-및-저장)
9. [품질 보증](#9-품질-보증)

---

## 1. 실험 개요

### 1.1 연구 목적
대화형 AI를 활용한 마인드맵 자동 생성 시스템에서 다양한 알고리즘 조합의 성능을 비교 평가하고, 최적의 조합을 도출한다.

### 1.2 실험 규모
- **총 실험 횟수**: 300회
- **실험 설계**: 20개 대화 × 15개 알고리즘 조합 (Full Factorial Design)
- **예상 소요 시간**: 3-5시간
- **예상 비용**: $5-10 (Anthropic Claude API)

### 1.3 실험 일시
- **계획 수립**: 2025-11-08
- **실험 실행**: 2025-11-08 ~ 2025-11-09 (야간)
- **데이터 분석**: 2025-11-09

---

## 2. 실험 환경

### 2.1 컴퓨팅 플랫폼
- **플랫폼**: Google Colab (Free/Pro)
- **런타임**: Python 3.11
- **CPU**: Intel Xeon (2 vCPUs)
- **메모리**: 12GB RAM
- **선택 이유**:
  - ✅ 무료/저비용 클라우드 컴퓨팅
  - ✅ 장시간 실행 가능 (최대 12-24시간)
  - ✅ 재현 가능한 실험 환경
  - ✅ Jupyter Notebook 기반 (코드 + 문서화)

### 2.2 API 및 모델
- **API 제공자**: Anthropic
- **모델**: claude-sonnet-4-5-20250929
- **API 엔드포인트**: https://api.anthropic.com/v1/messages
- **인증 방식**: API Key
- **요청 제한**:
  - Rate limit: 50 requests/minute (Tier 1)
  - 실험에서는 요청 간 1-2초 대기로 조절

### 2.3 필수 라이브러리
```python
anthropic==0.18.1      # Claude API 클라이언트
pandas==2.1.4          # 데이터 처리
numpy==1.26.3          # 수치 연산
scipy==1.11.4          # 통계 분석
tqdm==4.66.1           # 진행률 표시
```

---

## 3. 실험 설계

### 3.1 실험 변수

#### 독립 변수 (Independent Variables)
1. **알고리즘 조합** (15 levels)
   - Stage 1: 세션 분류 알고리즘 (3종)
   - Stage 2: 맥락 추출 알고리즘 (2종)
   - Stage 3: 키워드 추출 알고리즘 (1종)
   - Stage 4: 레이아웃 알고리즘 (4종)

2. **대화 데이터** (20 conversations)
   - 대화 유형 (5종): learning_short, learning_medium, learning_long, brainstorming, info_search
   - 대화 길이: 5-45 turns

#### 종속 변수 (Dependent Variables)
1. **마인드맵 품질 점수** (0-100점)
   - 노드 개수 적절성 (30%)
   - 키워드 정확성 (40%)
   - 구조 깊이 적절성 (30%)

2. **실행 시간** (초)
   - API 호출 시간
   - 처리 시간
   - 총 소요 시간

3. **성공/실패 여부**
   - 성공: 마인드맵 생성 완료
   - 실패: API 오류, 타임아웃, 파싱 오류 등

#### 통제 변수 (Control Variables)
- API 모델: claude-sonnet-4-5-20250929 (고정)
- Temperature: 0.0 (결정론적 출력)
- Max tokens: 4096 (고정)
- Random seed: 42 (재현성 보장)
- 네트워크 환경: Google Colab 기본 네트워크

### 3.2 실험 설계 유형
- **설계 방법**: Full Factorial Design (완전 요인 설계)
- **반복 횟수**: 각 조합당 20회 (20개 서로 다른 대화)
- **무작위화**: 대화-조합 순서는 고정 (재현성 위해)
- **블라인드**: 평가는 자동화 (평가자 바이어스 제거)

---

## 4. 알고리즘 조합

### 4.1 단계별 알고리즘

#### Stage 1: 세션 분류 알고리즘
대화를 의미적 단위(세션)로 분할하는 알고리즘

| 알고리즘 ID | 이름 | 설명 | 특징 |
|------------|------|------|------|
| v1_simple | Simple Classifier | 화자 전환 기반 분할 | 빠름, 단순 |
| v2_detailed | Detailed Classifier | 주제 변화 감지 분할 | 정확함, 중간 복잡도 |
| v3_strict | Strict Classifier | 의미적 일관성 기반 분할 | 매우 정확, 느림 |

#### Stage 2: 맥락 추출 알고리즘
각 세션에서 핵심 맥락을 추출하는 알고리즘

| 알고리즘 ID | 이름 | 설명 | 특징 |
|------------|------|------|------|
| d1_basic | Basic Extractor | 명사구 추출 | 빠름, 간단 |
| d2_detailed | Detailed Extractor | 의미 관계 파악 후 추출 | 정확함, 복잡 |

#### Stage 3: 키워드 추출 알고리즘
맥락에서 중요 키워드를 추출하는 알고리즘

| 알고리즘 ID | 이름 | 설명 | 특징 |
|------------|------|------|------|
| tfidf | TF-IDF | 단어 빈도-역문서 빈도 | 표준 알고리즘 |

*Note: 본 실험에서는 TF-IDF만 사용 (다른 알고리즘은 향후 연구)*

#### Stage 4: 레이아웃 알고리즘
키워드를 마인드맵 구조로 배치하는 알고리즘

| 알고리즘 ID | 이름 | 설명 | 특징 |
|------------|------|------|------|
| hierarchical | Hierarchical Layout | 계층적 트리 구조 | 전통적, 직관적 |
| force | Force-Directed Layout | 물리 시뮬레이션 기반 | 균형적, 미적 |
| radial | Radial Layout | 중심에서 방사형 확장 | 명확한 중심, 대칭 |
| timeline | Timeline Layout | 시간순 배열 | 시계열 데이터에 적합 |

### 4.2 조합 목록 (15개)

본 실험에서 사용하는 15개 알고리즘 조합:

| 조합 ID | 조합명 | Stage1 | Stage2 | Stage3 | Stage4 | 비고 |
|---------|--------|--------|--------|--------|--------|------|
| comb_01 | simple_hierarchical | v1_simple | d1_basic | tfidf | hierarchical | Baseline |
| comb_02 | simple_force | v1_simple | d1_basic | tfidf | force | |
| comb_03 | simple_radial | v1_simple | d1_basic | tfidf | radial | |
| comb_04 | detailed_hierarchical | v2_detailed | d2_detailed | tfidf | hierarchical | |
| comb_05 | detailed_force | v2_detailed | d2_detailed | tfidf | force | |
| comb_06 | detailed_radial | v2_detailed | d2_detailed | tfidf | radial | |
| comb_07 | strict_hierarchical | v3_strict | d2_detailed | tfidf | hierarchical | |
| comb_08 | strict_force | v3_strict | d2_detailed | tfidf | force | |
| comb_09 | strict_timeline | v3_strict | d2_detailed | tfidf | timeline | |
| comb_10 | hybrid_s1d2_hier | v1_simple | d2_detailed | tfidf | hierarchical | 혼합 1 |
| comb_11 | hybrid_s1d2_force | v1_simple | d2_detailed | tfidf | force | 혼합 2 |
| comb_12 | hybrid_d1s2_radial | v2_detailed | d1_basic | tfidf | radial | 혼합 3 |
| comb_13 | hybrid_str1d2_radial | v3_strict | d2_detailed | tfidf | radial | 혼합 4 |
| comb_14 | hybrid_d1str2_timeline | v2_detailed | d2_detailed | tfidf | timeline | 혼합 5 |
| comb_15 | hybrid_all_hier | v2_detailed | d2_detailed | tfidf | hierarchical | 최적화 |

**조합 선택 기준:**
1. **Baseline 조합** (comb_01-03): 가장 단순한 알고리즘 조합
2. **Detailed 조합** (comb_04-06): 정확도 중심 조합
3. **Strict 조합** (comb_07-09): 최고 정확도 조합
4. **Hybrid 조합** (comb_10-15): 단계별 최적 알고리즘 혼합

### 4.3 파일럿 vs 미드스케일 실험

| 실험 단계 | 조합 수 | 조합 범위 | 목적 |
|----------|---------|-----------|------|
| Pilot | 10개 | comb_01 ~ comb_10 | 초기 탐색, 상위/하위 식별 |
| Midscale | 5개 | comb_11 ~ comb_15 | 혼합 조합 최적화 |

---

## 5. 대화 데이터 구성

### 5.1 대화 유형 분류

총 20개 대화를 5개 유형으로 분류:

| 대화 유형 | 개수 | 평균 Turn 수 | 특징 | 예시 주제 |
|----------|------|-------------|------|----------|
| learning_short | 4개 | 5-11 | 짧은 학습 대화 | "파이썬 함수란?" |
| learning_medium | 4개 | 12-24 | 중간 학습 대화 | "머신러닝 기초" |
| learning_long | 4개 | 25-44 | 긴 학습 대화 | "딥러닝 전체 과정" |
| brainstorming | 4개 | 8-19 | 아이디어 발산 대화 | "앱 기능 아이디어" |
| info_search | 4개 | 6-14 | 정보 탐색 대화 | "여행지 추천" |

### 5.2 대화 데이터 상세

```
conversations/
├── conv_000.json  (learning_short,   8 turns)
├── conv_001.json  (learning_short,  10 turns)
├── conv_002.json  (learning_short,   6 turns)
├── conv_003.json  (learning_short,  11 turns)
├── conv_004.json  (learning_medium, 15 turns)
├── conv_005.json  (learning_medium, 22 turns)
├── conv_006.json  (learning_medium, 18 turns)
├── conv_007.json  (learning_medium, 23 turns)
├── conv_008.json  (learning_long,   32 turns)
├── conv_009.json  (learning_long,   41 turns)
├── conv_010.json  (learning_long,   28 turns)
├── conv_011.json  (learning_long,   38 turns)
├── conv_012.json  (brainstorming,   12 turns)
├── conv_013.json  (brainstorming,   18 turns)
├── conv_014.json  (brainstorming,   10 turns)
├── conv_015.json  (brainstorming,   15 turns)
├── conv_016.json  (info_search,      9 turns)
├── conv_017.json  (info_search,     13 turns)
├── conv_018.json  (info_search,      7 turns)
└── conv_019.json  (info_search,     11 turns)
```

### 5.3 대화 데이터 형식

```json
{
  "conversation_id": "conv_000",
  "type": "learning_short",
  "topic": "파이썬 함수 기초",
  "turns": 8,
  "messages": [
    {
      "turn": 1,
      "role": "user",
      "content": "파이썬에서 함수는 어떻게 정의하나요?"
    },
    {
      "turn": 2,
      "role": "assistant",
      "content": "파이썬에서 함수는 def 키워드를 사용합니다..."
    },
    ...
  ],
  "metadata": {
    "created_at": "2025-11-07",
    "language": "ko",
    "difficulty": "beginner"
  }
}
```

---

## 6. 실험 절차

### 6.1 전체 파이프라인

```
[입력] 대화 데이터 (conversation)
   ↓
[Stage 1] 세션 분류 (Session Classification)
   ↓ sessions = [{session_id, turns, ...}]
[Stage 2] 맥락 추출 (Context Extraction)
   ↓ contexts = [{session_id, context, ...}]
[Stage 3] 키워드 추출 (Keyword Extraction)
   ↓ keywords = [{keyword, weight, ...}]
[Stage 4] 레이아웃 생성 (Layout Generation)
   ↓
[출력] 마인드맵 (mindmap.json)
   ↓
[평가] 품질 평가 (Evaluation)
   ↓
[저장] experiments.csv
```

### 6.2 단계별 상세 절차

#### Stage 1: 세션 분류

**입력:**
```json
{
  "conversation": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    ...
  ]
}
```

**처리:**
```python
prompt_stage1 = load_prompt('stage1_v1_simple.txt')
prompt_stage1 = prompt_stage1.replace('{conversation}', conversation_text)

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    temperature=0.0,
    messages=[{"role": "user", "content": prompt_stage1}]
)

sessions = parse_json_response(response.content[0].text)
```

**출력:**
```json
{
  "sessions": [
    {
      "session_id": 1,
      "start_turn": 1,
      "end_turn": 5,
      "topic": "함수 정의",
      "summary": "def 키워드 사용법"
    },
    {
      "session_id": 2,
      "start_turn": 6,
      "end_turn": 8,
      "topic": "함수 호출",
      "summary": "함수명() 형태로 호출"
    }
  ]
}
```

#### Stage 2: 맥락 추출

**입력:** Stage 1 출력 (sessions)

**처리:**
```python
contexts = []
for session in sessions:
    prompt_stage2 = load_prompt('stage2_d1_basic.txt')
    prompt_stage2 = prompt_stage2.replace('{session}', json.dumps(session))

    response = call_claude(prompt_stage2)
    context = parse_json_response(response)
    contexts.append(context)
```

**출력:**
```json
{
  "contexts": [
    {
      "session_id": 1,
      "main_concept": "함수 정의",
      "sub_concepts": ["def 키워드", "함수명", "매개변수", "return"],
      "relationships": [
        {"from": "함수 정의", "to": "def 키워드", "type": "uses"},
        {"from": "함수 정의", "to": "매개변수", "type": "includes"}
      ]
    }
  ]
}
```

#### Stage 3: 키워드 추출

**입력:** Stage 2 출력 (contexts)

**처리:**
```python
all_keywords = []
for context in contexts:
    # TF-IDF 계산
    keywords = extract_keywords_tfidf(context)
    all_keywords.extend(keywords)

# 중복 제거 및 가중치 조정
final_keywords = merge_and_weight(all_keywords)
```

**출력:**
```json
{
  "keywords": [
    {"keyword": "함수", "weight": 0.85, "frequency": 12},
    {"keyword": "def", "weight": 0.72, "frequency": 8},
    {"keyword": "매개변수", "weight": 0.65, "frequency": 6},
    {"keyword": "return", "weight": 0.58, "frequency": 5}
  ]
}
```

#### Stage 4: 레이아웃 생성

**입력:** Stage 3 출력 (keywords)

**처리:**
```python
prompt_stage4 = load_prompt('stage4_hierarchical.txt')
prompt_stage4 = prompt_stage4.replace('{keywords}', json.dumps(keywords))

response = call_claude(prompt_stage4)
mindmap = parse_json_response(response)
```

**출력:**
```json
{
  "mindmap": {
    "root": {
      "id": "root",
      "label": "파이썬 함수",
      "x": 0,
      "y": 0
    },
    "nodes": [
      {"id": "n1", "label": "함수 정의", "parent": "root", "level": 1},
      {"id": "n2", "label": "def 키워드", "parent": "n1", "level": 2},
      {"id": "n3", "label": "매개변수", "parent": "n1", "level": 2},
      {"id": "n4", "label": "함수 호출", "parent": "root", "level": 1},
      {"id": "n5", "label": "return", "parent": "n1", "level": 2}
    ],
    "edges": [
      {"from": "root", "to": "n1"},
      {"from": "n1", "to": "n2"},
      {"from": "n1", "to": "n3"},
      {"from": "root", "to": "n4"},
      {"from": "n1", "to": "n5"}
    ],
    "layout_type": "hierarchical",
    "max_depth": 2,
    "node_count": 6
  }
}
```

### 6.3 에러 처리 및 재시도

```python
def call_claude(prompt, retries=3):
    """Claude API 호출 with 재시도"""
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )

            # JSON 파싱
            result = parse_json(response.content[0].text)
            return result, None

        except json.JSONDecodeError as e:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            return None, f"parse_error: {str(e)}"

        except Exception as e:
            if "timeout" in str(e).lower():
                return None, "timeout"
            elif "rate" in str(e).lower():
                time.sleep(5)  # Rate limit 대기
                if attempt < retries - 1:
                    continue
            return None, f"api_error: {str(e)}"

    return None, "max_retries_exceeded"
```

**에러 유형:**
- `parse_error`: JSON 파싱 실패
- `timeout`: API 응답 시간 초과 (>60초)
- `api_error`: API 서버 오류 (500, 502, 503)
- `rate_limit`: 요청 제한 초과
- `validation_error`: 출력 형식 검증 실패

---

## 7. 평가 방법

### 7.1 평가 지표

#### 7.1.1 노드 개수 적절성 (30%)

**평가 기준:**
- 최적 범위: 10-30개 노드
- 너무 적음 (< 10): 정보 손실
- 너무 많음 (> 30): 복잡도 증가

**점수 계산:**
```python
node_count = len(mindmap['nodes'])

if 10 <= node_count <= 30:
    node_score = 1.0
elif node_count < 10:
    node_score = node_count / 10  # 선형 감소
else:
    node_score = 30 / node_count  # 역수 감소
```

#### 7.1.2 키워드 정확성 (40%)

**평가 기준:**
- Golden 마인드맵과 키워드 중복도 측정
- Jaccard Similarity 사용

**점수 계산:**
```python
mindmap_keywords = set([n['label'].lower() for n in mindmap['nodes']])
golden_keywords = set([n['label'].lower() for n in golden_mindmap['nodes']])

keyword_overlap = len(mindmap_keywords & golden_keywords) / len(golden_keywords)
```

**Golden 마인드맵:**
- 연구자가 수동으로 작성한 정답 마인드맵
- 각 대화당 1개씩 사전 준비

#### 7.1.3 구조 깊이 적절성 (30%)

**평가 기준:**
- 최적 깊이: 2-5 레벨
- 너무 얕음 (< 2): 계층 부족
- 너무 깊음 (> 5): 복잡도 과다

**점수 계산:**
```python
max_depth = mindmap['max_depth']

if 2 <= max_depth <= 5:
    depth_score = 1.0
else:
    depth_score = 0.6  # 페널티
```

#### 7.1.4 총점 계산

```python
total_score = (
    node_score * 30 +       # 노드 개수 (30%)
    keyword_overlap * 40 +  # 키워드 정확성 (40%)
    depth_score * 30        # 구조 깊이 (30%)
)  # 0-100점
```

### 7.2 통계 분석

#### 7.2.1 기술 통계
- 평균 (Mean)
- 표준편차 (Standard Deviation)
- 95% 신뢰구간 (Confidence Interval)
- 중앙값 (Median)
- 사분위수 (Q1, Q3)

#### 7.2.2 추론 통계

**ANOVA (분산 분석):**
- 귀무가설 (H0): 모든 조합의 평균 점수가 같다
- 대립가설 (H1): 적어도 하나의 조합이 다르다
- 유의수준: α = 0.05

```python
groups = [df[df['combination_id'] == c]['total_score'] for c in combinations]
f_stat, p_value = stats.f_oneway(*groups)

if p_value < 0.05:
    print("조합 간 유의미한 차이 존재")
```

**Post-hoc Test (Tukey HSD):**
```python
from scipy.stats import tukey_hsd

result = tukey_hsd(*groups)
# 어떤 조합 쌍이 유의미하게 다른지 확인
```

#### 7.2.3 대화 유형별 분석

```python
for conv_type in ['learning_short', 'learning_medium', 'learning_long',
                  'brainstorming', 'info_search']:
    type_df = df[df['conversation_type'] == conv_type]

    # 유형별 최적 조합
    best_comb = type_df.groupby('combination_id')['total_score'].mean().idxmax()
```

---

## 8. 데이터 수집 및 저장

### 8.1 실험 결과 데이터

**파일명:** `experiments.csv`

**형식:** CSV (UTF-8 encoding)

**컬럼 구조:**
```
timestamp,conversation_id,conversation_type,conversation_turns,
combination_id,combination_name,
stage1_session,stage2_context,stage3_keyword,stage4_layout,
status,error,
node_count,node_score,keyword_overlap,max_depth,depth_score,total_score,
execution_time_sec
```

**샘플 데이터:**
```csv
2025-11-08 20:15:32,conv_000,learning_short,8,comb_01,simple_hierarchical,v1_simple,d1_basic,tfidf,hierarchical,success,,15,1.0,0.72,3,1.0,81.2,12.4
2025-11-08 20:15:48,conv_000,learning_short,8,comb_02,simple_force,v1_simple,d1_basic,tfidf,force,success,,18,1.0,0.68,4,1.0,79.2,14.1
```

### 8.2 메타데이터

**파일명:** `experiment_metadata.json`

**형식:** JSON

**구조:**
```json
{
  "experiment_name": "mindmap_generation_combinations",
  "start_time": "2025-11-08 20:00:00",
  "end_time": "2025-11-09 02:30:15",
  "duration_seconds": 23415,
  "total_experiments": 300,
  "successful_experiments": 292,
  "failed_experiments": 8,
  "random_seed": 42,
  "api_used": "anthropic_claude",
  "model": "claude-sonnet-4-5-20250929",
  "environment": {
    "platform": "Google Colab",
    "python_version": "3.11.5",
    "runtime_type": "CPU"
  },
  "costs": {
    "total_api_calls": 1200,
    "estimated_cost_usd": 8.45,
    "input_tokens": 2400000,
    "output_tokens": 450000
  }
}
```

### 8.3 중간 저장 (Checkpointing)

실험 중 50회마다 중간 결과 저장:

```python
if (exp_id + 1) % 50 == 0:
    df_temp = pd.DataFrame(experiments)
    df_temp.to_csv(f'experiments_checkpoint_{exp_id+1}.csv', index=False)
    print(f"✅ Checkpoint saved at {exp_id+1} experiments")
```

**중간 저장 파일:**
- `experiments_checkpoint_50.csv`
- `experiments_checkpoint_100.csv`
- `experiments_checkpoint_150.csv`
- `experiments_checkpoint_200.csv`
- `experiments_checkpoint_250.csv`

**용도:**
- 실험 중단 시 재개 가능
- 진행 상황 모니터링
- 조기 결과 분석

---

## 9. 품질 보증

### 9.1 재현성 (Reproducibility)

**고정 요소:**
- ✅ Random seed: 42
- ✅ Temperature: 0.0 (결정론적)
- ✅ 모델 버전: claude-sonnet-4-5-20250929
- ✅ 대화 데이터 순서 고정
- ✅ 조합 순서 고정

**변동 요소:**
- API 네트워크 지연 (실행 시간에만 영향)
- Colab 런타임 할당 (성능 차이 미미)

### 9.2 검증 (Validation)

#### 9.2.1 데이터 검증
```python
# 실험 개수 확인
assert len(df) == 300, f"Expected 300 experiments, got {len(df)}"

# 조합 완전성 확인
for comb in combinations:
    count = len(df[df['combination_id'] == comb['id']])
    assert count == 20, f"Combination {comb['id']}: expected 20, got {count}"

# 점수 범위 확인
assert df['total_score'].min() >= 0, "Score < 0 detected"
assert df['total_score'].max() <= 100, "Score > 100 detected"
```

#### 9.2.2 품질 검증
```python
# 성공률 확인
success_rate = len(df[df['status'] == 'success']) / len(df)
assert success_rate >= 0.90, f"Success rate too low: {success_rate:.2%}"

# 이상치 탐지
q1 = df['total_score'].quantile(0.25)
q3 = df['total_score'].quantile(0.75)
iqr = q3 - q1
outliers = df[(df['total_score'] < q1 - 1.5*iqr) |
              (df['total_score'] > q3 + 1.5*iqr)]
print(f"Outliers: {len(outliers)} / {len(df)}")
```

### 9.3 에러 로깅

모든 에러는 상세 로그와 함께 기록:

```python
error_log = {
    "experiment_id": exp_id,
    "timestamp": datetime.now().isoformat(),
    "conversation_id": conv['id'],
    "combination_id": comb['id'],
    "stage": stage_number,
    "error_type": error_type,
    "error_message": str(error),
    "stack_trace": traceback.format_exc()
}

with open('error_log.jsonl', 'a') as f:
    f.write(json.dumps(error_log) + '\n')
```

### 9.4 실험 프로토콜 준수

- ✅ 실험 전 API 연결 테스트
- ✅ 실험 중 진행률 실시간 표시
- ✅ 50회마다 중간 저장
- ✅ 실험 완료 후 데이터 검증
- ✅ 메타데이터 자동 생성
- ✅ 결과 파일 다운로드 가능

---

## 10. 실험 실행 명령

### 10.1 Colab 노트북 실행

```python
# Cell 1: 패키지 설치
!pip install anthropic pandas numpy scipy tqdm -q

# Cell 2: API 키 입력
api_key = getpass('Anthropic API Key: ')
client = Anthropic(api_key=api_key)

# Cell 3: 대화 데이터 로드
!git clone https://github.com/Kidong8206/mindmap_agent.git

# Cell 4: 실험 실행
experiments = run_experiments(
    conversations=conversations,
    combinations=combinations,
    client=client
)

# Cell 5: 결과 저장
df = pd.DataFrame(experiments)
df.to_csv('experiments.csv', index=False)

# Cell 6: 다운로드
from google.colab import files
files.download('experiments.csv')
files.download('experiment_metadata.json')
```

### 10.2 예상 출력

```
🚀 실험 시작: 2025-11-08 20:00:00
총 300회 실험 예정

Experiments: 100%|██████████| 300/300 [3:42:15<00:00, 44.45s/it]

✅ 실험 완료!
   시작: 2025-11-08 20:00:00
   종료: 2025-11-09 02:30:15
   소요 시간: 6.50시간
   성공: 292
   실패: 8

📊 결과 요약:
   평균 점수: 79.23
   표준편차: 8.45
   최고 점수: 95.67 (comb_13: hybrid_str1d2_radial)
   최저 점수: 52.34 (comb_02: simple_force)
```

---

## 11. 참고 자료

### 11.1 관련 파일
- `Mindmap_Experiment_Colab.ipynb`: 실제 실험 노트북
- `PROTOCOL_REAL_EXPERIMENT.md`: 실험 결과 처리 프로토콜
- `QUICKSTART_REAL_EXPERIMENT.md`: 빠른 시작 가이드
- `run_real_experiment_pipeline.sh`: 자동화 스크립트

### 11.2 GitHub 저장소
- Repository: https://github.com/Kidong8206/mindmap_agent
- Branch: `claude/mindmap-lab-complete-workflow-011CUq5Xky7RXL4wVTUtJAyi`
- Colab 노트북: `/mindmap-lab/Mindmap_Experiment_Colab.ipynb`

### 11.3 API 문서
- Anthropic Claude API: https://docs.anthropic.com/
- Model: claude-sonnet-4-5-20250929
- Pricing: https://www.anthropic.com/pricing

---

**문서 버전:** 1.0
**작성 일자:** 2025-11-08
**작성자:** Claude AI (Mindmap Agent Project)
**최종 수정:** 2025-11-08
