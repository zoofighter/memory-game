# 저장소 점검 결과 및 추가·수정 제안

**작성일**: 2026-09-13  
**프로젝트 기준 시점**: 2026-09-10  
**점검 범위**: `README.md`, `AGENTS.md`, `docs/`, `scripts/`, `dashboard/`, SQLite 스키마 및 현재 데이터  
**원본 보호**: `99.raw/`는 파일 목록과 연결 상태만 확인했으며 기존 파일을 수정하지 않았다.

## 1. 결론

현재 저장소는 21개 기업 마스터, 8개 기업의 분기 실적 208건, 계약·팹·마일스톤·데이터센터 테이블과 대시보드까지 기본 골격을 갖추고 있다. 다만 분석 정확도와 재현성을 보장하려면 **참조 무결성 복구 → 통화 단위 통일 → 원문 근거 연결 → 적재 방식 안전화 → 문서·스키마 동기화** 순으로 정비해야 한다.

가장 먼저 수정할 항목은 다음과 같다.

1. `datacenter_capacity`의 `ALPHABET` 3건을 기업 마스터의 `GOOGLE`로 정규화한다.
2. `earnings_reports`의 `T_KRW` 52건을 분기 평균 환율과 함께 `B_USD`로 환산한다.
3. `contracts` 10건을 포함해 원문 경로가 없는 데이터에 `raw_source`를 연결한다.
4. 전체 삭제 후 재적재하는 스크립트를 트랜잭션 기반 UPSERT로 바꾼다.
5. 현재 DB와 맞지 않는 문서의 SQL·경로·수치 설명을 정정한다.

## 2. 현재 상태 스냅샷

SQLite `integrity_check` 결과는 `ok`였으나, `foreign_key_check`에서는 3건의 위반이 확인됐다.

| 객체 | 현재 건수 | 점검 결과 |
|---|---:|---|
| `entities` | 21 | AGENTS.md의 21개 기업·7개 계층과 일치 |
| `earnings_reports` | 208 | 확정 192건, 전망 16건; 기업·분기 중복 없음 |
| `financials` | 33 | `raw_source`가 33건 모두 비어 있음 |
| `contracts` | 10 | `raw_source`가 10건 모두 비어 있음 |
| `fab_capacity` | 11 | `raw_source` 값은 있으나 실제 파일 경로 여부 추가 검증 필요 |
| `milestones` | 21 | `raw_source`가 21건 모두 비어 있음 |
| `datacenter_capacity` | 13 | 외래키 위반 3건 |
| `entity_strategy` | 0 | 스키마만 있고 데이터 없음 |

실적 플래그는 현재 규칙에 맞는다. `2020-Q1~2026-Q2` 192건은 `is_forecast=0`, `2026-Q3~2026-Q4` 16건은 `is_forecast=1`이며, 확정 실적의 `report_date` 누락도 없다. 이 결과는 **플래그 형식의 정합성**만 의미하며 수치가 공식 원문으로 검증되었다는 뜻은 아니다.

## 3. 반드시 수정할 항목

### P0-1. 데이터센터 외래키 3건 복구

[데이터센터 적재 스크립트](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/scripts/populate_datacenter_capacity.py)는 Google 시설에 `ALPHABET`을 사용하지만 기업 마스터의 식별자는 `GOOGLE`이다.

영향 레코드:

- `DC-GOOGL-COUNCIL`
- `DC-GOOGL-KAIROS`
- `DC-GOOGL-HENDERSON`

수정 전 반드시 영향 행 수가 3건인지 확인하고, DDL이 아니라 데이터 정정용 마이그레이션 스크립트(예: `scripts/fix_datacenter_google_entity.sql`)를 작성한 뒤 DB와 적재 원본 코드를 함께 수정해야 한다. 적재 연결에서 `PRAGMA foreign_keys = ON`도 명시해 같은 오류가 재발하면 즉시 실패하게 해야 한다.

**완료 기준**: `PRAGMA foreign_key_check` 결과 0건, 대시보드 API에서 Google 데이터센터 3건 정상 노출.

### P0-2. 통화 단위를 USD Billion으로 통일

