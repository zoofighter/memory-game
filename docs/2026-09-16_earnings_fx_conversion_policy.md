# 실적 통화·환율 환산 정책

## 결정

`earnings_reports`의 분석용 금액(`revenue`, `op_income`, `net_income`, `capex`,
`consensus_revenue`)은 `B_USD`를 기본 단위로 사용한다. USD 이외 통화로 공시된
실적만 원 공시값과 적용 환율을 함께 보존한다.

## 필드와 계산 규칙

- `unit`: 분석용 단위. 정상 분석 데이터는 `B_USD`.
- `reported_*`: 회사가 공시한 원 통화 금액. 매출·영업이익·순이익뿐 아니라
  컨센서스 매출과 설비투자도 환산 전 값을 보존한다.
- `reported_currency`: `USD`, `KRW`, `TWD`, `JPY` 등 ISO 통화 코드.
- `reported_unit`: `T_KRW`, `M_TWD`, `B_JPY` 등 원 공시값의 배율 포함 단위.
- `fx_rate`: 현지통화/1 USD 방향으로 고정한다.
- `fx_rate_type`: `QUARTER_AVG`, `REPORT_DATE`, `GUIDANCE` 등.
- `fx_source`, `fx_as_of_date`: 환율 출처와 기준일.

원 통화가 billion 단위이면 `B_USD = reported_value / fx_rate`로 계산한다.
million 단위이면 `B_USD = reported_value / fx_rate / 1000`으로 계산한다.

USD 원천 데이터는 `reported_currency='USD'`, `fx_rate=NULL`로 둔다. 환율이
검증되지 않은 비USD 데이터는 임의 환산하지 않으며 `unit`을 기존 원 단위로
유지하여 분석 대상에서 식별할 수 있게 한다.

## 정확성과 감사 가능성

USD 분석값만으로 원값을 역산하면 반올림 오차가 생기므로 `reported_*` 원값도
보존한다. 확정 실적에는 해당 분기 평균 환율을 우선 적용하며, 전망에는 회사가
공시한 가이던스 환율만 사용한다. 시장 환율이나 임의 고정환율은 출처·유형 없이
적용하지 않는다.

## 이번 적용 범위

공시 환율과 원값이 기존 적재 스크립트에 명시된 Kioxia 4건과 ASE 3건에 환율
메타데이터를 연결했다. 삼성전자와 SK하이닉스 52건은 Federal Reserve Board의
DEXKOUS 일별 관측치로 계산한 분기 평균을 적용해 `B_USD`로 전환한다.
2026-Q3 전망은 2026-09-11까지의 부분 분기 평균, 2026-Q4 전망은 같은 날의
현물환율을 전망 가정으로 사용하며 각각 `PARTIAL_QUARTER_AVG`,
`SPOT_FORECAST_ASSUMPTION`으로 구분한다.
