# [구현 계획도] Memory Claude 단계별 실행 로드맵
**문서 버전**: v1.0.0  
**작성일자**: 2026-09-10  
**프로젝트 코드명**: `b_0910_memory_claude`

---

## 1. 전체 구현 조감도

설계 문서 9개를 **실제 동작하는 시스템**으로 전환하는 전체 로드맵입니다.

```mermaid
graph TD
    subgraph NOW ["📄 현재 상태 (설계만 존재)"]
        DOCS["문서 9개<br/>코드 0줄 · 데이터 0건<br/>가치 = 0"]
    end

    subgraph P0 ["⚡ Phase 0: 가치 0→1 (15분)"]
        DIR["99.raw/ 디렉터리 생성"]
        DB["SQLite DB + 5개 테이블"]
        SEED["시드 데이터 투입<br/>16~21개사 + 3개 계약"]
    end

    subgraph P1 ["🧱 Phase 1: 기초 데이터 (2주)"]
        MANUAL["수기 데이터 대량 투입<br/>Capex · 실적 · 계약"]
        TABLE1["실적 매트릭스 테이블<br/>첫 버전 수동 생성"]
    end

    subgraph P2 ["🔧 Phase 2: 자동화 (1개월)"]
        API["SEC/DART API 자동 수집"]
        VALID["validator.py<br/>99.raw → SQLite 자동 정제"]
        GEN["generate_tables.py<br/>마크다운 테이블 자동 생성"]
    end

    subgraph P3 ["🎨 Phase 3: 시각화 (2개월)"]
        CANVAS["옵시디언 캔버스 자동 생성"]
        MERMAID["Mermaid 다이어그램"]
        CHART["SVG 차트 이미지"]
        FAB["Fab Capacity 데이터 입력"]
    end

    subgraph P4 ["🌐 Phase 4: 웹 대시보드 (3~6개월)"]
        SANKEY["Sankey 자본 흐름도"]
        SLIDER["타임라인 슬라이더"]
        SIM["병목 시뮬레이터"]
        FACT["기업 팩트시트"]
    end

    subgraph P5 ["🤖 Phase 5: 인텔리전스 (6~12개월)"]
        LLM["어닝콜 LLM 요약"]
        ALERT["뉴스 알림 봇"]
        CORR["상관관계 엔진"]
        AGENT["AI 에이전트 통합"]
    end

    NOW -->|"15분"| P0
    P0 -->|"2주"| P1
    P1 -->|"1개월"| P2
    P2 -->|"2개월"| P3
    P3 -->|"3~6개월"| P4
    P4 -->|"6~12개월"| P5
```

---

## 2. Phase 0 상세: 가치가 0에서 1로 바뀌는 순간

### 2.1 현재 vs Phase 0 완료 후

```mermaid
flowchart LR
    subgraph BEFORE ["❌ 현재 (설계만 존재)"]
        B1["docs/ 문서 9개"]
        B2["코드 0줄"]
        B3["데이터 0건"]
        B4["가치 = 0"]
    end

    subgraph AFTER ["✅ Phase 0 완료 (15분 후)"]
        A1["docs/ 문서 9개"]
        A2["99.raw/ 디렉터리 4개"]
        A3["memory_claude.db<br/>5개 테이블 + 시드"]
        A4["데이터 넣을 수 있는 상태"]
    end

    BEFORE -->|"15분 실행"| AFTER
```

### 2.2 Phase 0 실행 체크리스트

| 순서 | 작업 | 명령/내용 | 소요 | 결과물 |
| :---: | :--- | :--- | :---: | :--- |
| **0-1** | 99.raw/ 폴더 구조 생성 | `mkdir -p 99.raw/{contracts,financials,milestones,fab_capacity}` | 1분 | 빈 디렉터리 4개 |
| **0-2** | data/ 폴더 생성 | `mkdir -p data` | 1분 | DB 저장 위치 |
| **0-3** | scripts/ 폴더 생성 | `mkdir -p scripts` | 1분 | 스크립트 저장 위치 |
| **0-4** | SQLite DB 생성 + DDL 실행 | `sqlite3 data/memory_claude.db < scripts/init_db.sql` | 2분 | 빈 5개 테이블 |
| **0-5** | entities 시드 INSERT | 16~21개사 기업 마스터 데이터 | 5분 | 기업 식별 코드 체계 |
| **0-6** | contracts 시드 INSERT | human.md 계약 3건 (구글-앤트로픽 $200B 등) | 3분 | 첫 계약 데이터 |
| **0-7** | financials 시드 INSERT | 구글 Capex $76.7B | 2분 | 첫 실적 데이터 |
| | **합계** | | **15분** | |

