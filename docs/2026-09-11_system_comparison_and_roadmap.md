# Memory Claude: 유사 시스템 비교 및 진행 방향

**작성일**: 2026-09-11  
**대상 독자**: 본 프로젝트 운영자  
**목적**: 동류 시스템과의 위치 파악, 차별화 포인트 정의, 향후 발전 로드맵 구체화

---

## 1. 유사 시스템 지형도

Memory Claude와 목적·기능이 겹치는 시스템은 크게 **5개 범주**로 분류됩니다.  
각 범주는 비용·깊이·자동화 수준이 서로 다른 스펙트럼에 놓입니다.

```
                    ← 비용  낮음 · · · · · · · · 높음 →

깊이   높음  ┌──────────────────────────────────────────────┐
  |         │  SemiAnalysis    Bloomberg Terminal           │
  |         │  Fabricated      AlphaSense/Tegus             │
  |         │  Knowledge       Palantir Foundry             │
  |   중간  │  ─────────────────────────────────────────── │
  |         │  OpenBB          IDC STSI                     │
  |         │  MacroMicro      Koyfin                       │
  |   낮음  │  ─────────────────────────────────────────── │
  ↓         │  Feedly MI       (일반 주식 앱)               │
            └──────────────────────────────────────────────┘
                                 ↑
                         Memory Claude 현재 위치
                     (저비용 + 중~고 깊이를 추구)
```

---

### 범주 A — 기관급 유료 인텔리전스 플랫폼

| 시스템 | 핵심 강점 | 약점 | 월 비용 |
| :--- | :--- | :--- | :--- |
| **Bloomberg Terminal** | 실시간 시장 데이터, 전 자산군 커버 | 반도체 공급망 깊이 부족, AI 분석 약함 | $2,000~3,000 |
| **AlphaSense / Tegus** | 어닝콜 트랜스크립트 AI 검색, 브로커 리서치 | 팹·공급망 데이터 없음 | $1,000~2,000 |
| **Palantir AIP / Foundry** | 공급망 최적화, 아젠틱 AI, 대기업 커스터마이징 | 개인 투자자 접근 불가, 수억 원 계약 단위 | 기업용 |

> **핵심 격차**: 기관급 시스템은 **공시 중심**이며, 팹 캐파·HBM 공급망·데이터센터 증설처럼 정량화하기 어려운 데이터를 구조화하는 데는 취약합니다.

---

### 범주 B — 반도체·AI 인프라 특화 리서치

| 시스템 | 핵심 강점 | 약점 | 접근성 |
| :--- | :--- | :--- | :--- |
| **SemiAnalysis** | AI 인프라·HBM·파운드리 심층 분석, 독점 채널 취재 | 데이터 구조화 안 됨 (뉴스레터), 가격 비쌈 | 뉴스레터 (유료) |
| **Fabricated Knowledge** | 반도체 재무 + 기술 연계 분석 | 개인 블로그 수준, 체계 미흡 | Substack |
| **IDC STSI** | 시장 점유율·매출·예측 보고서 | 정량 보고서 단발, 시계열 추적 불가 | 보고서 유료 구매 |

> **핵심 격차**: 전문 리서치는 **텍스트 중심 소비**이며, 데이터베이스에 체계적으로 저장·쿼리·시각화하는 기능이 없습니다.

---

### 범주 C — 오픈소스 / 개인용 분석 플랫폼

| 시스템 | 핵심 강점 | 약점 | 비용 |
| :--- | :--- | :--- | :--- |
| **OpenBB** | Python 기반, SEC EDGAR·Yahoo 연동, 커스터마이징 자유 | 반도체 공급망 도메인 템플릿 없음, 구축 비용 높음 | 무료 |
| **MacroMicro** | 반도체 공급망 매크로 지표 시각화 (웨이퍼 가동률 등) | 기업 실적·계약 추적 안 됨, 분기 딥다이브 불가 | 무료~유료 |
| **Koyfin** | 재무 데이터 시각화, 멀티차트, 빠른 UI | 팹·DC·계약 데이터 없음, 공급망 관점 부재 | $49/월 |

---

### 범주 D — 개인 지식 관리 + 투자 리서치 (PKM)

| 시스템 | 핵심 강점 | 약점 |
| :--- | :--- | :--- |
| **Obsidian + Dataview** | 마크다운 기반 로컬, 링크 네트워크, 플러그인 생태계 | 구조적 데이터 처리 약함, 차트·대시보드 미약 |
| **Notion Database** | 관계형 DB UI, 협업 용이 | 클라우드 의존, 대용량 데이터 느림, 커스텀 뷰 한계 |
| **Roam Research** | 양방향 링크, 아웃라이너 | 정량 데이터 처리 부적합 |

