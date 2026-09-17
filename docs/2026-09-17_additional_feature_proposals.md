# Memory Claude 확장 가능 기능 추가 제안서

**작성일**: 2026-09-17  
**프로젝트 기준 시점**: 2026-09-10  
**현재 시스템**: 36개사 마스터, 실적 658건(28사), 계약 15건($877B), 마일스톤 25건, 대시보드 6종, 분석 보고서 3종  
**기존 제안 문서**:
- [2026-09-16_visualization_and_analytics_roadmap.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-16_visualization_and_analytics_roadmap.md) (시각화 7종 + LLM 분석 3종 + 파생 5종)
- [2026-09-17_news_intelligence_layer_design.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-17_news_intelligence_layer_design.md) (순방향/역방향 뉴스 인텔리전스)
- [2026-09-17_news_impact_analyzer_requirements.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-17_news_impact_analyzer_requirements.md) (순방향 분석기 요건정의서)

---

> 본 문서는 **기존 제안과 중복되지 않는 신규 확장 기능**만을 다룹니다.

---

## 카테고리 A — 데이터 품질 & 운영 도구

### A-1. 📊 데이터 품질 대시보드 (Data Quality & Coverage Scorecard)

**현재 문제**: 36개사 중 실적 보유 28사, beat_miss_status 입력 8사, capex 입력 2사, guidance 입력 2사. **어떤 데이터가 어디까지 채워져 있는지** 한눈에 보이지 않음.

```
┌──────────────────────────────────────────────────────────┐
│  📊 데이터 완결성 스코어보드                                │
│                                                          │
│  기업명       │ 매출 │ OPM │ Capex │ Beat │ 가이던스 │ 총점  │
│  ─────────────┼──────┼─────┼───────┼──────┼─────────┼──── │
│  NVIDIA       │ 26/26│26/26│  0/26 │23/26 │  1/26   │ 76/130│
│  GOOGLE       │ 26/26│26/26│  2/26 │24/26 │  0/26   │ 78/130│
│  SK_HYNIX     │ 24/26│24/26│  0/26 │20/26 │  0/26   │ 68/130│
│  ANTHROPIC    │  0/26│ 0/26│  0/26 │ 0/26 │  0/26   │  0/130│
│  ...          │      │     │       │      │         │      │
│                                                          │
│  ⚠️ Capex 데이터: 2사만 입력 (GOOGLE, META)                │
│  ⚠️ 가이던스: 2사만 입력 (NVIDIA, KIOXIA)                  │
│  ⚠️ 비상장 8사: 실적 데이터 0건                              │
└──────────────────────────────────────────────────────────┘
```

**구현**: `dashboard/data_quality.html` 또는 기존 `dashboard/index.html`에 탭 추가  
**가치**: 다음에 어떤 데이터를 채워야 하는지 우선순위가 명확해짐  
**난이도**: ⭐ (SQLite 집계 쿼리 + Chart.js 히트맵)

---

### A-2. ⏱️ 실적 발표 캘린더 (Earnings Calendar)

**현재 문제**: 28개사의 실적 발표 일정이 DB에 없음. 어떤 기업이 언제 발표하는지 매번 수동 확인.

```sql
-- 신규 테이블 제안
CREATE TABLE IF NOT EXISTS earnings_calendar (
    entity_id       TEXT NOT NULL,
    period          TEXT NOT NULL,           -- '2026-Q3'
    expected_date   TEXT,                    -- '2026-10-22'
    actual_date     TEXT,                    -- 실제 발표일 (발표 후 기록)
    status          TEXT DEFAULT 'PENDING',  -- PENDING / REPORTED / DELAYED
    notes           TEXT,
    PRIMARY KEY (entity_id, period),
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
);
```

**대시보드 UI**: 타임라인 뷰 (가로 축: 날짜, 세로: 기업, 색상: 발표 완료/대기/지연)  
**가치**: 역방향 워치리스트(방향 B)의 **유형 1: Earnings Watch**를 정확하게 보강  
**난이도**: ⭐⭐ (테이블 추가 + 데이터 수동 입력 + 시각화)

---

### A-3. 🔄 DB 변경 이력 추적 (Audit Trail Dashboard)

**현재 문제**: `earnings_correction_audit` 테이블이 존재하지만, 변경 이력을 시각적으로 보는 수단이 없음. 언제 어떤 데이터가 수정되었는지 추적 불가.

