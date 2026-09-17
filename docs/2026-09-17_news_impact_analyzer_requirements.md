# [요건정의서] 순방향 뉴스 임팩트 분석기 (News Impact Analyzer)

**문서 버전**: v1.0  
**작성일**: 2026-09-17  
**프로젝트 기준 시점**: 2026-09-10  
**프로젝트 코드명**: `b_0910_memory_claude`  
**상위 문서**: [2026-09-17_news_intelligence_layer_design.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-17_news_intelligence_layer_design.md) (방향 A)  
**관련 문서**:
- [requirements_spec.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/requirements_spec.md) (시스템 전체 요건정의서 v2.0)
- [AGENTS.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/AGENTS.md) (에이전트 운영 지침)
- [2026-09-16_raw_layer_architecture_and_rag_comparison.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-16_raw_layer_architecture_and_rag_comparison.md)

---

## 1. 비전 및 문제 정의

### 1.1 핵심 문제

현재 Memory Claude 시스템은 **"데이터를 넣으면 잘 보여주는 시스템"**이지만, **"새 뉴스가 발생했을 때 기존에 축적한 데이터와 즉각적으로 대조하여 임팩트를 정량화하는 능력"**은 부재합니다.

```
현재 상태:
  뉴스 발생 → 사용자가 수동으로 DB 조회 → 머리속에서 비교 → 임팩트 판단

목표 상태:
  뉴스 발생 → 시스템이 관련 기업 식별 → DB 자동 대조 → 정량적 임팩트 리포트 출력
```

### 1.2 해결 목표

> **"새로운 실적 발표, 공급 계약 체결, 기술 마일스톤 달성 뉴스가 입력되면, 현재 DB에 축적된 658건의 실적 + 15건의 계약($877B) + 25건의 마일스톤 + 12건의 Fab 캐파 데이터와 자동으로 대조하여, 밸류체인 전반에 걸친 정량적 임팩트를 분석하고 후속 조치를 권고하는 시스템을 구축한다."**

### 1.3 비-목표 (Non-Goals, Scope Exclusion)

| 제외 항목 | 이유 |
|:---|:---|
| 실시간 뉴스 스트리밍/크롤링 | 로컬 시스템 특성상 배치 처리가 적합 |
| DB 자동 INSERT/UPDATE | AGENTS.md 원칙: 사용자 확인 후 수동 반영 |
| 주가 예측 또는 매매 신호 생성 | 투자 조언 시스템이 아닌 인텔리전스 시스템 |
| 전체 뉴스 분류/태깅 (범용 NLP) | 36개 밸류체인 기업 한정의 타겟 분석만 수행 |

---

## 2. 사용자 및 사용 시나리오

### 2.1 주 사용자

- **프로젝트 운영자 (1인)**: 빅테크·반도체 밸류체인 36개사의 실적, 계약, 기술 로드맵을 추적하는 투자 리서처. 뉴스/IR 자료를 수동으로 수집하여 DB에 입력하는 워크플로우를 사용 중.

### 2.2 핵심 사용 시나리오

#### 시나리오 1: 실적 발표 뉴스 분석 (Earnings Impact)

```
[입력] 
  사용자가 아래 텍스트를 시스템에 전달:
  "SK하이닉스 2026-Q3 실적: 매출 32.5조원(KRW), 영업이익 15.8조원, OPM 48.6%"

[처리]
  1. 엔티티 식별: "SK하이닉스" → entity_id: SK_HYNIX (entity_aliases 테이블 매칭)
  2. 뉴스 유형 분류: EARNINGS (매출/영업이익/OPM 수치 포함)
  3. 환율 환산: 32.5조 KRW → ~$24.1B (분기 평균 환율 적용)
  4. DB 대조:
     - 전분기(2026-Q2): 매출 $52.86B*, OPM 76.3% → 비교
       (*주: 2026-Q2는 반기 누적 기준일 수 있음 — 원천 확인 필요)
     - 전년동기(2025-Q3): 매출 $17.63B, OPM 46.6% → YoY +36.8%
     - 컨센서스(is_forecast=1): 2026-Q3 전망치와 Beat/Miss 판정
  5. 밸류체인 파급 분석:
     - NVIDIA 향 HBM 공급 안정성 → L3 마진 영향
     - TSMC CoWoS 수요 변화 → L4 캐파 압박도
     - 삼성전자·마이크론 경쟁 포지션 변화

[출력]
  docs/news_impact/2026-09-17_SK_HYNIX_Q3_earnings.md
```

