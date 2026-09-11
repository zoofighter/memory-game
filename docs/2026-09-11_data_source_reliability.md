# DB 데이터 소스 및 신뢰도 가이드

**작성일**: 2026-09-11  
**기준 DB**: `data/memory_claude.db` (earnings_reports 테이블, 총 208건)  
**목적**: 데이터 입수 방법, 신뢰 등급, 검증 방법을 투명하게 기록

---

## 1. 솔직한 데이터 입수 경위

현재 `earnings_reports` 테이블의 **전 데이터는 AI(Claude)가 학습 데이터를 기반으로 기억·재구성한 수치**입니다.  
실제 Bloomberg 터미널, FactSet, Refinitiv 등의 유료 데이터베이스나 SEC EDGAR 원본 파일을 직접 파싱한 것이 아닙니다.

| 기간 | 실제 원천 | AI 재구성 방식 | 신뢰도 |
| :--- | :--- | :--- | :---: |
| 2020-Q1 ~ 2023-Q4 | SEC 10-Q/10-K, 각 사 IR 보도자료 (학습 데이터에 포함) | 학습된 수치를 기억하여 재입력 | ⭐⭐⭐⭐ (약 85~95%) |
| 2024-Q1 ~ 2024-Q4 | 동일 (비교적 최근 학습 데이터) | 동일 | ⭐⭐⭐⭐ (약 85~90%) |
| 2025-Q1 ~ 2025-Q2 | 학습 컷오프 인접 구간 | 학습 데이터 + 추론 혼합 | ⭐⭐⭐ (약 70~85%) |
| 2026-Q1 ~ 2026-Q2 | 학습 컷오프 이후 (실제 미경험 구간일 가능성) | **AI 추정/추론** | ⭐⭐ (약 50~70%) |
| 2026-Q3 ~ 2026-Q4 | 미발표 (전망치, is_forecast=1) | 월가 컨센서스 기반 AI 추정 | ⭐ (약 40~60%) |

---

## 2. 컬럼별 신뢰도 세부 평가

| 컬럼 | 신뢰도 | 설명 |
| :--- | :---: | :--- |
| `revenue` (매출) | ⭐⭐⭐⭐ | 대기업 분기 매출은 널리 보도되어 ±5% 이내 |
| `op_income` (영업이익) | ⭐⭐⭐⭐ | ±5~10% 이내, 충당금 처리 분기는 오차 가능 |
| `net_income` (순이익) | ⭐⭐⭐ | 세금·일회성 항목에 따라 ±10~15% 오차 가능 |
| `report_date` (발표일) | ⭐⭐⭐⭐ | 대부분 ±1~3일 이내 (확인 권장) |
| `gross_margin_pct` (매출총이익률) | ⭐⭐⭐⭐ | ±1~3%p 이내 |
| `eps_actual` (실제 EPS) | ⭐⭐⭐ | 액면분할·희석주식수 변동으로 ±5~15% 오차 가능 |
| `eps_consensus` (예상 EPS) | ⭐⭐ | **실제 월가 컨센서스가 아님** — AI 추정값 |
| `consensus_revenue` (예상 매출) | ⭐⭐ | **실제 컨센서스가 아님** — 실적의 약 98%로 역산 |
| `beat_miss_status` (판정) | ⭐⭐ | 컨센서스가 부정확하므로 판정도 참고용 수준 |
| `revenue_breakdown` (매출 비중) | ⭐⭐⭐ | 방향성은 맞으나 ±3~5%p 오차 가능 |
| `guidance_next_q` (가이던스) | ⭐⭐⭐ | 주요 가이던스 범위는 기억 기반, 세부 수치 확인 권장 |
| `key_takeaways` (핵심 코멘트) | ⭐⭐⭐ | 핵심 사실은 맞으나 정확한 인용문은 아님 |

---

## 3. 정확한 데이터 검증 방법

### 3-1. 무료 검증 소스 (우선순위 순)

| 소스 | URL | 확인 가능 항목 | 특징 |
| :--- | :--- | :--- | :--- |
| **Stock Analysis** | `stockanalysis.com/stocks/{ticker}/financials/?p=quarterly` | 분기 손익계산서 전체 | 무료, 정확, 빠름. **첫 번째 교차확인 추천** |
| **Macrotrends** | `macrotrends.net/stocks/charts/{ticker}/revenue` | 분기 매출/이익 시계열 | 차트+테이블, 무료 |
| **autoanalyst.ai.kr** | `autoanalyst.ai.kr/?market=us&tab=stock-info&code={TICKER}` | 한국어 기반 미국주식 재무 | 한국어 인터페이스 |
| **SEC EDGAR** | `sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=10-Q` | 원본 10-Q/10-K PDF | 최고 신뢰도, 시간 소요 |
| **각 사 IR 공식 페이지** | 아래 표 참조 | 어닝 프레스릴리즈, 보충자료 | 원본, 가장 정확 |

### 3-2. 기업별 공식 IR 페이지