### 2.3 Phase 0 파일 트리 (완료 후)

```text
b_0910_memory_claude/
├── docs/                              ← 설계 문서 (기존)
│   ├── human.md
│   ├── requirements_spec.md
│   ├── db_architecture.md
│   ├── data_sources.md
│   └── 2026-09-10_*.md (5개)
│
├── 99.raw/                            ← ✅ 신규 생성
│   ├── contracts/                     ← 수기 계약 데이터 입력
│   │   └── contracts.csv              ← 시드 3건
│   ├── financials/                    ← 수기 실적 데이터 입력
│   │   └── financials.csv             ← 시드 1건
│   ├── milestones/                    ← 수기 이벤트 입력
│   │   └── (빈 템플릿)
│   └── fab_capacity/                  ← 수기 Fab 데이터 입력
│       └── (빈 템플릿)
│
├── data/                              ← ✅ 신규 생성
│   └── memory_claude.db               ← SQLite DB (5개 테이블 + 시드)
│
└── scripts/                           ← ✅ 신규 생성
    └── init_db.sql                    ← DDL + 시드 데이터
```

---

## 3. Phase 1~5 상세 계획

### Phase 1: 기초 데이터 축적 (2주)

```mermaid
flowchart TD
    subgraph 입력 ["사용자 수기 작업"]
        M1["하이퍼스케일러 4사<br/>2024~2026 Capex 입력"]
        M2["엔비디아·TSMC·삼성<br/>3개년 실적 입력"]
        M3["주요 계약 10건<br/>금액·기간·유형 입력"]
        M4["과거 마일스톤 15건<br/>2023~2025 사건 입력"]
    end

    subgraph 산출 ["첫 번째 산출물"]
        T1["financials_matrix_table.md<br/>(수동 생성, 첫 버전)"]
        T2["past_timeline_table.md<br/>(수동 생성, 첫 버전)"]
    end

    M1 & M2 --> T1
    M3 & M4 --> T2
```

**Phase 1 완료 기준**: DB에 **실적 30건 + 계약 10건 + 마일스톤 15건** 이상 축적. 첫 번째 테이블이 옵시디언에서 열람 가능.

---

### Phase 2: 자동화 파이프라인 (1개월)

```mermaid
flowchart LR
    subgraph SCRIPTS ["scripts/ 개발"]
        S1["validator.py<br/>99.raw/ CSV·MD 파싱<br/>→ SQLite 자동 적재"]
        S2["fetch_sec.py<br/>SEC EDGAR API<br/>→ 미국 상장사 실적 자동 수집"]
        S3["fetch_dart.py<br/>DART API<br/>→ 삼성전자 실적 자동 수집"]
        S4["generate_tables.py<br/>SQLite → 마크다운 테이블<br/>자동 생성"]
    end

    RAW["99.raw/<br/>수기 데이터"] --> S1
    API["SEC / DART<br/>API"] --> S2 & S3
    S1 & S2 & S3 --> DB[("memory_claude.db")]
    DB --> S4 --> MD["docs/*.md<br/>테이블 자동 갱신"]
```

**Phase 2 완료 기준**: `python3 scripts/validator.py && python3 scripts/generate_tables.py` 한 줄로 **99.raw/ → DB → 마크다운 테이블** 전체 파이프라인 자동 실행.

---

### Phase 3: 시각화 & Fab 데이터 (2개월)

```mermaid
flowchart TD
    DB[("memory_claude.db")] --> GC["generate_canvas.py"]
    DB --> GD["generate_diagrams.py"]
    DB --> GI["generate_charts.py"]

    GC --> CANVAS["ecosystem.canvas<br/>옵시디언 캔버스"]
    GD --> MERM["diagrams.md<br/>Mermaid 관계도"]
    GI --> SVG["charts/*.svg<br/>Capex 바차트<br/>HBM 점유율 파이"]

    FAB["Fab Capacity<br/>TSMC·삼성·SK 팹 데이터 입력"] --> DB
    FAB_TABLE["fab_capacity_table.md<br/>증설 로드맵·수율 매트릭스"] --> OBSIDIAN["옵시디언 볼트"]

    CANVAS & MERM & SVG --> OBSIDIAN
```

