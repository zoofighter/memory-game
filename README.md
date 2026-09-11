# Memory Claude (b_0910_memory_claude)

> **AI · 반도체 밸류체인의 자본 · 기술 흐름 추적 및 미래 업황 예측 시스템**

---

## 📌 1. 프로젝트 개요

**Memory Claude**는 단편적인 뉴스나 단기 소음에 휘둘리지 않고, 글로벌 빅테크 및 반도체 밸류체인 핵심 기업들의 **정량적 실적(Earnings & Capex), 대규모 공급·투자 계약(Contracts), 캐파(Fab Capacity), 전략적 이정표(Milestones)**를 구조화된 데이터베이스로 축적하여 **2026~2028년 이후의 기술 및 자본 흐름을 예측**하기 위해 구축된 인텔리전스 시스템입니다.

### 핵심 질문
> *"하이퍼스케일러의 천문학적 AI Capex와 기업 간 대규모 공급 계약은 2026~2028년 메모리 및 파운드리, AI 가속기 시장의 업황을 어떻게 결정짓는가?"*

---

## 🏢 2. 추적 대상 기업 (Value Chain)

| 계층 (Layer) | 대상 기업 | 밸류체인 내 핵심 역할 |
| :--- | :--- | :--- |
| **AI Frontier Lab** | **Anthropic, OpenAI** | 프론티어 모델 개발 및 대규모 컴퓨팅 파워 수요 진원지 |
| **Hyperscalers** | **Microsoft, Alphabet (Google), Amazon, Meta, Oracle** | 초대형 AI 인프라 구축 주도 (2024~2026 Capex 집중) |
| **AI Computing** | **NVIDIA** | AI 가속기(GPU/Blackwell/Rubin) 공급 및 생태계 지배 |
| **Foundry & Equipment** | **TSMC, ASML** | 선단공정 독점 파운드리(CoWoS 등) 및 최첨단 EUV 노광장비 |
| **Memory & Storage** | **SK하이닉스, 삼성전자, SanDisk/WDC** | HBM3E/HBM4 공급망, 고용량 DRAM 및 eSSD/NAND |
| **Optical & Interconnect** | **Marvell, Coherent (Novali)** | CPO, 데이터센터 고속 광트랜시버 및 스케일아웃 네트워크 |
| **Infrastructure & Ecosystem** | **SoftBank, SpaceX, Apple** | 온디바이스 AI, 차세대 전력·통신 인프라 및 대형 펀딩 |

---

## 📂 3. 디렉토리 구조

```plaintext
b_0910_memory_claude/
├── README.md                           # 프로젝트 메인 안내서 (본 문서)
├── data/
│   ├── memory_claude.db                # 메인 SQLite 데이터베이스
│   └── memory_claude.sqbpro            # DB Browser for SQLite 프로젝트 설정 파일
├── 99.raw/                             # 1차 원본 데이터(IR, 공시, 기사, PDF) 보관소
│   ├── contracts/                      # 기업 간 계약 및 투자 원문
│   ├── financials/                     # 각 사 실적 발표 자료(PR, 10-Q, IR 프레젠테이션)
│   ├── fab_capacity/                   # 팹 및 패키징 캐파 증설 관련 자료
│   ├── milestones/                     # 주요 기술 로드맵 및 양산 일정
│   └── strategy/                       # 전략 분석 및 산업 리포트
├── docs/                               # 아키텍처, 요건정의 및 분석 산출물
│   ├── requirements_spec.md            # 시스템 요건정의서
│   ├── db_architecture.md              # DB 스키마 및 엔티티 관계 정의
│   ├── data_sources.md                 # 데이터 소스 및 수집 가이드
│   ├── 2026-09-11_data_source_reliability.md # 데이터 소스별 신뢰도 및 교차 검증 정책
│   ├── 2026-09-11_db_query_guide.md    # 주요 분석용 SQL 쿼리 가이드
│   ├── 2026-09-11_report_summary.md    # DB 기반 자동 생성 분석 종합 보고서
│   └── generated/                      # 자동 산출물 보관
└── scripts/                            # DB 적재, 쿼리, 리포트 생성 스크립트
    ├── init_db.sql                     # 코어 스키마 및 기초 데이터 세팅
    ├── add_earnings_table.sql          # 분기 실적 테이블(earnings_reports) DDL
    ├── populate_quarterly_earnings.py  # 2020~2026 분기별 실적 적재 및 갱신 스크립트
    └── export_report.py                # DB 데이터 기반 종합 보고서 마크다운 생성기
```

