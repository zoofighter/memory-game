# Memory Claude — 최근 작업 이력 정리 (09-16 ~ 09-17)

**작성일**: 2026-09-17  
**프로젝트 기준 시점**: 2026-09-10  

---

## 09-16 저녁 ~ 09-17 00:51 (세션 1)

| 시간 | 작업 | 유형 | 파일 |
|:---|:---|:---|:---|
| 21:59 | **💾 HBM 수급 분석 대시보드** 신규 구축 | 대시보드 | [dashboard/hbm_market_balance.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/hbm_market_balance.html) |
| 22:00 | multi_company_overlay / network_graph 상호 네비게이션 동기화 | 대시보드 수정 | 4개 대시보드 간 링크 추가 |
| 00:33 | **뉴스 인텔리전스 레이어 설계 문서** 작성 | 설계 문서 | [docs/2026-09-17_news_intelligence_layer_design.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-17_news_intelligence_layer_design.md) |
| 00:42 | **순방향 뉴스 임팩트 분석기 요건정의서** 작성 | 요건정의서 | [docs/2026-09-17_news_impact_analyzer_requirements.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-17_news_impact_analyzer_requirements.md) |
| 00:51 | **추가 가능 기능 13가지 제안서** 작성 | 제안 문서 | [docs/2026-09-17_additional_feature_proposals.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-17_additional_feature_proposals.md) |

## 09-17 10:04 ~ 10:10 (세션 2, 별도 세션에서 추가 구현)

| 시간 | 작업 | 유형 | 파일 |
|:---|:---|:---|:---|
| 10:04 | **📊 데이터 품질 대시보드** 구현 완료 | 대시보드 신규 | [dashboard/data_quality.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/data_quality.html) (32KB) |
| 10:09 | **🏗️ Capex 워터폴 차트** 구현 완료 | 대시보드 신규 | [dashboard/capex_waterfall.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/capex_waterfall.html) (19KB) |
| 10:10 | **3대 핵심 기능 요건정의서** 작성 | 요건정의서 | [docs/2026-09-17_three_features_requirements.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-17_three_features_requirements.md) |

---

## 각 작업 상세 설명

### 1. 💾 HBM 수급 분석 대시보드 (`hbm_market_balance.html`)

- 세대별 ASP 프리미엄 비교 (DDR5 $0.42 → HBM4 $2.85/GB, 6.8x)
- 메모리 3사 2025 시장 점유율 Doughnut (SK하이닉스 63.5%, 삼성 25.4%, 마이크론 11.1%)
- 메모리 3사 분기별 실적 & OPM 추이 (2020-Q1 ~ 2026-Q4)
- **2026~2028 HBM 수급 밸런스 인터랙티브 시뮬레이터** (CoWoS 캐파, 팹 WSPM, 수요 성장률 슬라이더)
- $57B 계약 테이블 + 3사 Fab 캐파 로드맵

### 2. 뉴스 인텔리전스 설계 (`news_intelligence_layer_design.md`)

- **방향 A (순방향)**: 뉴스 입력 → 엔티티 식별 → DB 대조 → 임팩트 분석 (3 Stage)
- **방향 B (역방향)**: DB에서 "봐야 할 뉴스" 자동 발견 (6가지 유형: 실적 미입력, 계약 만료, 마일스톤 도래, 이상치, 데이터 공백, 크로스체크)
- 통합 인텔리전스 루프 설계

### 3. 순방향 분석기 요건정의서 (`news_impact_analyzer_requirements.md`)

- 4가지 사용 시나리오 (실적, 계약, 마일스톤, 복합)
- FR-01~06 기능 요건 (입력, 엔티티 매칭 73별칭, 6종 분류, DB 5테이블 자동 조회, 파급 매트릭스, 리포트 출력)
- 3Stage 구현 계획 + 검증/리스크 분석

### 4. 추가 기능 13가지 제안서 (`additional_feature_proposals.md`)

- A: 데이터 품질(3종), B: 심층 분석(4종), C: 자동 보고서(3종), D: 외부 연동(3종), E: UX 강화(3종)

### 5. 📊 데이터 품질 대시보드 (`data_quality.html`) — 세션 2에서 구현