**구현**:
- 기존 `earnings_correction_audit` 테이블의 변경 이력을 타임라인으로 시각화
- "최근 7일 변경 사항" 요약 카드를 메인 대시보드에 추가
- 대규모 수정 시 자동 경고 ("28건 동시 변경 감지")

**가치**: 데이터 신뢰성 투명화 — "이 숫자가 언제 어떻게 들어왔는가"  
**난이도**: ⭐⭐

---

## 카테고리 B — 심층 분석 도구

### B-1. 🔮 선행지표 상관 매트릭스 대시보드 (Leading Indicator Heatmap)

**기존 로드맵(§3.5)의 시각화 구현체**: 28개사 간의 **시차별 매출 상관계수**를 히트맵으로 인터랙티브하게 표시.

```
             SK하이닉스  삼성전자  마이크론  TSMC  NVIDIA  구글   아마존
NVIDIA t      0.95      0.88    0.82    0.91   1.00   0.72   0.68
NVIDIA t-1    0.87      0.79    0.75    0.85   -      0.80   0.75
NVIDIA t-2    0.72      0.65    0.61    0.74   -      0.88   0.82

→ 구글 Capex가 2분기 후 NVIDIA 매출과 가장 높은 상관 (r=0.88)
→ NVIDIA 매출이 1분기 후 SK하이닉스 매출과 가장 높은 상관 (r=0.95)
```

**구현**: `dashboard/correlation_matrix.html`  
- Python으로 상관 매트릭스 사전 계산 → JSON → Chart.js Matrix 플러그인 또는 D3 히트맵  
- 슬라이더: lag(0~4분기), 기간 필터(2020~2026)  
**가치**: **밸류체인 전파 시차(Lag)** 를 정량적으로 증명 — 투자 타이밍 판단의 핵심  
**난이도**: ⭐⭐⭐ (numpy 상관 계산 + D3 히트맵)

---

### B-2. 📈 OPM(영업이익률) 히트맵 — 업황 사이클 스냅샷

28개사 × 26분기(2020-Q1 ~ 2026-Q2)의 **OPM을 색상 강도로 한눈에** 보여줌.

```
          20Q1 20Q2 20Q3 20Q4 21Q1 ... 25Q3 25Q4 26Q1 26Q2
NVIDIA    ████ ████ ████ ████ ████     ████ ████ ████ ████
TSMC      ███  ███  ████ ████ ████     ████ ████ ████ ████
SK하이닉스 ██   █    ░░░░ ░░░░ █        ████ ████ ████ ████
삼성전자   ██   █    ░░░░ ░░░░ ░        ██   ███  ████ ████
인텔      ███  ██   ██   █    █        ░    ░░   ░░   ░
                                      ↑ 적자 구간은 빨간색

색상 스케일: 빨강(-30%이하) → 주황(0%) → 초록(20%) → 파랑(50%+)
```

**가치**: 메모리 사이클(2022~2023 적자 → 2024~2026 슈퍼사이클)이 **시각적으로 즉시 포착**됨  
**난이도**: ⭐⭐ (Chart.js Matrix 플러그인 또는 순수 HTML 테이블 + CSS)

---

### B-3. 🏗️ Capex → 밸류체인 전파 워터폴 차트

**핵심 질문**: *"하이퍼스케일러가 $100B Capex를 쏟으면, 그 돈이 밸류체인 각 레이어에 얼마씩 흘러가는가?"*

```
  $100B Capex (L2 하이퍼스케일러)
    │
    ├── $45B → L3 컴퓨팅 (GPU/ASIC)
    │     ├── $28B → L4 파운드리 (TSMC 웨이퍼)
    │     │     ├── $8B → L4 장비 (ASML/AMAT/LAM)
    │     │     └── $4B → L5 메모리 (HBM 패키징)
    │     └── $17B → L5 메모리 (HBM 직접)
    ├── $25B → L7/L8 인프라·전력 (데이터센터 건설)
    ├── $20B → L6 네트워킹 (광통신)
    └── $10B → 기타 (소프트웨어, 인력 등)
```

**구현**: 기존 Sankey 시뮬레이터와 다른 접근 — **계약 테이블(contracts)의 value_b를 실제 비율로 역산**하여 워터폴 차트로 표현  
**가치**: *"Capex의 실제 흐름 경로"*를 정량적으로 추적  
**난이도**: ⭐⭐