#### 시나리오 2: 공급 계약 뉴스 분석 (Contract Impact)

```
[입력]
  "앤트로픽이 삼성전자와 HBM4 직납 계약 $8B 규모로 체결"

[처리]
  1. 엔티티 식별: "앤트로픽" → ANTHROPIC, "삼성전자" → SAMSUNG
  2. 뉴스 유형 분류: CONTRACT (계약 체결)
  3. DB 대조:
     - 기존 앤트로픽 관련 계약:
       · CON-ANTH-AMZN: AWS 컴퓨트 $280B (INFRA_COMPUTE)
       · CON-ANTH-GOOG: GCP 인프라 $150B (INFRA_COMPUTE)
       · CON-ANTH-SKH: SK하이닉스 메모리 직납 $15B (SUPPLY)
     - 삼성 기존 계약: CON-NVDA-SAM: 엔비디아 HBM4 $14B
     - 삼성 Fab 캐파: 평택 P4 HBM4 라인
  4. 신규 계약의 구조적 의미:
     - 앤트로픽 메모리 조달 다변화 (SK하이닉스 독점 → 삼성 추가)
     - 삼성 HBM4 수주 실적 +$8B → 총 $22B (연간 추정)
     - SK하이닉스 점유율 희석 가능성

[출력]
  docs/news_impact/2026-09-17_ANTHROPIC_SAMSUNG_HBM4_contract.md
```

#### 시나리오 3: 기술 마일스톤 뉴스 분석 (Milestone Impact)

```
[입력]
  "TSMC CoWoS 월 캐파가 12만장 돌파, 2027년 15만장 목표 재확인"

[처리]
  1. 엔티티 식별: "TSMC" → TSMC
  2. 뉴스 유형 분류: MILESTONE (기술/생산 마일스톤)
  3. DB 대조:
     - 기존 fab_capacity: TSMC 관련 레코드 조회
     - 기존 milestones: FAB_MILESTONE 카테고리 중 TSMC 관련
     - HBM 수급 시뮬레이터 파라미터: CoWoS 캐파 70k~150k 범위 내 위치
  4. 수급 밸런스 재계산:
     - 월 12만장 → 연 144만장 → AI 가속기 생산 가능 수량 역산
     - NVIDIA Blackwell/Rubin, Broadcom 커스텀 ASIC 생산량 영향

[출력]
  docs/news_impact/2026-09-17_TSMC_CoWoS_capacity.md
```

#### 시나리오 4: 복합 뉴스 분석 (Multi-Entity Impact)

```
[입력]
  "구글이 자체 TPU Ironwood 기반 AI 인프라 비중을 50%로 확대한다고 발표.
   이에 따라 NVIDIA GPU 구매량 조정 가능성이 제기됨."

[처리]
  1. 엔티티 식별: GOOGLE, NVIDIA (+ 암시적: TSMC, BROADCOM)
  2. 뉴스 유형 분류: STRATEGY (전략 변화, 다수 기업 관련)
  3. DB 대조:
     - GOOGLE 분기 Capex 추이 (earnings_reports.capex)
     - CON-GOOG-NVDA: 구글→엔비디아 GPU 공급 $30B 계약
     - 마일스톤 MS-2027-04: TPU Ironwood 50% 돌파 (일정 대비 진행)
  4. 밸류체인 파급:
     - L3 NVIDIA: 구글 향 GPU 매출 감소 추정 ($B)
     - L3 BROADCOM: 구글 TPU용 커스텀 칩 수요 증가
     - L4 TSMC: GPU↓ + TPU ASIC↑ → 총 파운드리 수요 순변화
     - L5 메모리: HBM 수요 구조 변화 (GPU 탑재 vs ASIC 탑재)
```

