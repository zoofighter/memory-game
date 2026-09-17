# P0 신규 기업 및 공식 실적 적재 결과

**작업일**: 2026-09-16  
**대상 DB**: `data/memory_claude.db`  
**기준 문서**: `docs/2026-09-16_entity_management_and_expansion_plan.md`

## 1. 결과 요약

P0 대상 10개 기업은 작업 시작 시점에 이미 `entities`와
`entity_aliases`에 등록되어 있었다. 중복 등록은 수행하지 않고 기존 마스터를
유지한 상태에서 공식 공시 기반 분기 실적을 적재했다.

| 항목 | 작업 전 | 작업 후 | 변화 |
|---|---:|---:|---:|
| 기업 마스터 | 36 | 36 | 0 |
| 전체 `earnings_reports` | 208 | 404 | +196 |
| P0 기업 실적 | 0 | 196 | +196 |

## 2. 기업별 적재 현황

| 기업 | 확정 | 전망 | 최초 기간 | 최종 기간 | 주요 출처 |
|---|---:|---:|---|---|---|
| Amkor | 25 | 0 | 2020-Q1 | 2026-Q1 | SEC Company Facts |
| Applied Materials | 24 | 0 | 2020-Q2 | 2026-Q2 | SEC Company Facts |
| Arista Networks | 26 | 0 | 2020-Q1 | 2026-Q2 | SEC Company Facts |
| Arm Holdings | 14 | 0 | 2022-Q2 | 2026-Q1 | SEC Company Facts |
| ASE Technology | 3 | 0 | 2025-Q2 | 2026-Q2 | SEC 6-K 공식 실적 발표 |
| Intel | 26 | 0 | 2020-Q1 | 2026-Q2 | SEC Company Facts |
| Kioxia | 3 | 1 | 2025-Q2 | 2026-Q3 | 일본 IFRS 결산 공시 |
| KLA | 24 | 0 | 2020-Q1 | 2025-Q4 | SEC Company Facts |
| Lam Research | 24 | 0 | 2020-Q1 | 2025-Q4 | SEC Company Facts |
| Vertiv | 26 | 0 | 2020-Q1 | 2026-Q2 | SEC Company Facts |

## 3. 적재 원칙

- 확정 실적은 SEC XBRL, SEC 6-K 또는 기업 공식 결산 공시만 사용했다.
- SEC XBRL에서 독립된 4분기 값이 없으면 FY에서 Q1~Q3를 차감했다.
- 가중평균 주식 수가 달라질 수 있으므로 연간 EPS에서 분기 EPS를 차감하지 않았다.
- Kioxia와 ASE는 공시된 해당 분기 평균 환율로 USD Billion으로 환산했다.
- 공식값이 없는 분기를 임의 보간하거나 시장 추정치로 채우지 않았다.
- 전망치는 기업이 직접 수치 가이던스를 공시한 Kioxia 2026-Q3만 적재했다.
- 아직 발표되지 않은 전망에는 `BEAT/MISS` 판정을 넣지 않았다.

## 4. 환율 환산

### Kioxia

| 기간 | 공시 환율 | 적용 |
|---|---:|---|
| 2025-Q2 | USD/JPY 145 | JPY billion ÷ 145 |
| 2026-Q1 | USD/JPY 155 | JPY billion ÷ 155 |
| 2026-Q2 | USD/JPY 160 | JPY billion ÷ 160 |
| 2026-Q3 전망 | USD/JPY 162 | 회사 가이던스 환율 |

### ASE

| 기간 | 공시 환율 | 적용 |
|---|---:|---|
| 2025-Q2 | NTD/USD 31.18 | TWD million ÷ 31.18 ÷ 1,000 |
| 2026-Q1 | NTD/USD 31.53 | TWD million ÷ 31.53 ÷ 1,000 |
| 2026-Q2 | NTD/USD 31.59 | TWD million ÷ 31.59 ÷ 1,000 |

## 5. 생성·변경 파일

| 파일 | 역할 |
|---|---|
| `scripts/populate_p0_sec_earnings.py` | SEC Company Facts 다운로드·검증·UPSERT |
| `scripts/populate_kioxia_verified_earnings_2026-09-16.sql` | Kioxia IFRS 실적·가이던스 적재 |
| `scripts/populate_ase_verified_earnings_2026-09-16.sql` | ASE 공식 6-K 실적 적재 |
| `scripts/add_earnings_entity_period_unique.sql` | 기업·분기 중복 방지 유일 인덱스 |
| `data/p0_sec_earnings_preview.json` | SEC 추출값 적용 전 검토 자료 |
| `99.raw/financials/sec_companyfacts/*.json` | SEC 원본 Company Facts |

## 6. 검증 결과

- SQLite `PRAGMA integrity_check`: `ok`
- `PRAGMA foreign_key_check`: 위반 없음
- `(entity_id, period)` 중복: 0건
- 수동 적재 SQL 재실행 전후 행 수: 404건으로 동일
- `uq_earnings_entity_period` 유일 인덱스 생성 완료

## 7. 한계와 후속 작업

ASE와 Kioxia는 SEC Company Facts에서 미국 상장사와 같은 분기 XBRL 시계열을
제공하지 않는다. 따라서 현재 공식 문서에서 교차 확인한 최근 분기만
적재했다. 과거 구간은 각 분기 IR PDF를 개별 검증하면서 확장해야 한다.

Arm은 현재 상장·공시 이력상 2020년부터 26개 분기를 만들 수 없다. 공시가
존재하는 기간만 유지하는 것이 적절하다. Applied Materials, KLA 및 Lam
Research의 최신 분기 공백 역시 아직 공식 제출되지 않은 기간을 추정치로
대체하지 않았다.

다음 작업의 우선순위는 다음과 같다.

1. ASE 2020-Q1 이후 6-K 실적 발표 자료의 분기별 자동 추출
2. Kioxia 2020-Q1 이후 공식 IR PDF의 분기별 환율 확인 및 환산
3. KLA의 최근 영업이익을 공식 손익계산서에서 보완
4. 각 기업의 다음 분기 공식 매출 가이던스만 전망 레코드로 추가
5. 대시보드에서 10개 신규 기업과 신규 계층 필터 동작 확인

## 8. 공식 자료

- [SEC Company Facts](https://data.sec.gov/api/xbrl/companyfacts/)
- [ASE 2026-Q2 SEC 6-K](https://www.sec.gov/Archives/edgar/data/1122411/000095010326011351/dp250868_6k.htm)
- [Kioxia 2027년 3월기 Q1 결산 공시](https://ssl4.eir-parts.net/doc/285A/tdnet/2859905/00.pdf)
- [Kioxia IR 자료실](https://www.kioxia-holdings.com/en-jp/ir/library.html)