[분기 실적 적재 스크립트](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/scripts/populate_quarterly_earnings.py)와 현재 DB에는 삼성전자 26건, SK하이닉스 26건이 `T_KRW`로 저장되어 있다. 이는 AGENTS.md의 “USD Billion 고정” 규칙과 충돌하며 기업 간 매출·이익 비교를 왜곡할 수 있다.

권장 구조:

- 표준 분석값: `revenue_usd_b`, `op_income_usd_b`, `net_income_usd_b`
- 원보고 값: `reported_value`, `reported_currency`, `reported_unit`
- 환산 근거: `fx_rate`, `fx_rate_type='QUARTER_AVG'`, `fx_source`, `fx_as_of_date`

단순히 기존 값을 덮어쓰지 말고 원화 원값과 적용 환율을 보존해야 한다. 스키마 변경은 먼저 `scripts/add_*.sql` 형식의 DDL을 작성하고 복제 DB에서 검증한다.

**완료 기준**: 분석용 금액 필드는 전부 `B_USD`, 52건 모두 환율과 출처를 역추적할 수 있음.

### P0-3. 출처 추적성 확보

현재 `contracts` 10건, `financials` 33건, `milestones` 21건의 `raw_source`가 모두 비어 있다. `source`에는 “공식 발표”, “업계 추정”, “컨센서스” 같은 설명만 있어 원문을 재확인할 수 없다.

최소 출처 필드 제안:

- `source_type`: `IR`, `SEC`, `NEWS`, `CONSENSUS`, `MANUAL`, `MODEL_ESTIMATE`
- `source_url`: 공개 원문 URL
- `raw_source`: `99.raw/` 아래 상대 경로
- `source_published_at`, `retrieved_at`
- `source_quote` 또는 근거 페이지/섹션
- `verification_status`: `UNVERIFIED`, `SINGLE_SOURCE`, `CROSS_CHECKED`, `PRIMARY_VERIFIED`

한 개 레코드에 복수 출처가 필요한 경우 컬럼을 계속 늘리기보다 `sources`와 `record_sources` 연결 테이블을 추가하는 편이 안전하다.

**완료 기준**: C4 데이터는 공식 1차 출처가 반드시 연결되고, C3 이하는 추정 방식과 한계가 기록됨.

### P0-4. 확정 실적의 실제 검증 상태 분리

`is_forecast=0`은 “기간상 확정 실적 구간”을 뜻하지만, [데이터 신뢰도 문서](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-11_data_source_reliability.md)는 2026-Q1~Q2 수치가 AI 추정일 가능성을 명시한다. 따라서 `is_forecast`만으로 공식 검증 여부를 표현하면 안 된다.

다음 두 축을 분리한다.

- `is_forecast`: 실제/전망의 시간적 성격
- `verification_status` 또는 `is_verified`: 공식 원문 대조 여부

2026-Q1~Q2를 `is_forecast=1`로 바꾸는 것이 아니라, 프로젝트의 고정된 시점 규칙은 유지하면서 검증 상태를 별도로 낮게 표시해야 한다.

## 4. 적재·스키마 개선

### P1-1. 전체 DELETE 적재 제거

[팹·마일스톤 적재 스크립트](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/scripts/populate_fab_and_milestones.py)는 `fab_capacity`와 `milestones`를 전부 삭제하며, [데이터센터 적재 스크립트](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/scripts/populate_datacenter_capacity.py)도 전체 삭제 후 다시 넣는다. 사용자가 추가한 데이터가 있으면 다음 실행에서 사라질 수 있다.

권장 방식:

- 명시적 자연키 또는 ID를 기준으로 `INSERT ... ON CONFLICT DO UPDATE`
- 하나의 트랜잭션에서 적재하고 검증 실패 시 `ROLLBACK`
- 변경 전/후 행 수, 삽입·갱신·미변경 건수 출력
- `--dry-run`과 `--replace-seed-only` 옵션 제공
- 적재 코드가 관리하는 행에 `ingestion_batch_id` 또는 `managed_by` 기록

### P1-2. 제약조건과 고유키 강화

현재 여러 테이블은 값 범위를 주석에만 적고 DB가 강제하지 않는다. 다음 제약을 DDL 마이그레이션으로 추가한다.