- 36개사 × 7개 필드의 입력 완결성 히트맵
- 레이어별 필터링, 전체 완결도 스코어

### 6. 🏗️ Capex 워터폴 차트 (`capex_waterfall.html`) — 세션 2에서 구현

- 하이퍼스케일러 $100B Capex의 L3→L4→L5→L6→L8 전파 비율 시각화
- 계약 데이터(contracts) 기반 비율 + 산업 보고서 추정 비율 병행

### 7. 3대 기능 요건정의서 (`three_features_requirements.md`) — 세션 2에서 작성

- 데이터 품질 대시보드, Capex 워터폴, 기업별 원페이저의 상세 요건 정의

---

## 현재 대시보드 현황 (총 8종)

| # | 대시보드 | 파일 | 구축 시점 |
|:---:|:---|:---|:---|
| 1 | 메인 대시보드 | [index.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/index.html) | 09-11 |
| 2 | 자본 흐름 Sankey 시뮬레이터 | [sankey_scenario.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/sankey_scenario.html) | 09-13 |
| 3 | 레이어별 자본 흡수 분석 | [layer_capital_absorption.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/layer_capital_absorption.html) | 09-16 |
| 4 | 밸류체인 의존도 네트워크 | [network_graph.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/network_graph.html) | 09-16 |
| 5 | 멀티 기업 비교 오버레이 | [multi_company_overlay.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/multi_company_overlay.html) | 09-16 |
| 6 | **💾 HBM 수급 분석** | [hbm_market_balance.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/hbm_market_balance.html) | **09-16 밤** |
| 7 | **📊 데이터 품질** | [data_quality.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/data_quality.html) | **09-17 오전** |
| 8 | **🏗️ Capex 워터폴** | [capex_waterfall.html](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/dashboard/capex_waterfall.html) | **09-17 오전** |

---

## 현재 문서 현황 (09-17 기준)

### 설계/요건 문서 (09-17 신규 4종)

| 문서 | 내용 | 파일 |
|:---|:---|:---|
| 뉴스 인텔리전스 설계 | 순방향/역방향 두 방향의 아키텍처 | [2026-09-17_news_intelligence_layer_design.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-17_news_intelligence_layer_design.md) |
| 순방향 분석기 요건정의서 | FR-01~06, NFR-01~04, Stage 1~3 | [2026-09-17_news_impact_analyzer_requirements.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-17_news_impact_analyzer_requirements.md) |
| 추가 기능 13가지 제안서 | 5개 카테고리, 기존과 비중복 | [2026-09-17_additional_feature_proposals.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-17_additional_feature_proposals.md) |
| 3대 기능 요건정의서 | 데이터 품질, Capex 워터폴, 원페이저 상세 | [2026-09-17_three_features_requirements.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-17_three_features_requirements.md) |

### 분석 보고서 (09-16 작성, 3종)

| 문서 | 내용 | 파일 |
|:---|:---|:---|
| ROAI 심층 분석 | 하이퍼스케일러 AI Capex 회수율 | [2026-09-16_hyperscaler_ai_capex_and_roai_analysis.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-16_hyperscaler_ai_capex_and_roai_analysis.md) |
| HBM 수급 삼국지 | 메모리 3사 ASP·점유율·수급 밸런스 | [2026-09-16_hbm_supply_trio_asp_and_market_balance.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-16_hbm_supply_trio_asp_and_market_balance.md) |
| Q2 통합 실적 브리핑 | 28개사 2026-Q2 종합 실적 | [2026-09-16_2026_q2_value_chain_earnings_synthesis.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-16_2026_q2_value_chain_earnings_synthesis.md) |

---

## ⚠️ 확인 필요 사항

1. **`layer_capital_absorption.html`이 0바이트** — 재생성이 필요합니다
   - 실행: `python3 scripts/generate_layer_capital_absorption.py` (해당 스크립트 존재 여부 확인 필요)
2. **`multi_company_overlay.html`의 생성 스크립트 내용이 삭제됨** — 사용자가 `generate_multi_company_overlay.py`를 빈 파일로 만들었으므로, 기존 HTML은 유지되나 재생성 불가
3. **대시보드 간 네비게이션** — 신규 대시보드 2종(data_quality, capex_waterfall)이 기존 네비게이션에 연결되어 있는지 확인 필요