---

### B-4. 🎯 Beat/Miss 패턴 분석 & 서프라이즈 트래커

현재 NVIDIA(23분기), GOOGLE/AMAZON/META/MICROSOFT(각 24분기), TSMC(24분기), SAMSUNG(22분기), SK_HYNIX(20분기) — 총 **181건**의 beat_miss_status 데이터가 있음.

```
기업별 Beat 비율:
  NVIDIA:    22/23 = 95.7% (유일한 MISS: 2022-Q2 게이밍 급락)
  GOOGLE:    21/24 = 87.5%
  AMAZON:    19/24 = 79.2%
  SK하이닉스: 16/20 = 80.0% (2022~2023 다운사이클 MISS 집중)

연속 Beat 스트릭:
  NVIDIA: 현재 16분기 연속 BEAT (2022-Q3 이후)
  TSMC:   현재 12분기 연속 BEAT (2023-Q3 이후)
```

**대시보드**: 가로 막대 (각 분기 BEAT=초록/MISS=빨강) + 연속 스트릭 카운터 + 서프라이즈 크기 차트  
**가치**: *"이 기업은 컨센서스를 지속적으로 초과하는가?"* → 신뢰도 평가  
**난이도**: ⭐⭐

---

## 카테고리 C — 자동 보고서 & 생산성 도구

### C-1. 📝 분기별 종합 브리핑 자동 생성기

실적이 업데이트될 때마다 `docs/generated/YYYY-QN_briefing.md`를 자동 생성.

```python
# scripts/generate_quarterly_briefing.py
# 실행: python3 scripts/generate_quarterly_briefing.py --quarter 2026-Q2

# 출력 구조:
# 1. Executive Summary (매출 Top5, OPM Top5, 최대 상승/하락 기업)
# 2. 레이어별 총량 추이 (L1~L8 합산 매출/영업익)
# 3. Beat/Miss 현황 (해당 분기 발표 기업 대상)
# 4. 주요 계약 업데이트
# 5. 마일스톤 진행 현황
# 6. 다음 분기 주요 이벤트
# 7. 데이터 품질 노트 (미입력 항목, 추정치 비중)
```

**가치**: 현재 수동으로 작성하는 종합 보고서([2026-09-16_2026_q2_value_chain_earnings_synthesis.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-16_2026_q2_value_chain_earnings_synthesis.md))를 **80% 자동화**  
**난이도**: ⭐⭐ (SQLite 집계 + 템플릿 마크다운 생성, LLM 불필요)

---

### C-2. 📊 기업별 원페이저 (Entity One-Pager) 자동 생성

각 기업에 대해 **투자 노트 1장**을 자동 생성하는 스크립트.

```
┌──────────────────────────────────────────────────────────┐
│  SK하이닉스 (SK_HYNIX) — L5 메모리                        │
│  000660.KS | HBM 시장 점유율 63.5%                        │
├──────────────────────────────────────────────────────────┤
│  최근 4분기 실적 (확정):                                   │
│  25Q3: $17.6B, OPM 46.6% → 25Q4: $22.7B, OPM 58.4%      │
│  26Q1: $35.9B, OPM 71.5% → 26Q2: $52.9B, OPM 76.3%      │
│                                                          │
│  주요 계약:                                               │
│  · NVIDIA HBM3E/4 공급: $18.0B                           │
│  · 앤트로픽 메모리 직납: $15.0B                             │
│                                                          │
│  마일스톤:                                                │
│  · 2027-03: HBM4 16단 대량 양산 (CRITICAL)                │
│                                                          │
│  Fab 캐파:                                               │
│  · M15X 이천: 1c DRAM, 양산 중                            │
│  · 용인 메가클러스터: HBM4 전용, 2027 가동 예정             │
│                                                          │
│  핵심 관전 포인트:                                         │
│  ⚡ OPM 76.3%는 메모리 역사상 전례 없는 수준               │
│  ⚡ HBM4 양산 시점이 삼성 대비 1~2분기 선행                 │
│  ⚡ 앤트로픽 직납으로 NVIDIA 외 수요 다변화 시작             │
└──────────────────────────────────────────────────────────┘
```