- `earnings_reports`: `UNIQUE(entity_id, period)`, `CHECK(is_forecast IN (0,1))`
- 기간: `YYYY-Q1~Q4` 또는 허용된 FY 형식 검사
- 비율: `CHECK(... BETWEEN 0 AND 100)`; 음수가 가능한 마진은 별도 범위 정의
- `confidence`: 허용 코드만 저장
- `beat_miss_status`: `BEAT`, `MISS`, `INLINE`, `NA`로 제한
- 금액과 캐파: 의미상 음수가 불가능한 필드는 0 이상
- 모든 적재 연결: `PRAGMA foreign_keys=ON`

### P1-3. 테이블 역할 중복 해소

`financials`와 `earnings_reports`가 매출·영업이익·Capex를 중복 보유해 값이 갈라질 가능성이 있다. 다음 중 하나를 명시적으로 선택해야 한다.

1. `earnings_reports`를 분기 실적의 단일 원장으로 정하고 `financials`는 연간·산업별 파생 지표만 저장한다.
2. 정규화된 `financial_metrics`를 단일 원장으로 두고 `earnings_reports`는 뷰로 만든다.

현재 규모에서는 1안이 이행 비용이 낮다. 문서에 “어느 테이블이 정본(source of truth)인가”를 명시해야 한다.

### P1-4. 재현 가능한 검증 스크립트 추가

`scripts/validate_db.py`를 추가해 다음 검사를 한 번에 수행하도록 한다.

- SQLite integrity/foreign-key check
- 21개 기업 마스터 일치
- 실적 전망 경계와 분기 형식
- 기업·기간 중복
- 단위 표준과 환율 근거
- 필수 출처와 실제 `99.raw/` 경로 존재 여부
- 고아 레코드, 비율·금액 이상치
- 보고서/대시보드가 요구하는 테이블·컬럼 존재 여부

CI가 없다면 최소한 README의 재현 절차에 이 스크립트를 포함한다.

## 5. 문서에서 수정할 항목

### P1-5. 잘못된 절대 경로 교체

[README](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/README.md), `docs/human.md`, `docs/data_sources.md`, `docs/db_architecture.md`, `docs/2026-09-11_db_query_guide.md` 등에 이전 사용자 경로인 `/Users/chansoojeon/Library/CloudStorage/...`가 남아 있다. 현재 작업 경로인 `/Users/boon/Dropbox/...`로 고치거나, 저장소 내부 문서는 상대 링크로 전환한다.

### P1-6. 기존 다음 작업 문서의 실행 불가능한 SQL 정정

[기존 다음 작업 문서](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-11_next_tasks.md)의 계약 INSERT 예시는 현재 스키마에 없는 `supplier_id`, `total_value_usd_b`, `status` 컬럼을 사용하며 `FOUNDRY`를 `contract_type`으로 제안한다. 실제 컬럼은 `seller_id`, `value_b`이고 허용 계약 유형 주석에는 `SUPPLY`, `INVESTMENT`, `PARTNERSHIP`, `LICENSE`, `SERVICE`가 적혀 있다.

또한 해당 문서가 제안하는 일부 계약 규모와 독점 표현은 원문 연결 없이 확정값처럼 쓰여 있다. DB에 넣기 전에 1차 출처 또는 복수의 신뢰할 수 있는 출처로 검증하고, 미공개 금액은 `NULL`, 추정 금액은 별도 추정 필드와 방법론으로 관리해야 한다.

### P1-7. README와 실제 구현 동기화

README는 `99.raw/contracts`, `99.raw/milestones` 등이 존재하는 것처럼 설명하지만 현재 확인된 원본 하위 폴더는 `financials`, `fab_capacity`, `strategy` 중심이다. 실제 폴더를 만들 예정인지, 문서의 목표 구조인지 구분해서 표시해야 한다.

또한 “8개사 208개 분기”라는 표현은 “8개사 × 26개 분기 = 208개 기업-분기 레코드”로 쓰는 것이 정확하다.

### P2-1. 생성 산출물 정리

`docs/generated/report_summary.md`와 `docs/generated/report_summary copy.md`, `dashboard/sankey_scenario.html`과 날짜가 붙은 유사 파일이 함께 존재한다. 자동 생성 파일은 생성 명령, 기준 DB 해시 또는 생성 시각을 머리말에 기록하고, 정본 파일과 보관본의 규칙을 정한다.

