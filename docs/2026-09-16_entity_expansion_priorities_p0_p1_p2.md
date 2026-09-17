# 기업 확장 우선순위 — P0·P1·P2

**작성일**: 2026-09-16  
**프로젝트 기준 시점**: 2026-09-10  
**현재 추적 대상**: 21개사  
**목적**: AI Capex가 가속기, 파운드리·패키징, 메모리·스토리지,
네트워크 및 전력 인프라로 전달되는 경로의 기업 공백 보완

## 1. 우선순위 정의

| 우선순위 | 의미 | 등록 원칙 |
|---|---|---|
| **P0** | 현재 핵심 분석을 완성하는 데 반드시 필요한 기업 | 즉시 기업 마스터 등록 및 데이터 적재 |
| **P1** | 데이터센터 병목과 2차 수혜를 정량화하는 기업 | P0 검증 후 순차 등록 |
| **P2** | 신규 수요원·대체 기술·장기 시나리오 기업 | 계약이나 실적 중요도가 확인될 때 등록 |

우선순위는 시가총액이나 시장 인지도보다 다음 기준으로 결정한다.

1. 기존 21개사 사이의 공급망 공백을 연결하는가?
2. 2026~2028년 HBM·NAND·파운드리·AI 가속기 수요 예측에 영향을 주는가?
3. 매출, Capex, 수주, 캐파 등 정량 데이터 수집이 가능한가?
4. 다른 기업과의 계약·공급 관계를 DB로 표현할 수 있는가?
5. 기존 기업과 역할이 중복되지 않는가?

## 2. P0 — 핵심 공급망 완성

### 2.1 대상 기업

| # | 제안 `entity_id` | 기업 | 티커 | 권장 계층 | 핵심 역할 |
|---:|---|---|---|---|---|
| 1 | `ARM` | Arm Holdings | ARM | `L3_COMPUTE` | 서버 CPU 및 커스텀 실리콘 IP |
| 2 | `INTEL` | Intel | INTC | `L4_FOUNDRY_EQUIP` | 파운드리, 첨단 패키징, 서버 CPU |
| 3 | `KIOXIA` | Kioxia Holdings | 285A | `L5_MEMORY_STORAGE` | NAND 및 데이터센터 SSD |
| 4 | `ASE` | ASE Technology | ASX / 3711 | `L4_FOUNDRY_EQUIP` | OSAT 및 첨단 패키징 |
| 5 | `AMKOR` | Amkor Technology | AMKR | `L4_FOUNDRY_EQUIP` | 미국 중심 첨단 패키징 |
| 6 | `APPLIED_MATERIALS` | Applied Materials | AMAT | `L4_FOUNDRY_EQUIP` | 증착·식각·패키징 장비 |
| 7 | `LAM_RESEARCH` | Lam Research | LRCX | `L4_FOUNDRY_EQUIP` | DRAM·NAND 공정 장비 |
| 8 | `KLA` | KLA | KLAC | `L4_FOUNDRY_EQUIP` | 공정 검사·계측과 수율 병목 |
| 9 | `ARISTA` | Arista Networks | ANET | `L6_NETWORK_OPTICAL` | AI 클러스터 Ethernet 패브릭 |
| 10 | `VERTIV` | Vertiv | VRT | `L7_POWER_INFRA` | AI 데이터센터 전력·냉각 |

### 2.2 선정 이유

P0는 현재 시스템에 빠진 다섯 영역을 최소 기업 수로 보완한다.

```text
설계·컴퓨팅      ARM
파운드리 경쟁    INTEL
NAND·SSD         KIOXIA
첨단 패키징      ASE, AMKOR
제조 장비        APPLIED_MATERIALS, LAM_RESEARCH, KLA
AI 네트워크      ARISTA
전력·냉각        VERTIV
```

P0 등록 후 현재 21개사 체계는 31개사로 확장된다.

### 2.3 기업별 핵심 수집 지표