---

## 3. 기능 요건 (Functional Requirements)

### FR-01: 뉴스 입력 인터페이스

| 항목 | 상세 |
|:---|:---|
| **입력 방식** | CLI 스크립트 실행 (`python3 scripts/analyze_news_impact.py`) |
| **입력 형태** | ① 자유 텍스트 (뉴스 본문, 메모) ② URL (향후 Stage 2) |
| **입력 언어** | 한국어 / 영어 혼용 지원 |
| **입력 길이** | 1줄 요약 ~ 1,000자 본문 (실적 발표 전문은 향후 Stage 3) |
| **배치 입력** | 향후: 다건 동시 분석 (`--batch` 모드) |

```bash
# 사용법 예시
python3 scripts/analyze_news_impact.py "SK하이닉스 2026-Q3 OPM 48.6%"
python3 scripts/analyze_news_impact.py --file news_article.txt
python3 scripts/analyze_news_impact.py --url "https://example.com/article"  # Stage 2+
```

### FR-02: 엔티티 자동 식별 (Entity Recognition)

| 항목 | 상세 |
|:---|:---|
| **매칭 소스** | `entities` 테이블 (36개사) + `entity_aliases` 테이블 (73개 별칭) |
| **매칭 방식** | 텍스트 내 한글명/영문명/ticker/약칭을 정규식 + 사전 매칭으로 식별 |
| **다중 엔티티** | 하나의 뉴스에서 복수 기업 식별 가능 (시나리오 4 참조) |
| **매칭 실패 처리** | 식별 불가 시 "⚠️ 관련 기업을 자동 식별하지 못했습니다" 표시 + 수동 지정 프롬프트 |
| **우선순위** | 정확 일치 > 부분 일치 > ticker 매칭 순서 |

**매칭 사전 구조** (현재 DB 기반):

```python
# entity_aliases + entities 테이블에서 자동 구축
ENTITY_MATCH_DICT = {
    # 한글명
    "SK하이닉스": "SK_HYNIX",
    "하이닉스": "SK_HYNIX",
    "삼성전자": "SAMSUNG",
    "삼성": "SAMSUNG",
    "엔비디아": "NVIDIA",
    "앤트로픽": "ANTHROPIC",
    "구글": "GOOGLE",
    "알파벳": "GOOGLE",
    # 영문명
    "NVIDIA": "NVIDIA",
    "TSMC": "TSMC",
    "Broadcom": "BROADCOM",
    # Ticker
    "NVDA": "NVIDIA",
    "GOOGL": "GOOGLE",
    "AMZN": "AMAZON",
    "TSM": "TSMC",
    "000660": "SK_HYNIX",
    "005930": "SAMSUNG",
    # 약칭/별칭
    "AWS": "AMAZON",
    "MS": "MICROSOFT",
    "xAI": "SPACEX",
    "Colossus": "SPACEX",
    # ... 총 73개 + 36개 정규 명칭
}
```

### FR-03: 뉴스 유형 자동 분류

입력 텍스트에서 뉴스의 성격을 자동으로 분류합니다.