## 6. 기능적으로 추가할 항목

### P2-2. `entity_strategy`의 최소 유효 모델 정의

빈 테이블을 임의의 정성 평가로 채우기 전에 차원 사전과 증거 규칙을 정의한다.

- 차원명과 허용값
- 관측 사실과 분석가 해석의 분리
- `as_of_date`와 유효 기간
- 근거 출처와 신뢰도
- 수정 이력

첫 적재는 21개사 전체를 얕게 채우기보다 핵심 연결망인 NVIDIA, TSMC, SK하이닉스, 삼성전자, Microsoft, Amazon, Google, Meta부터 검증된 근거로 시작하는 것이 낫다.

### P2-3. 수정 이력과 관측 시점 관리

전망치가 바뀌는 과정을 추적하려면 현재 값만 덮어쓰지 말고 다음을 추가한다.

- `observed_at`: 전망치를 관측한 날짜
- `valid_from`, `valid_to`: 값의 유효 구간
- `revision_reason`: 수정 이유
- `supersedes_id`: 이전 레코드 연결
- `ingestion_batch`: 적재 실행 식별자

이 구조가 있어야 “2026년 9월 당시 전망”과 이후 실제 결과를 공정하게 비교할 수 있다.

### P2-4. 대시보드 데이터 품질 표시

[대시보드 서버](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/scripts/serve_dashboard.py)는 DB 값을 그대로 반환한다. UI에서 다음 배지를 함께 표시해야 한다.

- 확정/전망
- 공식 검증/미검증
- 신뢰도 등급
- 원통화/환산 통화
- 출처 링크 또는 원문 파일
- 최종 갱신일

## 7. 권장 실행 순서

| 순서 | 작업 | 위험도 | 검증 |
|---:|---|---|---|
| 1 | Google 데이터센터 식별자 3건 수정 | 낮음 | FK 위반 0건 |
| 2 | `validate_db.py` 추가 | 낮음 | 현재 결함을 자동 재현 |
| 3 | 출처 모델 및 검증 상태 DDL 작성 | 중간 | 복제 DB 마이그레이션 |
| 4 | 계약·재무·마일스톤 원문 연결 | 중간 | 필수 출처 누락 0건 |
| 5 | KRW 52건을 환율 근거와 함께 USD 환산 | 높음 | 원값·환율·USD 값 대조 |
| 6 | DELETE 적재를 안전한 UPSERT로 교체 | 중간 | 2회 실행 결과 동일 |
| 7 | 문서 경로·SQL·스키마 설명 동기화 | 낮음 | 링크 및 예제 실행 검사 |
| 8 | `entity_strategy`와 전망 수정 이력 도입 | 중간 | 샘플 8개사 검토 |

## 8. 변경 시 지켜야 할 안전 절차

1. `data/memory_claude.db`를 직접 대량 수정하기 전에 영향 행 수를 조회한다.
2. 스키마 변경은 별도의 `scripts/add_*.sql` 또는 목적이 분명한 마이그레이션 파일로 작성한다.
3. 복제 DB에서 DDL과 적재 스크립트를 먼저 실행한다.
4. `PRAGMA integrity_check`, `PRAGMA foreign_key_check`, 테이블별 행 수, 전망 경계, 중복을 검증한다.
5. 생성 보고서와 대시보드를 다시 만들고 주요 수치가 변한 이유를 기록한다.
6. `99.raw/`의 기존 파일은 수정·덮어쓰기·삭제하지 않는다.

## 9. 신뢰도와 한계

이 문서는 저장소 내부 파일과 현재 SQLite DB의 구조·건수·정합성을 점검한 결과다. 인터넷이나 기업 IR/공시를 새로 조회하지 않았으므로 개별 실적, 계약 금액, 팹 캐파, 데이터센터 전력 수치의 사실성까지 확인한 것은 아니다. 특히 2026-Q1~Q2 확정 구간의 수치는 기간 규칙상 `is_forecast=0`을 유지하되, 공식 원문 대조 전까지는 “미검증 실제값”으로 취급해야 한다.