| 기업 | 반드시 수집할 지표 |
|---|---|
| Arm | 데이터센터·클라우드 매출, 로열티, CSS/Neoverse 채택 |
| Intel | 파운드리 매출·손실, Capex, 첨단 패키징 캐파, 공정 일정 |
| Kioxia | NAND 매출, ASP·출하량, 데이터센터 SSD, Fab 가동률 |
| ASE | ATM 매출, 첨단 패키징 비중, Capex, 주요 캐파 증설 |
| Amkor | Advanced Products 매출, Capex, 미국 팹 진행 상황 |
| Applied Materials | 반도체 시스템 매출, 메모리 비중, 수주·가이던스 |
| Lam Research | DRAM·NAND 투자 민감도, 중국 비중, 수주·가이던스 |
| KLA | 검사·계측 매출, 선단공정 비중, 서비스 매출 |
| Arista | Cloud Titans 매출, AI 네트워크 매출, 800G·1.6T 전환 |
| Vertiv | 수주·백로그, 유기적 성장, 냉각·전력 캐파, 가이던스 |

### 2.4 완료 조건

- `entities` 10건 및 주요 `entity_aliases` 등록
- 각 기업 공식 IR URL과 원본 파일 연결
- 최소 최근 8개 분기 확정 실적 적재
- `2026-Q3` 이후 전망치는 별도 플래그와 기준일 기록
- 기업당 최소 1개 계약·캐파·마일스톤 중 해당 데이터 적재
- 외래키 검사 및 대시보드 기업 필터 정상 동작

## 3. P1 — 데이터센터 병목과 2차 수혜 확장

### 3.1 대상 기업

| # | 제안 `entity_id` | 기업 | 티커 | 권장 계층 | 핵심 역할 |
|---:|---|---|---|---|---|
| 1 | `EATON` | Eaton | ETN | `L7_POWER_INFRA` | 배전, UPS 및 전력 관리 |
| 2 | `GE_VERNOVA` | GE Vernova | GEV | `L7_POWER_INFRA` | 발전, 그리드 및 가스터빈 |
| 3 | `SCHNEIDER` | Schneider Electric | SU | `L7_POWER_INFRA` | 배전, 냉각 및 데이터센터 자동화 |
| 4 | `CELESTICA` | Celestica | CLS | `L6_NETWORK_OPTICAL` | AI 서버·스위치 ODM |
| 5 | `DELL` | Dell Technologies | DELL | `L3_COMPUTE` | 엔터프라이즈 AI 서버·랙 |
| 6 | `SUPERMICRO` | Super Micro Computer | SMCI | `L3_COMPUTE` | GPU 서버 및 랙스케일 시스템 |

### 3.2 선정 이유

P1은 GPU와 HBM이 실제 데이터센터 매출로 전환되기 위한 물리적 병목을
측정한다.

```text
GPU·HBM 공급
   ↓
서버·랙 조립          Dell, Supermicro, Celestica
   ↓
전력·배전·UPS         Eaton, Schneider
   ↓
발전·그리드 연결       GE Vernova
```

이 기업들의 수주와 백로그가 증가하지 않는다면 GPU 주문이 강해도 실제
데이터센터 가동 시점이 지연될 수 있다.

### 3.3 핵심 수집 지표

| 구분 | 지표 |
|---|---|
| 서버·ODM | AI 서버 매출, GPU backlog, 랙 납기, 고객 집중도 |
| 전력·배전 | 데이터센터 수주, 백로그, 생산능력, 납기 |
| 냉각 | 수랭 매출, 지원 가능한 랙 밀도와 MW 규모 |
| 발전·그리드 | 가스터빈 수주, 송배전 백로그, 프로젝트 가동 시점 |

### 3.4 P1 등록 조건

P0 적재가 완료된 후 다음 중 하나를 충족할 때 등록한다.

- AI 데이터센터 관련 매출·수주가 별도 공시됨
- 기존 31개사와 중요한 공급 계약이 확인됨
- 데이터센터 가동 시점에 영향을 주는 정량 캐파가 확인됨
- 분기별 실적과 가이던스를 지속해서 수집할 수 있음

## 4. P2 — 신규 수요원과 장기 선택권

### 4.1 대상 기업