> Memory Claude는 **SQLite DB + Obsidian Canvas + 웹 대시보드**를 결합하여 이 범주의 한계를 극복합니다.

---

### 범주 E — 차세대 Agentic 금융 인텔리전스 (2026 신흥)

2026년 현재, AI 에이전트 기반의 자율 리서치 시스템이 급부상하고 있습니다:

| 기술/시스템 | 특징 |
| :--- | :--- |
| **MCP + SEC EDGAR** | AI 에이전트가 EDGAR를 자연어로 쿼리, XBRL 기반 정밀 데이터 추출 |
| **LangGraph / CrewAI** | 멀티 에이전트 오케스트레이션 — "Researcher → Parser → Synthesizer" 파이프라인 |
| **Sentinel Agents** | EDGAR 신규 공시를 실시간 모니터링, 특정 키워드 감지 시 자동 알림 |
| **XBRL-first Pipelines** | PDF 대비 74배 오류 감소, 수치 추출 정확도 극대화 |

> **Memory Claude의 미래 방향**이 바로 이 범주입니다.

---

## 2. Memory Claude의 차별화 포지션

위 5개 범주 중 어느 단일 시스템도 Memory Claude가 추구하는 조합을 제공하지 않습니다.

```
Memory Claude = 
  [SemiAnalysis의 도메인 깊이]
+ [OpenBB의 오픈소스·커스터마이징]
+ [Obsidian PKM의 로컬·프라이빗]
+ [Bloomberg의 시계열 데이터 구조]
+ [Palantir의 밸류체인 연계 시각화]
── 단, 비용은 $0 (AI 에이전트 활용)
```

### 사용자만이 갖는 Edge (정보 비대칭)

| Edge 항목 | 설명 |
| :--- | :--- |
| **수기 알파 데이터** | `99.raw/`에 쌓이는 수기 메모 — 공개 데이터베이스에 없는 정성 신호 |
| **밸류체인 연계 뷰** | 하이퍼스케일러 Capex → GPU 공급 → HBM 수요 → 팹 증설의 인과 연결 |
| **장기 시계열 축적** | 2020-Q1부터 분기별 누적 — 업황 사이클 패턴 학습 |
| **AI 학습 데이터** | 향후 이 DB 자체가 개인 특화 RAG 지식베이스가 될 수 있음 |

---

## 3. 앞으로의 진행 방향 (4단계 진화 시나리오)

### Stage 1 (현재 ~ 2026-Q4): 데이터 기반 확보

현재 Phase 5까지 구현 완료. 남은 핵심 과제:

```
Priority 1: 데이터 신뢰도 제고
├── SEC EDGAR API 연동으로 earnings_reports 수치 검증
├── DART API로 삼성전자·SK하이닉스 원본 확인
└── 컨센서스 수치: FactSet 무료 배포본 또는 Visible Alpha 활용

Priority 2: 99.raw/ 자동 파서 (Phase 6)
├── validator.py: MD/CSV → SQLite 자동 적재
└── 수기 메모를 구조화 DB에 반영하는 파이프라인 완성

Priority 3: entity_strategy 데이터 적재 (Phase 8)
└── 21개사 전략 차원 (AI 로드맵, 설비투자 의지, 파트너십) 기록
```

---

### Stage 2 (2027-Q1 ~ Q2): 자동 수집 에이전트

외부 데이터를 스스로 수집·정제하는 자율 파이프라인:

```python
# 목표 아키텍처 (Phase 7)
class MemoryClaudeAgent:
    tools = [
        SECEdgarTool(),          # 10-Q/10-K XBRL 파싱
        DartApiTool(),           # 한국 공시 자동 수집
        EarningsCallParser(),    # 어닝콜 트랜스크립트 요약
        NewsMonitorTool(),       # Google News RSS → 계약 탐지
        FabCapacityTracker(),    # TrendForce 발표 자동 수집
    ]
    
    def nightly_run(self):
        """매일 밤 자동 실행: 신규 공시 감지 → DB 업데이트"""
        new_filings = self.tools.sec.get_new_filings(watchlist=ENTITIES)
        for filing in new_filings:
            data = self.tools.parser.extract(filing)
            db.insert_earnings_report(data)
        self.generate_daily_brief()
```

**핵심 기술 스택:**
- `MCP + SEC EDGAR`: AI 에이전트의 EDGAR 자연어 쿼리
- `XBRL-first 파싱`: PDF 대비 74배 정확도
- `LangGraph`: 멀티에이전트 오케스트레이션 (수집 → 검증 → 적재)