| 유형 코드 | 한글명 | 식별 키워드/패턴 | DB 대조 테이블 |
|:---|:---|:---|:---|
| `EARNINGS` | 실적 발표 | 매출, 영업이익, OPM, 순이익, EPS, 분기, 실적, revenue, earnings | `earnings_reports` |
| `CONTRACT` | 계약 체결 | 계약, 공급, 납품, 투자, MOU, 합의, deal, supply, agreement | `contracts` |
| `MILESTONE` | 기술/생산 마일스톤 | 양산, 출하, 가동, 개발 완료, 샘플, 출시, launch, production | `milestones` |
| `CAPEX` | 설비투자 | Capex, 투자, 증설, 팹, 공장, fab, expansion, capex | `earnings_reports.capex`, `fab_capacity` |
| `STRATEGY` | 전략/구조 변화 | 전략, 인수, 합병, 분사, 조직, M&A, restructuring | `entity_strategy` |
| `MARKET` | 시장/수급 | 가격, ASP, 수요, 공급, 단가, 점유율, shortage, glut | `fab_capacity`, 수급 시뮬레이터 파라미터 |

**분류 규칙**:
- **규칙 기반** (Stage 1): 키워드 빈도 및 패턴 매칭으로 분류
- **LLM 기반** (Stage 3): 구조화 JSON으로 유형 + 핵심 수치 동시 추출

### FR-04: DB 컨텍스트 자동 조회

식별된 엔티티와 뉴스 유형에 따라 관련 DB 데이터를 자동으로 조회합니다.

#### FR-04-1: 실적 컨텍스트 조회 (EARNINGS 유형)

```sql
-- 해당 기업의 최근 8분기 실적 + 전년동기 비교
SELECT period, revenue, op_income, op_margin_pct, capex,
       beat_miss_status, guidance_next_q, key_takeaways, is_forecast
FROM earnings_reports
WHERE entity_id = :matched_entity_id
ORDER BY period DESC
LIMIT 8;
```

**출력 포맷**:
```
📊 SK_HYNIX 최근 실적 컨텍스트
──────────────────────────────────────────
 분기      │ 매출($B) │ 영업익($B) │  OPM   │ Capex │ 구분
──────────────────────────────────────────
 2026-Q2   │  52.86   │   40.35    │ 76.3%  │  -    │ 확정
 2026-Q1   │  35.87   │   25.66    │ 71.5%  │  -    │ 확정
 2025-Q4   │  22.66   │   13.23    │ 58.4%  │  -    │ 확정
 2025-Q3   │  17.63   │    8.21    │ 46.6%  │  -    │ 확정
 2025-Q2   │  15.75   │    6.68    │ 42.4%  │  -    │ 확정
 ...
──────────────────────────────────────────
 ▶ 전분기 대비: 매출 +47.3%, OPM +4.8%p
 ▶ 전년동기 대비: 매출 +199.8%, OPM +29.7%p
```

#### FR-04-2: 계약 컨텍스트 조회 (CONTRACT 유형)

```sql
-- 해당 기업이 buyer 또는 seller인 모든 계약
SELECT contract_id, buyer_id, seller_id, contract_type,
       value_b, description, announced_date, end_date
FROM contracts
WHERE buyer_id = :entity_id OR seller_id = :entity_id
ORDER BY value_b DESC;
```

#### FR-04-3: 마일스톤 컨텍스트 조회 (MILESTONE 유형)

```sql
-- 해당 기업의 전체 마일스톤 타임라인
SELECT event_id, event_date, category, description,
       impact_level, is_forecast, confidence
FROM milestones
WHERE entity_id = :entity_id
ORDER BY event_date;
```

#### FR-04-4: Fab 캐파 컨텍스트 조회 (CAPEX/MARKET 유형)

```sql
-- 해당 기업의 Fab/제조 캐파 현황
SELECT * FROM fab_capacity
WHERE entity_id = :entity_id
ORDER BY ramp_start_date;
```

#### FR-04-5: 밸류체인 연관 기업 조회 (모든 유형)

```sql
-- 해당 기업과 계약 관계가 있는 기업들 (공급자 + 고객)
SELECT DISTINCT
  CASE WHEN buyer_id = :entity_id THEN seller_id ELSE buyer_id END as related_entity,
  contract_type, value_b, description
FROM contracts
WHERE buyer_id = :entity_id OR seller_id = :entity_id
ORDER BY value_b DESC;
```