| # | 제안 `entity_id` | 기업 | 티커 | 권장 계층 | 핵심 역할 |
|---:|---|---|---|---|---|
| 1 | `XAI` | xAI | 비상장 | `L1_AI_LAB` | 대규모 모델 학습 및 GPU 수요 |
| 2 | `COREWEAVE` | CoreWeave | CRWV | `L2_HYPERSCALER` | GPU 특화 클라우드 |
| 3 | `NEBIUS` | Nebius | NBIS | `L2_HYPERSCALER` | AI 인프라 클라우드 |
| 4 | `CEREBRAS` | Cerebras | 비상장 | `L3_COMPUTE` | 웨이퍼스케일 AI 가속기 |
| 5 | `GROQ` | Groq | 비상장 | `L3_COMPUTE` | 추론 특화 가속기 |
| 6 | `SYNOPSYS` | Synopsys | SNPS | `L4_FOUNDRY_EQUIP` | EDA 및 반도체 IP |
| 7 | `CADENCE` | Cadence | CDNS | `L4_FOUNDRY_EQUIP` | EDA 및 시스템 설계 |

### 4.2 선정 이유

P2는 현재 매출 흐름의 완성보다 미래 시장 구조 변화 탐지를 목적으로 한다.

- xAI·CoreWeave·Nebius: 하이퍼스케일러 밖의 신규 AI 인프라 수요
- Cerebras·Groq: NVIDIA GPU와 다른 가속기 구조의 성장 가능성
- Synopsys·Cadence: 커스텀 ASIC 증가에 따른 설계 복잡도와 EDA 수요

### 4.3 P2 등록 조건

다음 조건 중 두 가지 이상을 충족할 때 정식 마스터로 승격한다.

- 연간 또는 다년 계약 규모가 공개됨
- 데이터센터 MW 또는 가속기 수량이 공개됨
- 분기 실적이나 이에 준하는 운영지표를 지속적으로 공개함
- 기존 핵심 기업과 공급·투자 관계가 확인됨
- 2026~2028년 메모리·파운드리 수요에 유의미한 영향을 줄 규모임

조건을 충족하지 못한 기업은 `entities`에 즉시 추가하지 않고
`milestones` 또는 원본 자료에서 관찰 대상으로 유지한다.

## 5. 우선순위별 실행 순서

| 단계 | 작업 | 예상 결과 |
|---|---|---|
| 1 | P0 10개사 마스터·별칭 등록 | 21개사 → 31개사 |
| 2 | P0 최근 8개 분기 공식 실적 적재 | 장비·패키징·인프라 실적 축 확보 |
| 3 | P0 계약·캐파·마일스톤 연결 | 밸류체인 흐름 보완 |
| 4 | 대시보드와 보고서 확장 검증 | 계층별 비교 가능 |
| 5 | P1 등록 조건 평가 및 선별 적재 | 전력·서버 병목 분석 강화 |
| 6 | P2 분기별 관찰 및 승격 판단 | 신규 수요와 대체 기술 탐지 |

## 6. DB 반영 원칙

기업 추가는 운영 DB 직접 수정만으로 끝내지 않는다.

```text
DB 백업
  → scripts/add_entities_YYYY-MM-DD.sql 작성
  → 사전 중복·영향 행 수 확인
  → entities UPSERT
  → entity_aliases UPSERT
  → 외래키·무결성 검사
  → init_db.sql 동기화
  → AGENTS.md·README·요구사항 문서 갱신
  → 대시보드 검증
```

기업 키는 대문자 스네이크 표기를 사용하며, 등록 이후에는 이름이나 티커가
변경되더라도 `entity_id`를 유지한다.

## 7. 최종 권고

즉시 실행 범위는 P0 10개사로 제한한다. P1은 데이터센터의 물리적 병목을
정량화할 필요가 있을 때 추가하고, P2는 공개 데이터와 계약 규모가 충분한
기업만 정식 마스터로 승격한다.

이 방식은 기업 수를 무분별하게 늘리지 않으면서 다음 분석 흐름을 완성한다.

```text
AI 모델 수요
→ 클라우드 Capex
→ CPU·GPU·ASIC
→ 파운드리·장비·패키징
→ HBM·NAND·SSD
→ 네트워크·광통신
→ 전력·냉각·데이터센터 가동
```

상세 기업 관리 구조와 SQL 예시는
`docs/2026-09-16_entity_management_and_expansion_plan.md`를 참조한다.