**구현**: `scripts/generate_entity_one_pager.py --entity SK_HYNIX`  
**출력**: `docs/generated/entity_profiles/SK_HYNIX.md`  
**가치**: 36개사 각각에 대한 **현재 포지션 스냅샷**을 즉시 생성  
**난이도**: ⭐⭐ (SQLite 다중 테이블 JOIN + 마크다운 템플릿)

---

### C-3. 🔗 밸류체인 의존도 요약 보고서 (Dependency Report)

계약 테이블에서 **특정 기업이 사라졌을 때 영향받는 범위**를 자동 산출.

```
❓ "만약 TSMC의 CoWoS 캐파가 50% 축소되면?"

영향받는 직접 고객:
  · NVIDIA — $35.0B 공급 계약의 50% 차질 → ~$17.5B 생산 감소
  · BROADCOM — 커스텀 ASIC 생산 지연

간접 파급:
  · L2 하이퍼스케일러 전체 — GPU 공급 차질로 AI 인프라 구축 지연
  · L5 메모리 — HBM 수요 연동 감소 (NVIDIA 생산 연동)
  · L8 전력 — 데이터센터 증설 일정 후방 지연

영향 계약 총액: $95.0B (전체 $877B의 10.8%)
```

**가치**: 밸류체인 **취약점(Single Point of Failure)** 정량화  
**난이도**: ⭐⭐ (contracts 테이블 그래프 탐색)

---

## 카테고리 D — 외부 데이터 연동

### D-1. 📈 주가 데이터 자동 수집 (Yahoo Finance)

```python
# 무료 API: yfinance 라이브러리 (pip install yfinance)
import yfinance as yf

# 28개 상장사 ticker 자동 매핑 (entities.ticker 필드 활용)
tickers = ["NVDA", "TSM", "GOOGL", "AMZN", "MSFT", "META", ...]
data = yf.download(tickers, start="2020-01-01", period="max", interval="1d")
```

**활용**:
- 실적 발표일 전후 주가 변동 분석 (Beat/Miss → 주가 반응)
- 밸류체인 기업 간 주가 상관계수 계산
- 분기별 시가총액 추이 비교

**제약**: 한국 주식(삼성 005930, SK하이닉스 000660)은 yfinance에서 `.KS` suffix 필요  
**난이도**: ⭐⭐ (yfinance + SQLite 저장)

---

### D-2. 💱 환율 자동 환산 테이블 (FX Rate History)

현재 DB에 `fx_rate` 필드가 있지만 대부분 미입력. 분기 평균 환율을 자동 수집하여 환산 정확도 향상.

```sql
CREATE TABLE IF NOT EXISTS fx_rates (
    currency_pair   TEXT NOT NULL,    -- 'KRW/USD', 'TWD/USD', 'JPY/USD'
    period          TEXT NOT NULL,    -- '2026-Q2'
    avg_rate        REAL NOT NULL,    -- 분기 평균 환율
    source          TEXT,             -- 'FRED', 'BOK', 'manual'
    PRIMARY KEY (currency_pair, period)
);
```

**가치**: SK하이닉스/삼성전자(KRW), TSMC(TWD), 키옥시아(JPY) 실적의 **USD 환산 오차 최소화**  
**난이도**: ⭐ (수동 입력 또는 FRED API 활용)

---

### D-3. 📰 RSS 피드 기반 뉴스 알림 (Lightweight News Feed)

상시 서버 없이 **배치로 실행 가능한** 뉴스 수집기.

```python
# scripts/fetch_news_feed.py
# 실행: python3 scripts/fetch_news_feed.py
# (또는 crontab으로 매일 09:00 자동 실행)

RSS_FEEDS = {
    "SemiAnalysis": "https://semianalysis.com/feed/",
    "AnandTech": "https://www.anandtech.com/rss/",
    "SeekingAlpha_NVDA": "https://seekingalpha.com/feed/...",
    # Google News RSS (기업명 검색)
    "Google_News_NVIDIA": "https://news.google.com/rss/search?q=NVIDIA+earnings",
    "Google_News_SK하이닉스": "https://news.google.com/rss/search?q=SK하이닉스+실적",
}

# 1. RSS 파싱 → 제목에서 entity_id 자동 매칭
# 2. 새 기사만 필터링 (이전 실행 대비 diff)
# 3. docs/news_feed/YYYY-MM-DD.md 로 저장
# 4. entity 매칭된 기사는 analyze_news_impact.py로 자동 전달 (Stage 2+)
```