### FR-05: 임팩트 분석 엔진

#### FR-05-1: 정량적 비교 분석 (자동 계산)

| 분석 항목 | 계산 로직 | 적용 조건 |
|:---|:---|:---|
| **QoQ 변화율** | `(curr - prev) / abs(prev) * 100` | 전분기 데이터 존재 시 |
| **YoY 변화율** | `(curr - prev_year) / abs(prev_year) * 100` | 전년동기 데이터 존재 시 |
| **Beat/Miss 판정** | 실제치 vs is_forecast=1 전망치 비교 | 전망치 데이터 존재 시 |
| **OPM 변동** | `curr_opm - prev_opm` (%p 단위) | 영업이익률 데이터 존재 시 |
| **환율 환산** | KRW→USD, TWD→USD (분기 평균 환율) | SK하이닉스, 삼성전자, TSMC |
| **계약 규모 비교** | 신규 계약 vs 기존 계약 (`contracts.value_b`) | 계약 관련 뉴스 |

#### FR-05-2: 밸류체인 파급 효과 매트릭스 (규칙 기반)

뉴스의 주체 기업이 속한 레이어에 따라, 영향을 받는 상위/하위 레이어를 자동 식별합니다.

```
[밸류체인 파급 방향]

  L1 AI랩 ←──── L2 하이퍼스케일러 ────→ L3 컴퓨팅
                      │                    │
                      │                    ▼
                      │               L4 파운드리
                      │                    │
                      ▼                    ▼
                 L7 인프라              L5 메모리
                      │                    │
                      ▼                    ▼
                 L8 전력              L6 광통신
```

**파급 규칙 테이블**:

| 뉴스 주체 레이어 | 상향 파급 (수요측) | 하향 파급 (공급측) |
|:---|:---|:---|
| **L2 하이퍼스케일러** (Capex 변동) | L1 AI랩 (컴퓨트 공급 변화) | L3→L4→L5→L6→L8 전체 |
| **L3 컴퓨팅** (신제품/실적) | L2 (구매 비용 변화) | L4 (파운드리 수요), L5 (HBM 수요) |
| **L4 파운드리** (캐파/수율) | L3 (생산 제약/해소) | L5 (패키징 수요) |
| **L5 메모리** (실적/계약) | L3 (원가 변동), L2 (인프라 비용) | L4 (파운드리 수요) |
| **L8 전력** (캐파/계약) | L2→L7 (데이터센터 전력 제약) | - |

#### FR-05-3: 후속 조치 권고 (Actionable Recommendations)

분석 결과에 따라 사용자에게 구체적인 DB 업데이트 작업을 권고합니다.

```
📌 추천 후속 조치 (Action Items)
──────────────────────────────────────────
 ☐ [DB 업데이트] earnings_reports에 SK_HYNIX 2026-Q3 실적 추가
   - period: 2026-Q3, revenue: 24.1, op_income: 11.7, op_margin_pct: 48.6
   - is_forecast: 0 (확정 실적)
   
 ☐ [계약 갱신] contracts 테이블 CON-NVDA-SKH 계약 금액 상향 검토
   - 현재: $18.0B → 갱신 추정: $22~25B
   
 ☐ [대시보드 갱신] dashboard 재생성 필요
   - python3 scripts/generate_multi_company_overlay.py
   - python3 scripts/generate_hbm_market_balance.py
   
 ☐ [99.raw 보관] 원천 자료를 99.raw/financials/ 에 보관
   - 파일명: 2026-09-17_sk_hynix_q3_earnings.txt
```

### FR-06: 분석 리포트 출력

#### FR-06-1: 출력 포맷