**Phase 3 완료 기준**: 옵시디언을 열면 **캔버스(기업 네트워크) + 다이어그램(관계도) + 차트(Capex 추이) + Fab 테이블(증설 로드맵)**이 즉시 열람 가능.

---

### Phase 4: 웹 대시보드 (3~6개월)

```mermaid
flowchart TD
    DB[("memory_claude.db")] --> GW["generate_web.py<br/>DB → data.json"]
    GW --> JSON["web/data.json"]

    JSON --> WEB["web/index.html"]

    subgraph SCREENS ["4대 핵심 화면"]
        SC_A["화면 A<br/>자본 흐름 Sankey<br/>(D3.js)"]
        SC_B["화면 B<br/>타임라인 슬라이더<br/>(2023~2028)"]
        SC_C["화면 C<br/>병목 시뮬레이터<br/>(시나리오 토글)"]
        SC_D["화면 D<br/>기업 팩트시트<br/>(클릭 팝업)"]
    end

    subgraph FAB_SCREENS ["Fab 확장 화면"]
        SC_F["화면 F<br/>Fab 증설 타임라인"]
        SC_G["화면 G<br/>수율×캐파 매트릭스"]
    end

    WEB --> SCREENS
    WEB --> FAB_SCREENS
```

**기술 스택**: HTML5 + Vanilla CSS (다크모드 네온) + Vanilla JS + D3.js (Sankey) + Chart.js

---

### Phase 5: 인텔리전스 자동화 (6~12개월)

```mermaid
flowchart TD
    subgraph AUTO ["자동 인텔리전스"]
        LLM["어닝콜 LLM 자동 요약<br/>Claude API"]
        NEWS["뉴스 알림 봇<br/>Google RSS + 자동 분류"]
        CORR["상관관계 엔진<br/>선행·후행 지표 식별"]
    end

    subgraph QUALITY ["데이터 품질"]
        CONF["Confidence 등급(C1~C5)<br/>전 테이블 반영"]
        RANGE["범위(low/mid/high)<br/>불확실성 시각화"]
        REV["변경 이력 추적<br/>data_revisions 테이블"]
    end

    subgraph FUTURE ["장기 진화"]
        AGENT["AI 에이전트<br/>자연어 → DB 조회 → 답변"]
        SECTOR["섹터 확장<br/>바이오·에너지·방산"]
        COMMUNITY["오픈소스·협업<br/>커뮤니티 인텔리전스"]
    end

    AUTO --> DB[("memory_claude.db")]
    DB --> QUALITY
    QUALITY --> FUTURE
```

---

## 4. Phase별 투입 시간 & 누적 가치

```mermaid
gantt
    title Memory Claude 구현 타임라인
    dateFormat  YYYY-MM
    axisFormat  %Y-%m

    section Phase 0 (15분)
    디렉터리 + DB + 시드         :done, p0, 2026-09, 2026-09

    section Phase 1 (2주)
    수기 데이터 대량 투입         :p1a, 2026-09, 2026-10
    실적 매트릭스 첫 버전         :p1b, 2026-10, 2026-10

    section Phase 2 (1개월)
    SEC/DART API 자동 수집        :p2a, 2026-10, 2026-11
    validator.py + 테이블 생성기  :p2b, 2026-10, 2026-11

    section Phase 3 (2개월)
    옵시디언 캔버스·차트 자동     :p3a, 2026-11, 2026-12
    Fab Capacity 데이터 1차       :p3b, 2026-11, 2026-12

    section Phase 4 (3~6개월)
    Sankey + 타임라인 웹 MVP      :p4a, 2026-12, 2027-02
    병목 시뮬레이터 + 팩트시트    :p4b, 2027-01, 2027-03

    section Phase 5 (6~12개월)
    LLM 어닝콜 + 뉴스 알림       :p5a, 2027-03, 2027-06
    상관관계 + AI 에이전트        :p5b, 2027-06, 2027-09
```

---

## 5. 각 Phase 완료 시 시스템 상태 비교