| 기업 | IR 주소 | 메뉴 경로 |
| :--- | :--- | :--- |
| 엔비디아 (NVIDIA) | `investor.nvidia.com` | Financial Info → Quarterly Results |
| TSMC | `investor.tsmc.com` | Financial Info → Quarterly Results |
| SK하이닉스 | `skhynix.com/kor/ir/financialInfo/performance.do` | IR → 경영실적 |
| 삼성전자 | `samsung.com/sec/ir/financial-information/financial-results/` | 재무정보 → 경영실적 |
| 구글/Alphabet | `abc.xyz/investor` | Earnings |
| 마이크로소프트 | `microsoft.com/en-us/investor/earnings/` | Earnings |
| 메타 | `investor.atmeta.com` | Earnings |
| 아마존 | `ir.aboutamazon.com/quarterly-results` | Quarterly Results |

### 3-3. 교차 검증 절차 (권장)

```
[1단계] DB에서 검증하고 싶은 기업/분기 조회
    sqlite3 data/memory_claude.db
    "SELECT period, revenue, op_income, eps_actual, report_date
     FROM earnings_reports WHERE entity_id='NVIDIA' ORDER BY period;"

[2단계] stockanalysis.com에서 동일 분기 수치 확인
    → stockanalysis.com/stocks/nvda/financials/?p=quarterly

[3단계] 차이가 ±5% 이상이면 UPDATE 쿼리로 수정
    UPDATE earnings_reports
    SET revenue = [정확한값], source = 'stockanalysis.com 교차검증'
    WHERE entity_id='NVIDIA' AND period='2024-Q4';

[4단계] 원본 IR PDF를 99.raw/financials/ 에 저장 (Phase 2 목표)
```

---

## 4. 컨센서스 데이터를 정확하게 얻으려면

실제 **월가 컨센서스(시장 기대치)** 데이터는 유료 서비스에서만 제공됩니다:

| 소스 | 유형 | 비용 | 비고 |
| :--- | :---: | :---: | :--- |
| **Bloomberg Terminal** | 유료 | ~$2,000/월 | 기관투자자 표준 |
| **FactSet** | 유료 | ~$1,000/월 | 컨센서스 최고 품질 |
| **Refinitiv (LSEG)** | 유료 | 협의 | Reuters 기반 |
| **Visible Alpha** | 유료 | ~$500/월 | 상세 모델링 컨센서스 |
| **Seeking Alpha Premium** | 유료 | ~$20/월 | EPS 컨센서스 제공 |
| **Earnings Whispers** | 부분 무료 | - | `earningswhispers.com` |

> **현실적 대안**: 국내 증권사 리서치 보고서(어닝 시즌 전 발간)의 컨센서스 표를  
> `99.raw/financials/` 에 저장하고 수동 입력하는 방식이 가장 현실적입니다.

---

## 5. 데이터 교체 우선순위 권고

아래 순서로 실제 공시 데이터로 교체할 경우 효율이 높습니다:

1. **엔비디아 2023~2025**: AI 슈퍼사이클의 핵심 기업, 오차 시 분석 왜곡 큼
2. **SK하이닉스 2022~2024**: HBM 전환 스토리의 핵심 데이터
3. **삼성전자 2023~2024**: HBM 지연 및 파운드리 실적 충격 구간
4. **TSMC 2022~2024**: HPC 비중 역전 및 CoWoS 전환 확인
5. **빅테크 4사 (구글/MS/메타/아마존) 2024**: Capex 폭증 및 AI 기여도

---

## 6. 업데이트 루틴 제안

| 시점 | 작업 |
| :--- | :--- |
| **어닝 시즌 (1월, 4월, 7월, 10월)** | 전 분기 확정 실적을 실제 공시 기준으로 UPDATE |
| **분기 후 2주 이내** | 매출/영업익 교차 확인 (stockanalysis.com) |
| **연간** | 연간 10-K 기반으로 전년도 분기 데이터 최종 정확도 검증 |

```sql
-- 특정 분기를 교정할 때 사용하는 UPDATE 템플릿
UPDATE earnings_reports
SET
    revenue          = [정확한값],
    op_income        = [정확한값],
    net_income       = [정확한값],
    eps_actual       = [정확한값],
    gross_margin_pct = [정확한값],
    report_date      = '[YYYY-MM-DD]',
    source           = '[출처: 예) NVIDIA IR FY2025 Q4 10-K, 2025-02-26]'
WHERE entity_id = '[ENTITY_ID]' AND period = '[YYYY-QN]';
```

---

> **요약**: 현재 DB는 트렌드와 방향성 파악에는 충분히 유용하나,  
> 정밀 투자 분석에는 주요 분기부터 순차적으로 공식 IR 자료 기반 교정이 필요합니다.  
> **가장 빠른 검증 방법: `stockanalysis.com` + 각 사 IR 보도자료 교차확인**

---

*작성: Memory Claude 프로젝트 내부 문서*  
*다음 검토 예정: 2026년 10월 어닝 시즌 (2026-Q3 실적 발표 후)*