```markdown
# 📊 뉴스 임팩트 분석 리포트

**분석 일시**: 2026-09-17 00:38
**뉴스 유형**: EARNINGS (실적 발표)
**관련 기업**: SK_HYNIX (L5_MEMORY)
**밸류체인 파급 범위**: L3 (NVIDIA), L4 (TSMC), L5 (SAMSUNG, MICRON)

---

## 1. 뉴스 요약
> SK하이닉스 2026-Q3 실적: 매출 32.5조원, 영업이익 15.8조원, OPM 48.6%

## 2. DB 대조 결과
### 2.1 실적 비교
| 구분 | 2026-Q2 | 2026-Q3 (신규) | 변화 |
|:---|:---|:---|:---|
| 매출($B) | 52.86 | 24.1 | ... |
| OPM | 76.3% | 48.6% | -27.7%p |

### 2.2 관련 계약 현황
(DB에서 자동 조회된 계약 목록)

### 2.3 마일스톤 진행 상황
(DB에서 자동 조회된 마일스톤 목록)

## 3. 밸류체인 파급 분석
(규칙 기반 자동 분석)

## 4. 추천 후속 조치
(DB 업데이트 권고 사항)
```

#### FR-06-2: 출력 경로

```
docs/
└── news_impact/                    # 뉴스 임팩트 분석 결과 보관 디렉터리
    ├── 2026-09-17_SK_HYNIX_Q3_earnings.md
    ├── 2026-09-17_ANTHROPIC_SAMSUNG_contract.md
    └── 2026-09-17_TSMC_CoWoS_capacity.md
```

---

## 4. 비기능 요건 (Non-Functional Requirements)

### NFR-01: 성능

| 항목 | 기준 |
|:---|:---|
| 분석 실행 시간 (Stage 1) | < 3초 (SQLite 쿼리 + 텍스트 매칭) |
| 분석 실행 시간 (Stage 3, LLM) | < 15초 (API 호출 포함) |
| 메모리 사용량 | < 100MB (Python 스크립트 단독 실행) |

### NFR-02: 데이터 무결성

| 항목 | 규칙 |
|:---|:---|
| DB 읽기 전용 | 분석 스크립트는 DB를 **읽기만** 함 (SELECT only) |
| 원천 보호 | 99.raw/ 파일 수정/삭제 금지 (AGENTS.md 제3조) |
| 환율 표준 | KRW/TWD → USD 환산 시 분기 평균 환율 적용 (AGENTS.md 제4조) |
| 수치 단위 | USD Billion 고정, 분기 표기 YYYY-QN (AGENTS.md 제4조) |

### NFR-03: 확장성

| 항목 | 설계 |
|:---|:---|
| 엔티티 추가 | `entity_aliases` 테이블에 별칭 추가만으로 매칭 범위 확장 |
| 뉴스 유형 추가 | 분류 규칙 딕셔너리에 항목 추가로 유형 확장 |
| 파급 규칙 추가 | 레이어 간 파급 매트릭스에 행 추가로 확장 |
| LLM 백엔드 교체 | Stage 3에서 Gemini/Claude/OpenAI 교체 가능한 추상화 레이어 |

### NFR-04: 운영 환경

| 항목 | 사양 |
|:---|:---|
| OS | macOS |
| Python | 3.10+ |
| DB | SQLite3 (data/memory_claude.db) |
| 외부 의존성 (Stage 1) | 없음 (표준 라이브러리만 사용) |
| 외부 의존성 (Stage 3) | google-generativeai 또는 anthropic SDK |

---

## 5. 데이터 모델

### 5.1 의존하는 기존 테이블

| 테이블 | 용도 | 현재 건수 |
|:---|:---|:---|
| `entities` | 36개사 마스터 (entity_id, name_ko, name_en, layer, ticker) | 36 |
| `entity_aliases` | 기업 별칭 매칭 사전 (alias → entity_id) | 73 |
| `earnings_reports` | 분기 실적 (매출, 영업익, OPM, Capex, 가이던스 등) | 658 |
| `contracts` | 대규모 공급/투자/컴퓨트 계약 | 15 |
| `milestones` | 기술/생산 마일스톤 타임라인 | 25 |
| `fab_capacity` | 팹/제조 캐파 및 증설 계획 | 12 |
| `datacenter_capacity` | 데이터센터 인프라 현황 | 13 |