```mermaid
graph LR
    subgraph P0_STATE ["Phase 0 완료"]
        P0S["빈 DB + 시드 4건<br/>데이터 입력 가능 상태"]
    end

    subgraph P1_STATE ["Phase 1 완료"]
        P1S["DB에 55건+<br/>첫 번째 테이블 2개<br/>옵시디언에서 열람"]
    end

    subgraph P2_STATE ["Phase 2 완료"]
        P2S["API 자동 수집<br/>99.raw → DB → MD<br/>원클릭 파이프라인"]
    end

    subgraph P3_STATE ["Phase 3 완료"]
        P3S["옵시디언 풀 연동<br/>캔버스+차트+Fab<br/>볼트가 살아있음"]
    end

    subgraph P4_STATE ["Phase 4 완료"]
        P4S["웹 대시보드 가동<br/>Sankey+슬라이더<br/>인터랙티브 분석"]
    end

    subgraph P5_STATE ["Phase 5 완료"]
        P5S["AI 자동 인텔리전스<br/>알림+요약+예측<br/>나만의 블룸버그"]
    end

    P0_STATE -->|"+2주"| P1_STATE -->|"+1개월"| P2_STATE -->|"+2개월"| P3_STATE -->|"+3개월"| P4_STATE -->|"+6개월"| P5_STATE
```

---

## 6. 설계 문서 → 구현 매핑

지금까지 작성한 **문서 9개**가 어느 Phase에서 실현되는지:

```mermaid
flowchart TD
    subgraph DOCS ["📄 설계 문서 9개"]
        D1["1. 요건정의서"]
        D2["2. DB 아키텍처"]
        D3["3. 데이터 소스"]
        D4["4. 아웃풋 정의서"]
        D5["5. 기업 확장 검토"]
        D6["6. 추가 제안"]
        D7["7. Fab Capacity"]
        D8["8. 정량화 방법론"]
        D9["9. 가치 및 방향성"]
    end

    subgraph IMPL ["🔨 구현 Phase"]
        P0["Phase 0<br/>DB 생성"]
        P1["Phase 1<br/>데이터 축적"]
        P2["Phase 2<br/>자동화"]
        P3["Phase 3<br/>시각화"]
        P4["Phase 4<br/>웹 대시보드"]
        P5["Phase 5<br/>인텔리전스"]
    end

    D1 -->|"전체 로드맵"| P0 & P1 & P2 & P3 & P4
    D2 -->|"DDL + 시드"| P0
    D3 -->|"API 스크립트"| P2
    D4 -->|"산출물 생성"| P2 & P3 & P4
    D5 -->|"entities 확장"| P1
    D6 -->|"LLM·알림·히트맵"| P5
    D7 -->|"fab_capacity 테이블"| P3
    D8 -->|"confidence·range"| P5
    D9 -->|"전략 가이드"| P0 & P1 & P2 & P3 & P4 & P5
```

---

## 7. Phase 0 실행 판단 기준

**Phase 0을 지금 실행해야 하는 이유:**

| 질문 | 답변 |
| :--- | :--- |
| 추가 설계가 필요한가? | ❌ 문서 9개로 충분. 더 쓰면 과잉 설계 |
| 기술적 위험이 있는가? | ❌ SQLite + 폴더 생성. 실패 가능성 0% |
| 되돌릴 수 있는가? | ✅ 언제든 삭제 가능. 비가역적 작업 없음 |
| 선행 조건이 있는가? | ❌ 없음. 지금 바로 가능 |
| 소요 시간은? | **15분** |

```mermaid
flowchart LR
    Q1{"추가 설계<br/>필요한가?"} -->|"아니오"| Q2{"기술 위험<br/>있는가?"}
    Q2 -->|"아니오"| Q3{"되돌릴 수<br/>있는가?"}
    Q3 -->|"예"| Q4{"소요 시간은?"}
    Q4 -->|"15분"| GO["✅ 지금 실행"]
```

---

## 8. Phase 0 실행 시 구체적 명령어

```bash
# 0-1. 디렉터리 구조 생성
mkdir -p 99.raw/{contracts,financials,milestones,fab_capacity}
mkdir -p data
mkdir -p scripts
mkdir -p web

# 0-2. DDL + 시드 SQL 작성 → 실행
sqlite3 data/memory_claude.db < scripts/init_db.sql

# 0-3. 확인
sqlite3 data/memory_claude.db ".tables"
# 출력: contracts  entities  fab_capacity  financials  milestones

sqlite3 data/memory_claude.db "SELECT count(*) FROM entities;"
# 출력: 21  (21개사 시드)

sqlite3 data/memory_claude.db "SELECT * FROM contracts;"
# 출력: 구글-앤트로픽, 아마존-앤트로픽, 오픈AI-아마존 3건
```

> **다음 단계**: Phase 0 실행 승인 시, `scripts/init_db.sql` 작성 → 실행 → 확인까지 즉시 진행합니다.
