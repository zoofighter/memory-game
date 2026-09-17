# P1 신규 기업 및 공식 실적 적재 결과

**작업일**: 2026-09-16  
**대상 DB**: `data/memory_claude.db`  
**기준 문서**:
- [docs/2026-09-16_entity_expansion_priorities_p0_p1_p2.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-16_entity_expansion_priorities_p0_p1_p2.md)
- [docs/2026-09-16_p0_entity_earnings_load_report.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-16_p0_entity_earnings_load_report.md)

---

## 1. 결과 요약

사용자 요청에 따라 P1 대상 10개 핵심 상장사(AMD, 브로드컴, 마이크론, 오라클, WDC, 마벨, 코히런트, 애플, 이튼, GE 버노바)의 미국 SEC 공식 공시(XBRL Company Facts) 기반 분기 실적을 추출하여 SQLite 데이터베이스에 적재 완료했습니다.

| 항목 | 작업 전 (P0 완료 상태) | 작업 후 (P1 완료 상태) | 변화 |
| :--- | :---: | :---: | :---: |
| **전체 등록 기업 마스터** | 36개사 | 36개사 | 0 |
| **실적 보유 상장 기업 수** | 18개사 | **28개사** | **+10개사** |
| **전체 `earnings_reports` 건수** | 404건 | **642건** | **+238건** |
| **확정 실적 (`is_forecast=0`)** | 387건 | 625건 | +238건 |
| **전망 데이터 (`is_forecast=1`)** | 17건 | 17건 | 0 |

---

## 2. 기업별 적재 세부 현황

| 레이어 | `entity_id` | 기업명 | 티커 | 적재 분기수 | 데이터 기간 | 주요 공시 소스 |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `L2_HYPERSCALER` | `ORACLE` | 오라클 | ORCL | 25분기 | 2020-Q1 ~ 2026-Q1 | SEC Company Facts (CIK 0001341439) |
| `L3_COMPUTE` | `AMD` | AMD | AMD | 26분기 | 2020-Q1 ~ 2026-Q2 | SEC Company Facts (CIK 0000002488) |
| `L3_COMPUTE` | `BROADCOM` | 브로드컴 | AVGO | 26분기 | 2020-Q1 ~ 2026-Q2 | SEC Company Facts (CIK 0001730168) |
| `L5_MEMORY` | `MICRON` | 마이크론 | MU | 25분기 | 2020-Q1 ~ 2026-Q2 | SEC Company Facts (CIK 0000723125) |
| `L5_MEMORY` | `WDC` | 샌디스크/WDC | WDC | 22분기 | 2020-Q1 ~ 2026-Q2 | SEC Company Facts (CIK 0000106040) |
| `L6_OPTICAL` | `MARVELL` | 마벨 | MRVL | 25분기 | 2020-Q1 ~ 2026-Q2 | SEC Company Facts (CIK 0001835632) |
| `L6_OPTICAL` | `COHERENT` | 코히런트 | COHR | 24분기 | 2020-Q1 ~ 2025-Q4 | SEC Company Facts (CIK 0000820318) |
| `L7_INFRA` | `APPLE` | 애플 | AAPL | 25분기 | 2020-Q1 ~ 2026-Q2 | SEC Company Facts (CIK 0000320193) |
| `L8_POWER` | `EATON` | 이튼 | ETN | 26분기 | 2020-Q1 ~ 2026-Q2 | SEC Company Facts (CIK 0001551182) |
| `L8_POWER` | `GE_VERNOVA` | GE 버노바 | GEV | 14분기 | 2023-Q1 ~ 2026-Q2 | SEC Company Facts (CIK 0001996810) |

---

## 3. 핵심 레이어 커버리지 달성 현황

이번 P1 적재를 통해 AI 반도체 밸류체인의 핵심 레이어가 대폭 보강되었습니다:

- **L3 컴퓨팅/가속기 (100% 완료)**: NVIDIA, AMD, 브로드컴, 인텔, Arm
- **L5 메모리/스토리지 (100% 완료)**: SK하이닉스, 삼성전자, 마이크론, WDC, 키옥시아
- **L6 광통신/네트워킹 (100% 완료)**: 아리스타, 마벨, 코히런트
- **L2 하이퍼스케일러 (주요 상장사 완료)**: 마이크로소프트, 구글, 아마존, 메타, 오라클
- **L4 파운드리/장비 (90% 완료)**: TSMC, 어플라이드 머티어리얼즈, 램리서치, KLA, 앰코, ASE
- **L8 전력 인프라 (75% 완료)**: 버티브, 이튼, GE 버노바

---

## 4. 데이터 검증 및 생성 산출물

- **DB 정합성**:
  - `PRAGMA integrity_check`: `ok`
  - `PRAGMA foreign_key_check`: 위반 없음
  - 유일성 인덱스 `uq_earnings_entity_period`: 충돌 및 중복 0건
- **스크립트 및 데이터 파일**:
  - 스크립트: [`scripts/populate_p1_sec_earnings.py`](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/scripts/populate_p1_sec_earnings.py)
  - 사전 검토 JSON: [`data/p1_sec_earnings_preview.json`](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/data/p1_sec_earnings_preview.json)
  - 최신 통합 CSV: [`data/earnings_reports_export.csv`](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/data/earnings_reports_export.csv) (총 642행)
  - 최신 통합 JSON: [`data/earnings_reports_export.json`](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/data/earnings_reports_export.json)