---

## 🗄️ 4. 데이터베이스 아키텍처

SQLite 기반(`data/memory_claude.db`)으로 경량화 및 독립성을 유지하며, 다음 5대 핵심 엔티티를 관리합니다.

1. **`companies`**: 추적 대상 기업 마스터 (티커, 국적, 밸류체인 계층, 핵심 제품군)
2. **`earnings_reports`**: 2020-Q1 ~ 2026-Q4 분기별 정량 실적
   - 매출액(`revenue_usd_b`), 영업이익(`operating_income_usd_b`), 영업이익률(`operating_margin_pct`)
   - 실적 발표일, 확정 실적/전망 구분(`is_forecast`), 컨센서스 대비 비트/미스(`beat_miss_status`)
   - 세부 매출 비중, 다음 분기 가이던스, 실적콜 핵심 코멘트
3. **`financials`**: 연간/분기별 Capex 및 R&D 지출 추이
4. **`contracts`**: 기업 간 초대형 AI 칩 공급 계약, 클라우드 파트너십, 지분 투자 내역
5. **`fab_capacity` & `milestones`**: TSMC CoWoS, HBM 라인 증설 캐파 및 양산 마일스톤

---

## 🚀 5. 빠른 시작 (Quick Start)

### 1) 사전 준비
- Python 3.9 이상
- [DB Browser for SQLite](https://sqlitebrowser.org/) (GUI 확인 권장)

### 2) 데이터베이스 초기화 및 데이터 적재
```bash
# 1. 코어 테이블 생성 및 기초 데이터 적재
sqlite3 data/memory_claude.db < scripts/init_db.sql

# 2. 분기별 실적 테이블(earnings_reports) 생성
sqlite3 data/memory_claude.db < scripts/add_earnings_table.sql

# 3. 2020-Q1 ~ 2026-Q4 분기 실적 데이터 투입 (8대 핵심 기업 208개 분기)
python3 scripts/populate_quarterly_earnings.py
```

### 3) 분석 보고서 자동 추출
```bash
# DB 최신 데이터를 마크다운 분석 리포트로 내보내기
python3 scripts/export_report.py
```

---

## 🔍 6. 데이터 신뢰도 및 검증 정책

본 프로젝트의 데이터는 **확정 실적(Actuals)**과 **전망치(Forecast)**로 엄격하게 구분됩니다.

- **`is_forecast = 0` (확정 실적)**: 각 사 공식 IR 프레젠테이션, 10-Q/10-K 공시 자료 기준
- **`is_forecast = 1` (전망치)**: 공시된 가이던스 및 컨센서스 기반 시나리오
- **데이터 검증 프로세스**:
  - 상세 내용은 [docs/2026-09-11_data_source_reliability.md](file:///Users/chansoojeon/Library/CloudStorage/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-11_data_source_reliability.md) 참조
  - 1차 수집 자료는 원본 보관소(`99.raw/`)에 저장 후 인덱싱 및 DB 동기화

---

## 📚 7. 주요 문서 인덱스

- [에이전트 운영 지침 (AGENTS.md)](file:///Users/chansoojeon/Library/CloudStorage/Dropbox/03_code/b_0910_memory_claude/AGENTS.md)
- [시스템 요건정의서](file:///Users/chansoojeon/Library/CloudStorage/Dropbox/03_code/b_0910_memory_claude/docs/requirements_spec.md)
- [데이터베이스 구조 설계서](file:///Users/chansoojeon/Library/CloudStorage/Dropbox/03_code/b_0910_memory_claude/docs/db_architecture.md)
- [Fab 생산 캐파 및 마일스톤 심층 분석 보고서](file:///Users/chansoojeon/Library/CloudStorage/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-11_fab_capacity_and_milestones_report.md)
- [데이터 소스 신뢰도 및 검증 가이드](file:///Users/chansoojeon/Library/CloudStorage/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-11_data_source_reliability.md)
- [분석용 쿼리 모음집](file:///Users/chansoojeon/Library/CloudStorage/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-11_db_query_guide.md)
- [종합 리포트 요약본](file:///Users/chansoojeon/Library/CloudStorage/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-11_report_summary.md)
