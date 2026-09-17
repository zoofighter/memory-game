# Memory Claude — 미흡한 부분 및 추가 고민 사항 종합 검토

**작성일**: 2026-09-17  
**프로젝트 기준 시점**: 2026-09-10  
**검토 범위**: DB 데이터 품질, 대시보드, 스크립트, 문서, 시스템 아키텍처, 99.raw RAG 도입 타당성 전반

---

## 1. 🔴 즉시 수정 필요 (Broken / Critical)

### 1.1 빈 파일 3건 — 재생성 불가 상태

| 파일 | 크기 | 문제 | 영향 |
|:---|:---:|:---|:---|
| [dashboard/layer_capital_absorption.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/layer_capital_absorption.html) | **0 bytes** | 대시보드 파일이 비어 있음 | 레이어별 자본 흡수 분석 페이지 접근 불가 |
| [scripts/generate_multi_company_overlay.py](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/scripts/generate_multi_company_overlay.py) | **0 bytes** | 생성 스크립트가 비어 있음 | multi_company_overlay.html 재생성 불가 |
| [scripts/generate_network_graph.py](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/scripts/generate_network_graph.py) | **0 bytes** | 생성 스크립트가 비어 있음 | network_graph.html 재생성 불가 |
| [scripts/generate_hbm_market_balance.py](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/scripts/generate_hbm_market_balance.py) | **0 bytes** | 생성 스크립트가 비어 있음 | hbm_market_balance.html 재생성 불가 |

> [!CAUTION]
> 대시보드 HTML은 남아 있지만, 생성 스크립트 3개가 빈 파일이므로 **DB 데이터 변경 시 대시보드를 갱신할 수 없음**. 이 스크립트들은 DB에서 데이터를 읽어 HTML에 인라인 JSON으로 주입하는 역할이었음. 재작성 또는 백업 복원이 필요.

### 1.2 대시보드 중복 파일

- [dashboard/2026-09-11_sankey_scenario.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/2026-09-11_sankey_scenario.html) (23KB) — 구버전
- [dashboard/sankey_scenario.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/sankey_scenario.html) (25KB) — 현행 버전

두 파일이 공존하여 혼란 가능. 구버전 삭제 또는 아카이브 이동 권장.

---

## 2. 🟠 데이터 품질 갭 (Data Quality Gaps)

### 2.1 7대 핵심 기업의 OPM 입력 불완전

**가장 중요한 7대 기업**(NVIDIA, GOOGLE, AMAZON, META, MICROSOFT, SAMSUNG, TSMC)의 OPM이 **전체 28분기 중 2~6분기만 입력**되어 있음:

| 기업 | 전체 분기 | OPM 입력 | 입력률 | 입력된 기간 |
|:---|:---:|:---:|:---:|:---|
| NVIDIA | 28 | 5 | 17.9% | 2025-Q2 ~ 2026-Q2 |
| MICROSOFT | 28 | 4 | 14.3% | 2025-Q2 ~ 2026-Q2 |
| SAMSUNG | 28 | 4 | 14.3% | 2025-Q3 ~ 2026-Q2 |
| GOOGLE | 28 | 3 | 10.7% | 2025-Q2 ~ 2025-Q4 |
| META | 28 | 3 | 10.7% | 2025-Q2 ~ 2025-Q4 |
| AMAZON | 28 | 2 | 7.1% | 2025-Q3 ~ 2025-Q4 |
| TSMC | 28 | 2 | 7.1% | 2025-Q3 ~ 2025-Q4 |

> [!WARNING]
> 반면 P1 기업(AMD, Broadcom, Intel, Micron, Vertiv 등)은 **26분기 전체 OPM이 입력**되어 있음. P0(7대 핵심) 기업의 2020-Q1 ~ 2025-Q1 기간 OPM이 누락된 것은 데이터 적재 시점의 차이로 추정. **핵심 기업 OPM 소급 입력이 시급.**

### 2.2 Capex 데이터 극심한 부족

- `earnings_reports.capex` 필드: **2사만 입력** (GOOGLE 2건, META 1건)
- `financials` 테이블에 별도 CAPEX 데이터: **33건** (GOOGLE, AMAZON, META, MICROSOFT 등 하이퍼스케일러 + NVIDIA, TSMC)
- **두 테이블에 Capex 데이터가 분산**되어 있어 조회 시 혼란 발생