**가치**: 36개 기업 관련 뉴스를 **능동적으로 수집** — 역방향 워치리스트의 자동화  
**난이도**: ⭐⭐ (feedparser 라이브러리 + entity 매칭)

---

## 카테고리 E — 인터랙티브 경험 강화

### E-1. 🔍 통합 검색 인터페이스 (Unified Search)

대시보드에 **검색 바**를 추가하여, 기업명/기간/키워드로 DB 전체를 검색.

```
[검색: "SK하이닉스 2026"]

결과:
 📊 실적 (4건): 2026-Q1 $35.9B, 2026-Q2 $52.9B, ...
 🔗 계약 (2건): NVIDIA HBM3E/4 $18B, 앤트로픽 직납 $15B
 🏭 마일스톤 (1건): 2027-03 HBM4 16단 양산
 🏗️ Fab (2건): M15X 이천, 용인 메가클러스터
```

**가치**: 현재 대시보드별로 분산된 정보를 **하나의 진입점**에서 탐색  
**난이도**: ⭐⭐ (JavaScript 클라이언트 사이드 검색, DB 데이터를 JSON으로 사전 임베딩)

---

### E-2. 📱 모바일 반응형 대시보드

현재 대시보드는 1985px 뷰포트 기준으로 설계되어 모바일에서 사용성이 낮음. CSS 미디어 쿼리 추가로 태블릿/모바일 지원.

**가치**: 이동 중에도 실적/계약 현황 빠른 확인  
**난이도**: ⭐⭐ (CSS 미디어 쿼리 + 레이아웃 조정)

---

### E-3. 📋 "나의 워치리스트" 기능 (Personal Watchlist)

대시보드에서 **관심 기업 3~5개를 고정** 하여 메인 화면에서 핵심 지표를 즉시 확인.

```
[나의 워치리스트]
 ★ NVIDIA    — 최신: 26Q2 $44.0B | OPM 65.4% | Beat 16연속
 ★ SK하이닉스 — 최신: 26Q2 $52.9B | OPM 76.3% | Beat 8연속
 ★ TSMC     — 최신: 26Q2 $28.1B | OPM 53.2% | Beat 12연속
```

**구현**: localStorage 기반 (서버 불필요)  
**난이도**: ⭐

---

## 종합 우선순위 매트릭스

```
                    높음 ←── 인사이트 가치 ──→ 낮음
                    ┌────────────────────────────┐
  쉬움    ⭐        │ A-1 데이터 품질     E-3 워치│
                    │ C-1 분기 브리핑     D-2 환율│
  ──────────────────┤                            │
  보통    ⭐⭐      │ C-2 원페이저        E-2 반응│
                    │ B-2 OPM 히트맵     A-3 이력│
                    │ B-4 Beat/Miss     E-1 검색│
                    │ C-3 의존도 리포트   D-3 RSS│
                    │ A-2 실적 캘린더            │
  ──────────────────┤                            │
  어려움  ⭐⭐⭐    │ B-1 상관 매트릭스           │
                    │ B-3 Capex 워터폴           │
                    │ D-1 주가 연동              │
                    └────────────────────────────┘
```

---

## 추천 실행 순서 (Top 5)

| 순위 | 기능 | 이유 | 소요 시간 |
|:---:|:---|:---|:---|
| **1** | **A-1 데이터 품질 대시보드** | 다음에 뭘 채워야 하는지 명확해짐 — 모든 후속 작업의 기반 | ~2시간 |
| **2** | **C-1 분기별 종합 브리핑 자동 생성** | 수동 보고서 작성의 80% 자동화, 즉시 체감 가능 | ~3시간 |
| **3** | **B-2 OPM 히트맵** | 28사 × 26분기 업황 사이클을 한 화면에 — 시각적 임팩트 최대 | ~3시간 |
| **4** | **C-2 기업별 원페이저 자동 생성** | 36개사 각각의 "현재 위치" 스냅샷 즉시 생산 | ~3시간 |
| **5** | **B-4 Beat/Miss 패턴 트래커** | 181건의 기존 데이터로 즉시 구현 가능, 신뢰도 평가 | ~2시간 |

> 위 5개를 모두 구현하면 **약 13시간 소요**, 시스템의 **분석 깊이와 자동화 수준이 한 단계 도약**합니다.
