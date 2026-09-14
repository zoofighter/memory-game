# AGENTS.md — Memory Claude Agent Guidelines

이 문서는 **Memory Claude (`b_0910_memory_claude`)** 프로젝트에서 작업하는 모든 AI 코딩 에이전트(Antigravity, Claude, Gemini 등)를 위한 핵심 운영 지침 및 제약사항입니다. 에이전트는 작업을 시작하기 전 반드시 본 문서의 원칙을 숙지하고 준수해야 합니다.

---

## 1. 프로젝트 정체성 및 핵심 미션

- **목적**: 단기적인 뉴스성 소음에 휘둘리지 않고, 빅테크·반도체 밸류체인 핵심 기업들의 **정량적 실적(Earnings), 인프라 투자(Capex), 대규모 공급·지분 계약(Contracts), 팹 증설(Fab Capacity), 기술 로드맵(Milestones)**을 체계적으로 축적하여 **2026~2028년 이후의 기술 및 자본 흐름을 예측**하는 인텔리전스 시스템입니다.
- **핵심 질문**:
  > *"하이퍼스케일러의 초대형 AI Capex와 기업 간 장기 공급 계약은 2026~2028년 메모리 및 파운드리, AI 가속기 시장의 업황을 어떻게 결정짓는가?"*

---

## 2. 시점 및 타임라인 규칙 (Critical)

- **프로젝트 기준 시점**: **`2026년 9월 10일`**
- **실적 구분 플래그 (`is_forecast`) 규칙**:
  - **`is_forecast = 0` (확정 실적)**: **2020-Q1 ~ 2026-Q2** (각 사 IR 발표 및 공시가 완료된 실적)
  - **`is_forecast = 1` (전망치)**: **2026-Q3 ~ 2026-Q4 이후** (가이던스, 시장 컨센서스, 시나리오 추정치)
- **금지 사항**: 2026-Q3 이후의 데이터를 확정 실적으로 다루거나, 확정 실적 기간에 임의 추정치를 덮어쓰지 마십시오.

---

## 3. 디렉토리 접근 및 보호 정책

```plaintext
b_0910_memory_claude/
├── 99.raw/     # [절대 보호 구역] 사용자가 수집한 1차 원본 자료 보관소
├── data/       # SQLite DB (memory_claude.db) 및 뷰 설정 파일
├── dashboard/  # 인터랙티브 웹 대시보드 (index.html)
├── docs/       # 기획, 아키텍처, 쿼리 가이드 및 분석 보고서
└── scripts/    # 데이터 적재, DB 마이그레이션, 자동 리포트 생성 스크립트
```

### 🔒 `99.raw/` 디렉토리 보호 (Strict)
- `99.raw/`는 IR 보도자료(PDF), 10-Q/10-K, 뉴스 전문, 수기 메모가 저장되는 **원본 금고**입니다.
- **에이전트는 사용자의 명시적 요청이 없는 한 `99.raw/` 내의 기존 파일을 절대 수정, 덮어쓰기, 삭제하지 않습니다.**
- 파일 읽기 및 신규 원본 파일 배치만 허용됩니다.

### 💾 `data/` 디렉토리 관리
- 메인 데이터베이스: `data/memory_claude.db` (SQLite)
- 테이블 스키마 변경 시에는 사전에 DDL 스크립트(`scripts/add_*.sql`)를 작성하고 정합성을 검증한 후 반영합니다.
- 대규모 UPDATE/DELETE 작업 전에는 반드시 영향받는 행의 수(Row Count)를 사전 확인합니다.

### 📝 `docs/` 문서화 규칙
- 분석 문서 및 정기 산출물은 식별이 쉽도록 날짜 접두사(`YYYY-MM-DD_*.md`) 또는 명확한 명명 규칙을 준수합니다.
- DB 데이터의 신뢰도와 한계를 사용자에게 항상 투명하게 고지합니다. (참조: [docs/2026-09-11_data_source_reliability.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-11_data_source_reliability.md))

---

## 4. 데이터베이스 및 수치 표준 규약

| 항목 | 표준 표기 및 규칙 | 예시 |
| :--- | :--- | :--- |
| **통화 단위** | **USD Billion (십억 달러)** 고정 | `30.04` ($30.04B) |
| **분기 표기** | `YYYY-QN` (하이픈 대문자 Q) | `2024-Q3`, `2026-Q1` |
| **이익률 단위** | 퍼센트(`%`), 소수점 1~2자리 | `65.4` (65.4%) |
| **환율 환산** | 원화(KRW), 대만달러(TWD) 실적은 해당 분기 평균 환율 기준 USD 환산 | SK하이닉스, 삼성전자, TSMC |
| **컨센서스** | 신뢰도 수준(⭐~⭐⭐⭐⭐) 구분 명시, 단순 역산 추정치 여부 투명화 | `beat_miss_status` |

---

## 5. 핵심 밸류체인 21개 기업 — entity_id·티커 매핑

에이전트는 쿼리 및 분석 시 다음 기업 마스터 체계를 준수합니다.  
**DB `entity_id`** (대문자 스네이크) → 괄호 안은 거래소 **ticker**입니다.

- **AI 프론티어 랩** (L1_AI_LAB): Anthropic (`ANTHROPIC`), OpenAI (`OPENAI`)
- **하이퍼스케일러** (L2_HYPERSCALER): Alphabet (`GOOGLE` / GOOGL), Amazon (`AMAZON` / AMZN), Microsoft (`MICROSOFT` / MSFT), Oracle (`ORACLE` / ORCL), Meta (`META` / META)
- **컴퓨팅/가속기** (L3_COMPUTE): NVIDIA (`NVIDIA` / NVDA), AMD (`AMD` / AMD), Broadcom (`BROADCOM` / AVGO)
- **파운드리/장비** (L4_FOUNDRY): TSMC (`TSMC` / TSM), ASML (`ASML` / ASML)
- **메모리/스토리지** (L5_MEMORY): SK하이닉스 (`SK_HYNIX` / 000660), 삼성전자 (`SAMSUNG` / 005930), Micron (`MICRON` / MU), WDC (`WDC` / WDC)
- **광통신/네트워킹** (L6_OPTICAL): Marvell (`MARVELL` / MRVL), Coherent (`COHERENT` / COHR)
- **인프라/특수** (L7_INFRA): SpaceX (`SPACEX`), SoftBank (`SOFTBANK` / 9984), Apple (`APPLE` / AAPL)

---

## 6. 에이전트 작업 원칙 및 응답 스타일

1. **정량적 근거 우선**: 추상적인 서술보다 실제 DB에 적재된 수치(매출, Capex, 마진, 계약 규모)를 기반으로 설명합니다.
2. **코드 및 쿼리 재사용성**: 일회성 조회가 아닌 경우 `scripts/` 또는 `docs/*_query_guide.md`에 기록 가능한 형태로 제공합니다.
3. **파일 링크 표준**: 파일 언급 시 반드시 GitHub Markdown 링크 형식(`[파일명](file:///절대경로)`)을 사용합니다.
4. **선제적 검증**: 스크립트 실행 후 에러 유무뿐 아니라 데이터베이스의 실제 카운트 및 변경 결과를 능동적으로 확인합니다.