```
earnings_reports.capex  → 3건 (거의 비어 있음)
financials.metric='CAPEX' → 33건 (하이퍼스케일러 위주)
→ 통합 뷰 또는 데이터 일원화 필요
```

### 2.3 가이던스/EPS/컨센서스 데이터

| 필드 | 입력된 기업 | 총 건수 | 비고 |
|:---|:---|:---:|:---|
| `guidance_next_q` | NVIDIA(1), KIOXIA(1) | 2건 | 전체의 0.3% |
| `eps_actual` | NVIDIA만 일부 | 극소 | 대부분 미입력 |
| `consensus_revenue` | NVIDIA, GOOGLE 등 8사 | ~180건 | P0 기업에만 존재 |

### 2.4 `entity_strategy` 테이블 — 완전 비어 있음

- 테이블 스키마는 존재 (10개 컬럼)
- **데이터 0건** — 기업별 전략 차원 분석이 전혀 적재되지 않음
- 요건정의서에서 정의된 기능(#9)이 미구현 상태

### 2.5 비상장 8사 + ASML 실적 0건

| 기업 | 레이어 | 사유 |
|:---|:---|:---|
| ANTHROPIC | L1 | 비상장, 재무 비공개 |
| OPENAI | L1 | 비상장, 재무 비공개 |
| COREWEAVE | L2 | 2025 IPO, 일부 분기만 공개 |
| NEBIUS | L2 | 최근 독립, 데이터 희소 |
| **ASML** | **L4** | **상장사임에도 실적 0건 — 적재 누락** ⚠️ |
| SPACEX/xAI | L7 | 비상장, 재무 비공개 |
| SOFTBANK | L7 | 상장사이지만 미적재 ⚠️ |
| SCHNEIDER | L8 | 상장사이지만 미적재 ⚠️ |

> [!IMPORTANT]
> **ASML, SOFTBANK, SCHNEIDER**는 상장사로 실적 데이터 확보 가능. 특히 ASML은 L4 파운드리 장비의 핵심 기업으로 분석에 필수적. 우선 적재 필요.

---

## 3. 🟡 시스템 아키텍처 고민 사항

### 3.1 대시보드 재생성 체계의 취약성

현재 아키텍처:
```
DB 변경 → python3 scripts/generate_*.py → dashboard/*.html 재생성
```

**문제점**:
- 생성 스크립트 3개가 빈 파일 (§1.1)
- 각 대시보드가 독자적으로 DB 데이터를 JSON으로 인라인 임베딩 → **DB 변경 시 모든 대시보드를 개별 재생성해야 함**
- 재생성 순서나 의존성 관리가 없음 (Makefile, 마스터 스크립트 부재)

**개선 방향**:
```bash
# 제안: 마스터 재생성 스크립트
# scripts/regenerate_all_dashboards.py
python3 scripts/export_earnings_data.py        # 공통 JSON 생성
python3 scripts/export_quality_scorecard.py     # 품질 데이터
python3 scripts/export_capex_waterfall.py       # Capex 데이터
python3 scripts/generate_entity_one_pager.py --all  # 원페이저 전체
# ... 각 대시보드 재생성
```

### 3.2 데이터 적재 경로의 비일관성

현재 실적 데이터 적재 경로가 복수 존재:

| 스크립트 | 대상 | 데이터 소스 | 비고 |
|:---|:---|:---|:---|
| `populate_quarterly_earnings.py` | 초기 7사 | 수동 하드코딩 | 초기 구축용 |
| `populate_p0_sec_earnings.py` | P0 7사 추가 | SEC API + 수동 | 공시 기반 |
| `populate_p1_sec_earnings.py` | P1 21사 | SEC API + 수동 | 공시 기반 |
| `populate_bookmark_intelligence.py` | 계약/캐파 | 북마크 URL 기반 | 뉴스 기반 |

→ **통합 적재 파이프라인이 없어** 어떤 스크립트가 어떤 데이터를 담당하는지 추적이 어려움. 향후 데이터 추가 시 혼란 예상.

### 3.3 환율 관리 미완성

- SK하이닉스: `fx_rate` 필드에 26분기 모두 입력 ✅
- 삼성전자: `fx_rate` 미확인 (동일 KRW/USD 환율 적용 필요)
- TSMC: TWD/USD 환율 미입력
- KIOXIA: JPY/USD 환율 미입력
- **별도 `fx_rates` 테이블 미생성** — 환율 히스토리 중앙 관리 없음

### 3.4 `financials` vs `earnings_reports` 이원화

| 테이블 | 용도 | 현재 건수 |
|:---|:---|:---:|
| `earnings_reports` | 분기 실적 (매출, OPM, Capex 등) | 658건 |
| `financials` | 연간 KPI (Capex, HBM_REVENUE 등) | 33건 |

**문제**: Capex가 두 테이블에 분산. 쿼리 시 `UNION` 또는 `LEFT JOIN`이 필요하여 복잡도 증가. 장기적으로 하나의 인터페이스로 통합하거나 뷰를 통한 추상화 필요.

---

## 4. 🟡 대시보드/시각화 고민 사항

### 4.1 대시보드 간 네비게이션 불완전

| 대시보드 | 다른 대시보드로의 링크 | 상태 |
|:---|:---|:---|
| index.html | → sankey, layer_capital, network, overlay | ✅ |
| multi_company_overlay.html | → index, network, hbm | ✅ |
| network_graph.html | → index, overlay, hbm | ✅ |
| hbm_market_balance.html | → index, overlay, network | ✅ |
| **data_quality.html** | → ? | ⚠️ 미확인 |
| **capex_waterfall.html** | → ? | ⚠️ 미확인 |
| layer_capital_absorption.html | 0바이트 | 🔴 깨짐 |

신규 대시보드 2종(data_quality, capex_waterfall)이 기존 네비게이션 체계에 연결되어 있는지 확인 필요.

### 4.2 대시보드 데이터 갱신 시점 표시 없음

현재 대시보드에 **"이 데이터는 언제 기준인가"** 표시가 없음. 사용자가 보는 차트의 데이터가 최신인지 알 수 없음.

**개선**: 대시보드 하단에 `Last Updated: 2026-09-17 10:09` 같은 타임스탬프 추가.

### 4.3 모바일 대응 미비

모든 대시보드가 1985px 뷰포트 기준으로 설계. 태블릿이나 모바일에서 접근 시 레이아웃이 깨질 가능성 높음.

---

## 5. 🟡 분석 보고서 / 문서 고민 사항

### 5.1 문서 과다 — 42개 파일, 정리 필요

`docs/` 디렉터리에 42개 파일이 있으며, 날짜별로 정렬되나 **역할별 분류가 없음**:

```
docs/
├── 2026-09-10_*.md   (11개) — 초기 설계/기획 문서
├── 2026-09-11_*.md   (8개)  — 구현/검증 보고서
├── 2026-09-13_*.md   (2개)  — 감사/타당성 분석
├── 2026-09-16_*.md   (12개) — 시각화/분석/확장
├── 2026-09-17_*.md   (5개)  — 뉴스 인텔리전스/제안
├── ask.md, human.md, requirements_spec.md, ...
└── generated/        — 자동 생성 보고서
```

**개선 제안**: 하위 폴더 분류 또는 INDEX.md 작성
```
docs/
├── design/       — 요건정의서, 아키텍처, 로드맵
├── analysis/     — 심층 분석 보고서 (ROAI, HBM 삼국지 등)
├── operations/   — 데이터 적재 보고서, 감사 결과
├── proposals/    — 기능 제안서, 확장 계획
└── generated/    — 자동 생성 (원페이저, 브리핑)
```

### 5.2 원페이저(`entity_profiles/`)의 자동 갱신 주기 미정

`generate_entity_one_pager.py`로 생성된 원페이저가 **DB 변경 시 자동으로 갱신되지 않음**. 데이터를 추가한 후 원페이저가 구버전 데이터를 보여줄 위험.

### 5.3 분석 보고서의 데이터 스냅샷 의존성

- [2026-09-16_hyperscaler_ai_capex_and_roai_analysis.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-16_hyperscaler_ai_capex_and_roai_analysis.md) — 작성 시점의 스냅샷으로 고정
- DB가 업데이트되어도 보고서 내 수치는 변하지 않음
- **"이 보고서는 2026-09-16 기준 데이터입니다"** 같은 명시적 스냅샷 표기 필요

---

## 6. 🟣 99.raw 비정형 데이터와 RAG(검색 증강 생성) 도입 타당성 검토

### 6.1 검토 배경 및 현재 `99.raw/`의 상황

`99.raw/`는 AGENTS.md에서 규정한 **[절대 보호 구역]** 원본 금고로, 현재 총 33개의 1차 원천 파일이 보관되어 있습니다:

- **SEC Company Facts JSON (21개)**: Intel, AMD, Broadcom, Micron, ASML, Vertiv, Eaton 등 주요 기업 SEC 공시 원문
- **HTML 웹페이지/컨콜 요약 (5개)**: TSMC 컨콜 정리, 구글/엔비디아 실적 발표 분석, 반도체 A/S 리포트 등
- **증권사/SNS 리포트 스크랩 (3개)**: 바클레이즈 돈 복사 구조 리포트, 노무라 2030 메모리 $3.7T 전망, MS DC 확장 계획
- **북마크 인덱스 (4개)**: `bookmarks_index.json` (계약, 캐파, 마일스톤, 전략 출처 링크)
- **수기 메모 (1개)**: `manual.md` (인텔-하이닉스 계약 및 추가 아이디어 메모)

**현재 구조의 한계**:
1. **정성적 컨텍스트 증발 (Qualitative Context Loss)**: SEC 주석, 컨퍼런스콜 경영진 질의응답(Q&A), 애널리스트 코멘트 등 핵심 뉘앙스가 SQLite의 정형 수치(매출, OPM)로 추출·축약되는 과정에서 사라집니다.
2. **원문 역추적 및 인용 불가 (Grounding & Provenance Gap)**: 대시보드나 AI 브리핑에서 특정 수치나 가이던스를 제시할 때 "어느 문서 몇 페이지/몇 번째 단락에 근거했는가"를 실시간으로 직접 인용하지 못합니다.
3. **신규 문서 적재 병목**: `99.raw`에 새 리포트나 공시가 들어와도 일일이 수동 파싱 스크립트(`populate_*.py`)를 작성해야만 DB에 반영됩니다.

---

### 6.2 RAG 도입의 필요성 및 기대 효과 (Why RAG?)

| 구분 | 현재 (SQL 단독) | RAG 도입 후 (하이브리드) | 가치 및 기대 효과 |
|:---|:---|:---|:---|
| **질의 범위** | 정량 수치만 조회 가능<br>(예: "SK하이닉스 2026-Q2 OPM은?") | 정량 수치 + 정성적 배경 결합<br>(예: "하이닉스 OPM 급등의 원인과 컨콜 발언은?") | 단순 데이터베이스를 넘어선 **입체적 인텔리전스 시스템**으로 진화 |
| **근거 제시** | DB 수치만 출력 (출처 추적 수동) | `99.raw/` 원문 발췌문과 페이지/링크를 직접 인용 (Grounding) | 분석의 신뢰도 및 감사 추적성(Audit Lineage) 극대화 |
| **비정형 발굴** | HTML/PDF 본문 내 정성적 계약·협력 정황 방치 | "HBM4 베이스 다이 TSMC 협력 조건" 등 비정형 텍스트 즉시 검색 | 숨겨진 전략적 인텔리전스 회수 |
| **DB 적재 보조** | 개발자가 직접 문서를 읽고 정규식 작성 | 원문 문서를 읽고 DB 스키마에 맞는 INSERT 쿼리 자동 초안 생성 | 데이터 수집/적재 파이프라인의 획기적 속도 향상 |

---

### 6.3 리스크 및 기술적 제약사항 (Trade-offs & Constraints)

1. **🔒 `99.raw/` 절대 보호 정책 준수 (Critical)**
   - `99.raw/` 내부에 벡터 DB 파일(예: `.chroma/`, `faiss.index`)이나 가공된 캐시 파일을 생성하는 것은 **엄격히 금지**되어야 합니다.
   - **원칙**: `99.raw/`는 오직 Read-Only 입력 소스로만 사용하며, 임베딩 인덱스 및 전처리 텍스트는 반드시 **`data/rag_index/` 또는 별도 격리 디렉터리에 저장**해야 합니다.

2. **오버엔지니어링 경계 (현재 파일 규모 33건)**
   - 현재 문서 수가 33건으로 아직 수천~수만 건 수준이 아닙니다.
   - 무거운 분산 벡터 DB(Pinecone, Milvus, Qdrant 클라우드 등)나 복잡한 LangChain 파이프라인을 구축하는 것은 과도한 인프라 낭비(Over-engineering)입니다.
   - **권장**: 로컬 파일 기반 경량 벡터 스토어(**SQLite-vec**, **ChromaDB 로컬**, 또는 **BM25 + 임베딩 하이브리드**)로 가볍게 시작해야 합니다.

3. **이종 포맷 파싱 및 전처리 복잡도**
   - 포맷이 제각각입니다: SEC JSON(대용량 계층형 키-값), 네이버 블로그/X HTML(불필요한 태그/스크립트 다수), PDF 리포트(표/도표 파싱 필요).
   - 단순 무지성 텍스트 청킹 시 노이즈(HTML boilerplate, 네비게이션 메뉴 등)가 대량 인덱싱될 위험이 있어, **포맷별 전처리 클리너(Cleaner)** 구축이 선행되어야 합니다.

---

### 6.4 권장 아키텍처 및 3단계 도입 로드맵

```
[99.raw/ 원천 금고] (Read-Only)
   ├── HTML/PDF/MD/JSON
         │
         ▼ (텍스트 정제 & 파싱)
[scripts/build_raw_index.py]
         │
         ▼ (임베딩 생성: bge-m3 또는 text-embedding-3-small)
[data/rag_index/] (격리 저장소)
         │
         ├── ChromaDB / SQLite-vec (벡터 검색)
         └── FTS5 / BM25 (키워드 검색)
         │
         ▼
[하이브리드 인텔리전스 엔진 (Memory Claude)]
   ├── 쿼리 A (수치): SQLite SQL 실행 (earnings_reports, contracts)
   └── 쿼리 B (맥락): RAG 원문 검색 (99.raw 스니펫 인용)
```

#### 📍 Phase 1: 경량 로컬 RAG 파이프라인 구축 (PoC)
- **대상**: `99.raw/` 내 HTML 및 MD 파일 (블로그 컨콜 정리, 리포트 요약 등 정성 문서 중심)
- **엔진**: SQLite 기본 FTS5 (전문 검색) + 로컬 ChromaDB (Sentence-Transformers 또는 OpenAI 임베딩)
- **산출물**:
  - `scripts/build_raw_rag_index.py` (원문 읽기 → 텍스트 정제 → `data/rag_index/`에 적재)
  - `scripts/query_raw_rag.py` (키워드/의미 기반 원문 검색 및 발췌 스니펫 출력)

#### 📍 Phase 2: 정량(SQL) + 정성(RAG) 통합 브리핑 체계
- 사용자의 질문에 대해:
  1. SQL 쿼리로 확정 수치(매출, OPM, 계약 규모)를 조회
  2. RAG로 해당 분기/기업의 컨콜 발언 및 애널리스트 코멘트 발췌
  3. 두 정보를 융합하여 완결된 브리핑 리포트 출력

#### 📍 Phase 3: 신규 문서 자동 정보 추출(Information Extraction) 파이프라인
- 사용자가 `99.raw/`에 새 PDF/HTML을 투입하면:
  1. RAG 파이프라인이 문서를 자동 분석
  2. 주요 정량 수치(Capex, 매출, 신규 계약, 마일스톤)를 자동 추출
  3. `scripts/add_earnings.sql` 형태의 DB 적재 초안 스크립트를 사용자 승인용으로 생성

---

### 6.5 검토 결론: "단계적 도입 적극 권장 (중기 P2 과제)"

- **최종 결론**: **`99.raw/` 대상 RAG 추가는 프로젝트의 본질적 목표("2026~2028년 자본 및 기술 흐름 예측")를 달성하는 데 매우 강력하고 유효한 도구**입니다.
- 단, `99.raw/`의 원본 무결성을 해치지 않도록 **격리된 인덱스 저장(`data/rag_index/`)** 원칙을 철저히 준수하고, 거창한 클라우드 DB 대신 **로컬 경량 하이브리드 파이프라인(Phase 1)**부터 시작할 것을 권장합니다.

---

## 7. 🟢 장기적으로 고민할 사항

### 7.1 데이터 검증 자동화 부재

현재 데이터 입력 후 검증은 수동(SQL 쿼리로 확인). 자동 검증이 없으므로:
- 환율 환산 오류 감지 불가
- 분기 표기 오류 (예: "2024Q3" vs "2024-Q3") 감지 불가
- 매출이 음수이거나 OPM이 100% 초과인 이상치 감지 불가

**제안**: `scripts/validate_data_integrity.py` — 기본 무결성 검사 자동화

### 7.2 백업 전략 없음

`data/memory_claude.db`는 프로젝트의 핵심 자산이지만:
- 버전 관리 (git) 여부 불명
- 정기 백업 스크립트 없음
- DB 손상 시 복구 절차 미정의

### 7.3 뉴스 인텔리전스 레이어 — 설계만 완료

4개의 설계/요건 문서가 작성되었으나 **구현 코드는 0줄**:
- `analyze_news_impact.py` 미생성
- `generate_news_watchlist.py` 미생성
- 설계 문서의 구체적인 SQL 쿼리는 즉시 활용 가능

### 7.4 대시보드 서빙 의존성

`scripts/serve_dashboard.py`로 로컬 서버를 띄워야 CORS 없이 동작하는 대시보드가 있을 수 있음. 그러나 대부분은 `file://` 프로토콜로 직접 열기 가능한 **self-contained HTML**. 어떤 대시보드가 서버 의존인지 명확하지 않음.

### 7.5 시스템의 궁극적 질문에 대한 답변 경로

> *"하이퍼스케일러의 초대형 AI Capex와 기업 간 장기 공급 계약은 2026~2028년 메모리 및 파운드리, AI 가속기 시장의 업황을 어떻게 결정짓는가?"*

이 핵심 질문에 답하기 위해 아직 부족한 데이터:

| 필요 데이터 | 현재 상태 | 갭 |
|:---|:---|:---|
| 하이퍼스케일러 5사 연간 Capex 시계열 | financials에 33건 | 분기별 데이터 없음 |
| Capex → 각 레이어 배분 비율 | 계약 15건에서 부분 추정 | L6/L7/L8 방향 계약 0건 |
| HBM 출하량 & ASP | fab_capacity에서 간접 추정 | 정확한 분기별 출하량 없음 |
| 2027~2028년 전망치 | milestones에 일부 | 체계적 시나리오 모델 미구축 |

---

## 8. 우선순위 정리 (실행 순서 제안)

### 🔴 즉시 (1~2시간)

1. `layer_capital_absorption.html` 재생성 (0바이트 복구)
2. 생성 스크립트 3개 재작성 또는 백업 복원
3. 구버전 `2026-09-11_sankey_scenario.html` 정리

### 🟠 단기 (반나절)

4. 7대 핵심 기업 OPM 2020-Q1 ~ 2025-Q1 소급 입력 (약 140건)
5. ASML 실적 26분기 적재 (상장사, SEC/IR 데이터 확보 용이)
6. Capex 데이터 일원화 (earnings_reports vs financials 통합 뷰)
7. 대시보드 간 네비게이션 완전 연결

### 🟡 중기 (1~3일)

8. 데이터 무결성 자동 검증 스크립트
9. 마스터 대시보드 재생성 스크립트 (`regenerate_all.sh`)
10. `entity_strategy` 테이블 초기 데이터 적재
11. `docs/` 디렉터리 구조 재정리
12. 뉴스 인텔리전스 Stage 1 구현 착수
13. **`99.raw/` 경량 RAG PoC 구축 (Phase 1: 텍스트 추출 + 로컬 벡터 인덱스)**

### 🟢 장기 (1주+)

14. SOFTBANK, SCHNEIDER 실적 적재
15. 환율 테이블 중앙화 (`fx_rates`)
16. DB 백업 자동화
17. 2027~2028 시나리오 모델 체계화
18. **정량 SQL + RAG 하이브리드 질의응답 및 DB 자동 적재 파이프라인 완성 (Phase 2~3)**