---

### Stage 3 (2027-Q3 ~ 2028-Q1): 예측 인텔리전스

축적된 시계열 데이터를 기반으로 업황 예측 모델 구축:

```
현재 DB 구조 (과거 누적)
    ↓
예측 모델 입력:
├── earnings_reports: 21개사 × 6년 × 4분기 = ~500건
├── contracts: 계약 규모 × 체결 시점 → 매출 반영 시차 모델
├── fab_capacity: WSPM 증설 일정 → 공급 예측
└── datacenter_capacity: 전력·가속기 → 수요 예측

예측 출력:
├── "2027-Q2 SK하이닉스 HBM3E 매출 $X±Y억 전망"
├── "TSMC N2 캐파 부족 → 납기 지연 리스크 시나리오"
└── "하이퍼스케일러 Capex 피크아웃 시 NVIDIA 매출 영향"
```

---

### Stage 4 (2028+): 개인화 인텔리전스 어시스턴트

이 단계에서 Memory Claude는 사용자 전용 금융 AI로 진화합니다:

```
"엔비디아 2026 데이터센터 매출 추세 보여줘"
    → DB 쿼리 + 차트 자동 생성

"TSMC 2027년 N2 캐파 추가되면 어느 고객이 가장 수혜야?"
    → 계약·팹·실적 DB 연계 분석 + 시나리오 출력

"이번 주 중요한 IR 발표 요약해줘"
    → Sentinel Agent가 자동 수집 + 기존 DB와 차이 분석
```

**핵심 전제**: 4년치 이상의 구조화 데이터가 축적되면, 이 DB 자체가 반도체·AI 밸류체인에 특화된 **개인 RAG 지식베이스**가 됩니다.

---

## 4. 벤치마크: 3년 후 어떤 수준을 목표로 하는가

| 지표 | 현재 (2026-09) | 1년 후 (2027-09) | 3년 후 (2029-09) |
| :--- | :--- | :--- | :--- |
| 기업 수 | 21개 | 21개 (깊이 강화) | 30~40개 (인접 산업 확장) |
| 실적 레코드 | 208건 | ~600건 (자동 수집) | ~2,000건 |
| 계약 레코드 | 10건 | ~100건 | ~500건 |
| 데이터 자동화율 | 0% (전수 수동) | ~60% (SEC+DART 자동) | ~90% (Agentic) |
| 예측 정확도 | N/A | 매출 ±10% 목표 | 매출 ±5%, 시황 방향 85% |
| 산출물 | 보고서 + 대시보드 | + 자동 브리핑 | + 시나리오 예측 리포트 |

---

## 5. 실행 우선순위 제안

지금 당장 가장 레버리지가 높은 작업 순서:

| 시점 | 작업 | 효과 |
| :--- | :--- | :--- |
| **즉시** | SEC EDGAR API 연동 스크립트 | earnings_reports AI 추정치 → 공시 원본 교체, 신뢰도 즉시 상승 |
| **1개월** | `validator.py` 구현 (Phase 6) | 99.raw/ 수기 입력 → DB 자동 반영 파이프라인 |
| **3개월** | 어닝콜 자동 요약 파이프라인 | 매 분기 실적 시즌 21개사 동시 업데이트 |
| **6개월** | Sentinel 에이전트 (Phase 7) | 새로운 공시·계약 자동 탐지 → 알림 → "감지 시스템"으로 진화 |

---

## 6. 핵심 통찰 — 왜 이 시스템이 의미있는가

> **"기관 투자자는 데이터 팀이 있고, 개인 투자자는 직관에 의존한다.  
> Memory Claude는 그 사이를 메우는 개인화된 인텔리전스 인프라다."**

Bloomberg Terminal이 $3,000/월을 받는 이유는 데이터 때문이 아닙니다.  
**시계열로 구조화된 데이터 + 즉각적인 쿼리 능력 + 연결고리 시각화** 때문입니다.

AI 에이전트 시대에 이 세 가지를 개인이 구축할 수 있는 비용이 처음으로 $0에 수렴했습니다.  
Memory Claude는 그 가능성을 반도체·AI 밸류체인에 특화하여 실현하는 프로젝트입니다.

---

## 참고 연동 문서

- [requirements_spec.md v2.0](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/requirements_spec.md)
- [2026-09-10_value_and_direction.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-10_value_and_direction.md)
- [2026-09-10_strategic_imagination_scenarios.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-10_strategic_imagination_scenarios.md)
- [2026-09-10_implementation_roadmap.md](file:///Users/boon/Dropbox/03_code/b_0910_memory_claude/docs/2026-09-10_implementation_roadmap.md)