### 5.2 신규 테이블 (선택적, Stage 2+)

#### `news_analysis_log` — 분석 이력 추적

```sql
CREATE TABLE IF NOT EXISTS news_analysis_log (
    analysis_id     TEXT PRIMARY KEY,           -- 'NA-YYYY-MM-DD-NNN'
    analysis_date   TEXT NOT NULL,              -- ISO 8601
    input_text      TEXT NOT NULL,              -- 입력된 뉴스 텍스트 (최대 2000자)
    input_source    TEXT,                       -- 'manual' / 'bookmark' / 'url'
    news_type       TEXT NOT NULL,              -- EARNINGS / CONTRACT / MILESTONE / CAPEX / STRATEGY / MARKET
    matched_entities TEXT NOT NULL,             -- JSON array: ["SK_HYNIX", "NVIDIA"]
    impact_summary  TEXT,                       -- 1~2문장 핵심 임팩트 요약
    action_items    TEXT,                       -- JSON array: 추천 후속 조치 목록
    output_path     TEXT,                       -- 생성된 리포트 파일 경로
    stage           TEXT DEFAULT 'STAGE_1',     -- STAGE_1 / STAGE_2 / STAGE_3
    created_at      TEXT DEFAULT (datetime('now'))
);
```

**목적**: 시간이 지남에 따라 "어떤 뉴스를 분석했는가"의 이력을 축적하여, 향후 **분석 패턴 파악** 및 **놓친 뉴스 역추적**에 활용합니다.

---

## 6. 구현 단계 (Implementation Stages)

### Stage 1: 규칙 기반 DB 대조 분석기 ⭐ (즉시 구현)

```
scripts/analyze_news_impact.py
├── entity_matcher.py      # 엔티티 자동 식별 모듈
├── news_classifier.py     # 뉴스 유형 분류 모듈
├── db_context_builder.py  # DB 컨텍스트 조회 모듈
├── impact_analyzer.py     # 임팩트 분석 엔진
└── report_generator.py    # 마크다운 리포트 생성
```

**구현 범위**:
- [x] 엔티티 매칭: `entity_aliases` 73건 + `entities` 36건 기반 정규식 매칭
- [x] 뉴스 유형 분류: 6개 유형, 키워드 기반 규칙
- [x] DB 컨텍스트 조회: 5개 테이블 자동 쿼리 (FR-04-1 ~ FR-04-5)
- [x] 정량적 비교 분석: QoQ, YoY, Beat/Miss, OPM 변동 자동 계산
- [x] 밸류체인 파급 규칙: 레이어 간 파급 매트릭스 적용
- [x] 후속 조치 권고: DB 업데이트 + 대시보드 재생성 + 99.raw 보관 추천
- [x] 마크다운 리포트 자동 생성: `docs/news_impact/` 디렉터리 출력

**외부 의존성**: 없음 (Python 표준 라이브러리 + sqlite3)

### Stage 2: 북마크 연동 + 에이전트 프롬프트 통합

**추가 구현 범위**:
- [ ] `sync_chrome_bookmarks.py` 확장: 이전 실행 대비 diff 감지
- [ ] 새 북마크의 제목에서 entity 자동 매칭
- [ ] 매칭된 entity의 DB 컨텍스트를 포함한 **에이전트 프롬프트 자동 생성**
- [ ] `docs/news_alerts/` 디렉터리에 프롬프트 + 컨텍스트 자동 저장

### Stage 3: LLM API 기반 완전 자동화

**추가 구현 범위**:
- [ ] 뉴스 텍스트 → 구조화 JSON 자동 변환 (Gemini Flash / Claude Haiku)
- [ ] 자연어 기반 임팩트 분석 (LLM이 DB 컨텍스트를 참조하여 서술형 분석)
- [ ] `news_analysis_log` 테이블 자동 기록
- [ ] URL 입력 → 페이지 본문 자동 추출 → 분석 파이프라인

