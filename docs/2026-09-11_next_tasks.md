# 다음 작업 추천 — 2026-09-11

**작성일**: 2026-09-11 21:39  
**기준**: 오늘 완료 작업 + DB 현황 (earnings_reports 208건, contracts 10건, entity_strategy 0건)

---

## 오늘(09-11) 완료된 작업 요약

| # | 작업 | 산출물 |
|:---:|:---|:---|
| 1 | 요건정의서 Gap Analysis | `requirements_gap_analysis.md` |
| 2 | `requirements_spec.md` v1.0 → **v2.0** 갱신 | 9테이블·6뷰·21개사·Phase 9까지 |
| 3 | `AGENTS.md` DB 동기화 | 21개사 매핑, 경로 수정, dashboard/ 추가 |
| 4 | 유사 시스템 비교 + 진행 방향 문서 | [2026-09-11_system_comparison_and_roadmap.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-11_system_comparison_and_roadmap.md) |
| 5 | Sankey 다이어그램 프로토타입 | [dashboard/sankey_scenario.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/sankey_scenario.html) |
| 6 | 시나리오 시뮬레이터 프로토타입 | 동일 파일 (탭 2) |

---

## 다음 작업 추천 — 우선순위별

### 🔴 P0 — 데이터 신뢰도 제고 (가장 임팩트 큰 것)

**`earnings_reports` 핵심 수치 SEC EDGAR로 검증**

현재 208건 데이터가 AI 추정치(⭐⭐~⭐⭐⭐)입니다.  
NVIDIA·Google·Amazon 3개사만이라도 SEC EDGAR 원본과 대조하면 신뢰도가 즉시 ⭐⭐⭐⭐으로 올라갑니다.

```bash
# 바로 실행 가능 — 무료, 계정 없음
python3 scripts/fetch_sec_edgar.py --entity NVIDIA GOOGLE AMAZON
```

- 참조: [2026-09-11_data_source_reliability.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-11_data_source_reliability.md)

---

### 🟡 P1 — 데이터 공백 채우기

#### ① `contracts` 테이블 보강 (현재 10건)

실제 체결된 주요 계약 중 미입력된 것들:

| 계약 | 추정 규모 | 비고 |
|:---|:---|:---|
| SoftBank → NVIDIA (Stargate) | ~$500B | AI 인프라 초대형 계약 |
| Oracle → NVIDIA GPU 공급 | 미공개 | OCI AI 인프라 |
| Amazon → TSMC CoWoS 패키징 | 미공개 | AWS Trainium2 |
| Apple → TSMC A-시리즈 독점 | 미공개 | 장기 파운드리 계약 |

#### ② 두 대시보드 통합

`sankey_scenario.html` → `index.html`에 탭으로 통합  
현재 대시보드가 2개로 분리되어 있음. 통합 시 완성된 단일 대시보드.

---

### 🟢 P2 — 전략 데이터 적재

**`entity_strategy` 테이블 — 현재 0건**

21개사의 전략 차원(AI 로드맵, Capex 의지, 파트너십 전략)을 기록하면:
- 시나리오 시뮬레이터의 민감도 계수를 데이터 기반으로 교체 가능
- 기업 전략 변화 시점별 추적 가능

---

### 🟢 P2 — `validator.py` 구현 (Phase 6)

**`99.raw/` 수기 입력 → DB 자동 파이프라인**

현재 `99.raw/manual.md` 수기 내용이 DB에 자동 반영되지 않음.  
`validator.py` 완성 시 수기 메모 → 구조화 DB 파이프라인 완성.

---

## 실행 순서 제안

```
즉시 (10분)   → contracts 테이블 보강 (Stargate 등 대형 계약 추가)
단기 (30분)   → index.html + sankey_scenario.html 통합 대시보드
중기 (1~2일)  → SEC EDGAR API 연동 스크립트 작성
중기 (2~3일)  → entity_strategy 21개사 데이터 적재
장기 (1주)    → validator.py 구현 (Phase 6 완성)
```

---

## 현재 DB 상태 스냅샷 (2026-09-11 기준)

| 테이블 | 확정 | 전망 | 비고 |
|:---|:---:|:---:|:---|
| `earnings_reports` | 192건 | 16건 | AI 추정치 기반, SEC EDGAR 검증 필요 |
| `contracts` | 10건 | — | **보강 우선 (주요 빅테크 공급계약 보강)** |
| `financials` | 33건 | — | 기존 요약 재무 데이터 (양호) |
| `datacenter_capacity` | 13건 | — | 양호 (주요 하이퍼스케일러 및 AI 랩) |
| `fab_capacity` | 11건 | — | 양호 (TSMC, 삼성전자, SK하이닉스, 인텔 등) |
| `milestones` | 21건 | — | 양호 (주요 제품 및 공정 마일스톤) |
| `entities` | 21개사 | — | 밸류체인 L1~L7 마스터 완비 |
| `entity_aliases` | 25건 | — | 티커 및 검색 별칭 매핑 완비 |
| `entity_strategy` | 0건 | — | **미적재 (P2 단계에서 적재 예정)** |

---

## 세부 실행 가이드 (Actionable Checklist)

### 1단계: `contracts` 테이블 즉시 보강 (10분 소요)

누락된 핵심 장기 공급 및 전략적 제휴 계약을 DB에 INSERT:

```sql
-- 1. SoftBank -> NVIDIA: Stargate AI 슈퍼컴퓨터 인프라
INSERT INTO contracts (contract_id, buyer_id, supplier_id, contract_type, total_value_usd_b, start_date, end_date, description, status)
VALUES ('CNT-2026-SFT-NVDA', 'SOFTBANK', 'NVIDIA', 'SUPPLY', 500.0, '2025-01-01', '2030-12-31', 'Stargate 프로젝트 및 AI 인프라 대규모 GPU/시스템 공급', 'ACTIVE');

-- 2. Oracle -> NVIDIA: OCI Supercluster 확장 공급
INSERT INTO contracts (contract_id, buyer_id, supplier_id, contract_type, total_value_usd_b, start_date, end_date, description, status)
VALUES ('CNT-2025-ORCL-NVDA', 'ORACLE', 'NVIDIA', 'SUPPLY', 40.0, '2025-06-01', '2028-12-31', 'OCI 차세대 AI 인프라 Blackwell GPU 클러스터 공급', 'ACTIVE');

-- 3. Amazon -> TSMC: Trainium2/Inferentia3 패키징 CoWoS 물량 선점
INSERT INTO contracts (contract_id, buyer_id, supplier_id, contract_type, total_value_usd_b, start_date, end_date, description, status)
VALUES ('CNT-2025-AMZN-TSMC', 'AMAZON', 'TSMC', 'FOUNDRY', 15.0, '2025-01-01', '2027-12-31', 'AWS Trainium2 3nm 제조 및 CoWoS 어드밴스드 패키징 공급', 'ACTIVE');

-- 4. Apple -> TSMC: 2nm (N2) 공정 초도 물량 독점 공급
INSERT INTO contracts (contract_id, buyer_id, supplier_id, contract_type, total_value_usd_b, start_date, end_date, description, status)
VALUES ('CNT-2025-AAPL-TSMC', 'APPLE', 'TSMC', 'FOUNDRY', 25.0, '2025-09-01', '2027-12-31', 'A19 Pro 및 M5용 N2(2nm) 파운드리 전량 독점 배정', 'ACTIVE');

-- 5. Meta -> AMD: 차세대 MI350/MI400 가속기 대규모 도입
INSERT INTO contracts (contract_id, buyer_id, supplier_id, contract_type, total_value_usd_b, start_date, end_date, description, status)
VALUES ('CNT-2025-META-AMD', 'META', 'AMD', 'SUPPLY', 12.0, '2025-03-01', '2027-12-31', 'Llama 서빙 및 오픈 추론 인프라용 AMD Instinct 가속기 공급', 'ACTIVE');
```

---

### 2단계: 대시보드 통합 작업 (`index.html` + `sankey_scenario.html`)

- **목표**: 대시보드를 일원화하여 사용자가 한 화면에서 모든 시각화 도구를 탐색 가능하도록 개편.
- **통합 탭 구성**:
  1. `Tab 1: Earnings & Capex Overview` (기존 `index.html` 기능 — 분기별 실적, Capex, 마진)
  2. `Tab 2: Capital Flow Sankey` (신규 D3 Sankey — 빅테크 Capex → 하드웨어 밸류체인 흐름)
  3. `Tab 3: Scenario Simulator` (신규 시뮬레이터 — 3대 충격 시나리오 및 기업별 민감도 분석)
  4. `Tab 4: Value Chain Network` (21개사 계약 및 공급망 상호의존성 그래프)
- **파일 위치**: `dashboard/index.html`로 단일 번들링 유지 (CDN 라이브러리: Chart.js, D3.js).

---

### 3단계: SEC EDGAR 자동 수집 검증 스크립트 (`fetch_sec_edgar.py`)

- **목표**: 10-Q/10-K 원본 XBRL API를 연동하여 `earnings_reports` 실적 수치를 100% 공시 기반(⭐⭐⭐⭐)으로 격상.
- **수집 대상**:
  - 미국 직상장 14개사 (NVIDIA, GOOGLE, AMAZON, MICROSOFT, META, ORACLE, AMD, BROADCOM, MICRON, WDC, MARVELL, COHERENT, ASML(ADR), TSMC(ADR))
- **동작 방식**: SEC EDGAR Company Facts API (`https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json`) 활용 (무료, API Key 불필요, User-Agent 헤더 필수).

---

### 4단계: `entity_strategy` 테이블 데이터 적재

- **목표**: 21개사의 중장기 전략 팩터를 구조화하여 시뮬레이터 민감도 및 밸류체인 분석의 뼈대 형성.
- **적재 필드**:
  - `ai_capex_willingness`: High / Moderate / Low (Capex 유지 강도)
  - `custom_silicon_strategy`: Proprietary / Hybrid / Merchant-only (자체 칩 내재화 비중)
  - `memory_procurement_priority`: HBM3E / HBM4 / LPDDR5X (메모리 조달 로드맵)
  - `key_risks`: 전력 수급, 수율 병목, 독점 규제 등

---

### 5단계: `validator.py` 파이프라인 (Phase 6 완성)

- **목표**: `99.raw/manual.md` 및 향후 수기 입력 문서를 자동으로 파싱하여 정합성 검사 후 DB에 UPSERT.
- **검증 규칙**:
  - `entity_id`가 21개사 마스터에 존재하는가?
  - `quarter` 포맷이 `YYYY-QN` 규격을 만족하는가?
  - 단위가 USD Billion 기준 음수/극단치 오류가 없는가?
  - `is_forecast` 플래그 규칙(2026-Q2 이하 = 0, 2026-Q3 이상 = 1) 준수 여부.