---

## 7. 검증 계획 (Verification Plan)

### 7.1 단위 테스트

| 테스트 항목 | 검증 내용 | 기대 결과 |
|:---|:---|:---|
| 엔티티 매칭 정확도 | 73개 별칭 + 36개 정규 명칭 모두 매칭 | 100% 매칭률 |
| 뉴스 유형 분류 | 각 유형별 3개 이상의 테스트 케이스 | 정확 분류 |
| DB 컨텍스트 조회 | 28개 실적 보유 기업 각각 조회 | 빈 결과 없음 |
| QoQ/YoY 계산 | SK_HYNIX 2026-Q2 기준 수동 계산과 대조 | 소수점 1자리 일치 |

### 7.2 통합 테스트

| 시나리오 | 입력 | 기대 출력 |
|:---|:---|:---|
| 시나리오 1 (실적) | "SK하이닉스 Q3 OPM 48.6%" | SK_HYNIX 식별, EARNINGS 분류, 전분기 대비 분석 |
| 시나리오 2 (계약) | "앤트로픽 삼성 HBM4 $8B 계약" | ANTHROPIC+SAMSUNG 식별, CONTRACT 분류, 기존 계약 대조 |
| 시나리오 3 (마일스톤) | "TSMC CoWoS 12만장 돌파" | TSMC 식별, MILESTONE 분류, 수급 파급 분석 |
| 시나리오 4 (복합) | "구글 TPU 비중 50% 확대" | GOOGLE+NVIDIA 식별, STRATEGY 분류, 다수 레이어 파급 |

### 7.3 실사용 검증

- Stage 1 구현 후, **실제 뉴스 3건 이상**을 입력하여 분석 결과의 유용성을 사용자가 평가
- 불필요한 정보 / 누락된 분석 / 잘못된 매칭을 피드백 반영

---

## 8. 리스크 및 대응 방안

| 리스크 | 발생 확률 | 영향도 | 대응 방안 |
|:---|:---|:---|:---|
| 엔티티 매칭 오류 (동음이의어) | 중 | 중 | "MS" → MICROSOFT vs 밀리초? → 문맥 규칙 + 수동 확인 프롬프트 |
| 비정형 뉴스의 수치 추출 실패 | 중 | 낮 | Stage 1에서는 수치 추출 없이 DB 대조만 수행, Stage 3에서 LLM 보완 |
| DB 데이터 부재 (비상장 8개사) | 확정 | 낮 | "⚠️ 해당 기업의 실적 데이터가 DB에 없습니다" 명시적 표시 |
| 환율 환산 오류 | 낮 | 중 | DB의 기존 fx_rate 필드 활용, 미입력 시 경고 표시 |
| 밸류체인 파급 분석의 과도한 단순화 | 높 | 낮 | Stage 1에서는 "참고용"으로 명시, Stage 3에서 LLM 서술 보완 |

---

## 9. 용어 정의 (Glossary)

| 용어 | 정의 |
|:---|:---|
| **순방향 분석** | 뉴스 입력 → DB 대조 → 임팩트 산출의 흐름 |
| **역방향 발견** | DB 데이터 → 부족/이상 감지 → 뉴스 탐색 권고 (별도 요건정의서) |
| **엔티티 매칭** | 텍스트에서 36개 밸류체인 기업을 자동 식별하는 처리 |
| **임팩트 분석** | 뉴스가 기존 DB 데이터 대비 어떤 변화/영향을 의미하는지 정량화 |
| **파급 매트릭스** | L1~L8 밸류체인 레이어 간 영향 전파 규칙 |
| **Beat/Miss** | 실제 실적이 사전 전망치(is_forecast=1) 대비 상회/하회 여부 |
| **Stage 1/2/3** | 구현 단계 (규칙 기반 → 북마크 연동 → LLM 자동화) |
