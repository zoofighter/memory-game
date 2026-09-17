#!/usr/bin/env python3
import json
from pathlib import Path
import xlsxwriter

ROOT = Path(__file__).resolve().parents[1]
TMP = Path('/private/tmp/memory_claude_earnings_export')
OUT = ROOT / 'outputs' / 'earnings_export_2026-09-16' / 'memory_claude_earnings_2026-09-16.xlsx'

earnings = json.loads((TMP / 'earnings.json').read_text())
entities = json.loads((TMP / 'entities.json').read_text())
actuals = [r for r in earnings if r['is_forecast'] == 0]
forecasts = [r for r in earnings if r['is_forecast'] == 1]

OUT.parent.mkdir(parents=True, exist_ok=True)
wb = xlsxwriter.Workbook(OUT)
wb.set_properties({
    'title': 'Memory Claude 실적 데이터',
    'subject': '기업별 확정 실적 및 전망치',
    'author': 'Memory Claude',
    'comments': 'data/memory_claude.db 기준 2026-09-16 내보내기',
})

navy, blue, pale, gray, green, amber, red = '#17365D', '#2F75B5', '#D9EAF7', '#F2F2F2', '#E2F0D9', '#FFF2CC', '#FCE4D6'
title = wb.add_format({'bold': True, 'font_size': 20, 'font_color': '#FFFFFF', 'bg_color': navy, 'align': 'left', 'valign': 'vcenter'})
subtitle = wb.add_format({'font_color': '#44546A', 'font_size': 10})
section = wb.add_format({'bold': True, 'font_color': '#FFFFFF', 'bg_color': blue, 'align': 'left', 'valign': 'vcenter'})
kpi_label = wb.add_format({'bold': True, 'font_color': '#44546A', 'bg_color': pale, 'align': 'center', 'border': 1, 'border_color': '#B4C6E7'})
kpi_value = wb.add_format({'bold': True, 'font_size': 16, 'font_color': navy, 'bg_color': '#FFFFFF', 'align': 'center', 'border': 1, 'border_color': '#B4C6E7', 'num_format': '#,##0'})
note = wb.add_format({'font_color': '#666666', 'font_size': 9, 'text_wrap': True, 'valign': 'top'})
header = wb.add_format({'bold': True, 'font_color': '#FFFFFF', 'bg_color': navy, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 0})
text_fmt = wb.add_format({'valign': 'top'})
wrap_fmt = wb.add_format({'valign': 'top', 'text_wrap': True})
num_fmt = wb.add_format({'num_format': '#,##0.00;[Red](#,##0.00);-', 'align': 'right'})
pct_fmt = wb.add_format({'num_format': '0.00;[Red](0.00);-', 'align': 'right'})
date_fmt = wb.add_format({'num_format': 'yyyy-mm-dd', 'align': 'center'})
forecast_fmt = wb.add_format({'bg_color': amber})
actual_fmt = wb.add_format({'bg_color': green})
link_fmt = wb.add_format({'font_color': '#0563C1', 'underline': True, 'valign': 'top', 'text_wrap': True})

summary = wb.add_worksheet('요약')
summary.hide_gridlines(2)
summary.set_tab_color(navy)
summary.set_row(0, 30)
summary.merge_range('A1:H1', 'Memory Claude 실적 데이터', title)
summary.merge_range('A2:H2', '기준일 2026-09-16 · 원본 DB: data/memory_claude.db', subtitle)
summary.merge_range('A4:H4', '데이터 현황', section)

kpis = [
    ('전체 실적', len(earnings)), ('확정 실적', len(actuals)), ('전망치', len(forecasts)), ('실적 보유 기업', len({r['entity_id'] for r in earnings})),
]
for i, (label, value) in enumerate(kpis):
    c = i * 2
    summary.write(5, c, label, kpi_label)
    summary.write(6, c, value, kpi_value)

summary.write('A9', '구분', header); summary.write('B9', '행 수', header); summary.write('C9', '비중', header)
summary.write('A10', '확정'); summary.write_formula('B10', "=COUNTIF('전체 실적'!I2:I405,0)", kpi_value, len(actuals)); summary.write_formula('C10', '=B10/B12', pct_fmt, len(actuals)/len(earnings))
summary.write('A11', '전망'); summary.write_formula('B11', "=COUNTIF('전체 실적'!I2:I405,1)", kpi_value, len(forecasts)); summary.write_formula('C11', '=B11/B12', pct_fmt, len(forecasts)/len(earnings))
summary.write('A12', '합계'); summary.write_formula('B12', '=SUM(B10:B11)', kpi_value, len(earnings)); summary.write_formula('C12', '=SUM(C10:C11)', pct_fmt, 1)
summary.write('E9', '단위', header); summary.write('F9', '행 수', header)
for rr, unit in enumerate(sorted({r['unit'] for r in earnings}), start=9):
    count = sum(1 for r in earnings if r['unit'] == unit)
    summary.write(rr, 4, unit); summary.write_formula(rr, 5, f'=COUNTIF(\'전체 실적\'!N2:N405,E{rr+1})', kpi_value, count)

summary.merge_range('A15:H15', '사용 시 주의사항', section)
notes = [
    '확정 실적: 2020-Q1~2026-Q2, 전망치: 2026-Q3 이후. is_forecast 열이 최종 판별 기준입니다.',
    'B_USD와 T_KRW가 혼재하므로 서로 다른 unit 값은 직접 합산하지 마십시오.',
    '빈 셀은 DB에 값이 없는 항목입니다. 0으로 해석하지 마십시오.',
    'source 열은 DB 원문을 그대로 보존했습니다. URL이 아닌 설명형 출처도 포함될 수 있습니다.',
]
for idx, n in enumerate(notes, start=16): summary.merge_range(idx-1, 0, idx-1, 7, '• ' + n, note)
summary.set_column('A:A', 18); summary.set_column('B:C', 13); summary.set_column('D:D', 3); summary.set_column('E:E', 18); summary.set_column('F:H', 13)
summary.freeze_panes(3, 0)

columns = [
    ('id','ID'), ('entity_id','기업 ID'), ('name_ko','기업명(한글)'), ('name_en','기업명(영문)'), ('layer','레이어'), ('ticker','티커'), ('period','분기'), ('data_type','구분'), ('is_forecast','전망 플래그'), ('report_date','발표일'),
    ('revenue','매출'), ('op_income','영업이익'), ('net_income','순이익'), ('unit','단위'), ('eps_actual','EPS 실제'), ('eps_consensus','EPS 컨센서스'), ('consensus_revenue','매출 컨센서스'), ('beat_miss_status','Beat/Miss'), ('gross_margin_pct','매출총이익률(%)'), ('op_margin_pct','영업이익률(%)'), ('capex','Capex'),
    ('revenue_breakdown','매출 세부'), ('guidance_next_q','다음 분기 가이던스'), ('key_takeaways','핵심 포인트'), ('source','출처'), ('created_at','생성일시')
]

def write_earnings_sheet(name, rows, tab_color):
    ws = wb.add_worksheet(name)
    ws.hide_gridlines(2); ws.set_tab_color(tab_color); ws.freeze_panes(1, 6)
    data = [[r.get(k) for k, _ in columns] for r in rows]
    table_cols = [{'header': h, 'header_format': header} for _, h in columns]
    ws.add_table(0, 0, len(data), len(columns)-1, {'name': 'T_' + name.replace(' ', '_'), 'columns': table_cols, 'data': data, 'style': 'Table Style Medium 2'})
    widths = [8,17,16,19,18,12,11,8,11,12,14,14,14,10,12,14,16,14,16,16,14,28,32,38,48,20]
    for i, w in enumerate(widths): ws.set_column(i, i, w)
    ws.set_row(0, 32)
    for idx in [10,11,12,14,15,16,20]: ws.set_column(idx, idx, widths[idx], num_fmt)
    for idx in [18,19]: ws.set_column(idx, idx, widths[idx], pct_fmt)
    ws.set_column(21, 24, None, wrap_fmt)
    if data:
        ws.conditional_format(1, 7, len(data), 7, {'type': 'text', 'criteria': 'containing', 'value': '전망', 'format': forecast_fmt})
        ws.conditional_format(1, 7, len(data), 7, {'type': 'text', 'criteria': 'containing', 'value': '확정', 'format': actual_fmt})
        for ri, r in enumerate(rows, start=1):
            src = r.get('source') or ''
            if isinstance(src, str) and src.startswith(('http://','https://')):
                ws.write_url(ri, 24, src, link_fmt, src)
    return ws

write_earnings_sheet('전체 실적', earnings, navy)
write_earnings_sheet('확정 실적', actuals, '#70AD47')
write_earnings_sheet('전망치', forecasts, '#FFC000')

ent = wb.add_worksheet('기업 마스터'); ent.hide_gridlines(2); ent.freeze_panes(1, 2); ent.set_tab_color('#A5A5A5')
ent_cols = [('entity_id','기업 ID'),('name_ko','기업명(한글)'),('name_en','기업명(영문)'),('layer','레이어'),('country','국가'),('ticker','티커'),('is_public','상장 여부'),('description','설명'),('created_at','생성일시'),('updated_at','수정일시')]
ent_data = [[r.get(k) for k,_ in ent_cols] for r in entities]
ent.add_table(0,0,len(ent_data),len(ent_cols)-1,{'name':'T_Entities','columns':[{'header':h,'header_format':header} for _,h in ent_cols],'data':ent_data,'style':'Table Style Medium 2'})
for i,w in enumerate([18,18,22,20,12,13,11,48,20,20]): ent.set_column(i,i,w, wrap_fmt if i==7 else text_fmt)
ent.set_row(0,32)

dd = wb.add_worksheet('데이터 사전'); dd.hide_gridlines(2); dd.set_tab_color('#5B9BD5')
dd.set_row(0,30); dd.merge_range('A1:E1','데이터 사전 및 품질 메모',title)
dd.write_row('A3',['필드','한글명','형식/단위','설명','주의사항'],header)
descs = {
 'period':('YYYY-QN','회계 분기','예: 2026-Q2'), 'is_forecast':('0/1','확정/전망 판별','0=확정, 1=전망'),
 'revenue':('숫자','매출','unit 열과 함께 해석'), 'op_income':('숫자','영업이익','빈 셀은 미수집'), 'net_income':('숫자','순이익','빈 셀은 미수집'),
 'unit':('텍스트','금액 단위','B_USD=십억 달러, T_KRW=조 원'), 'gross_margin_pct':('퍼센트포인트','매출총이익률','65.4는 65.4%'),
 'op_margin_pct':('퍼센트포인트','영업이익률','25.0은 25.0%'), 'capex':('숫자','설비투자','unit 열과 함께 해석'),
 'source':('텍스트/URL','출처','DB 원문 유지'), 'report_date':('날짜 텍스트','발표일','DB 원문 유지'),
}
for ri,(key,label) in enumerate(columns,start=3):
    fmt,meaning,caution = descs.get(key,('텍스트/숫자',label,''))
    dd.write_row(ri-1,0,[key,label,fmt,meaning,caution],wrap_fmt)
dd.set_column('A:A',24); dd.set_column('B:B',24); dd.set_column('C:C',20); dd.set_column('D:D',38); dd.set_column('E:E',42); dd.freeze_panes(3,0)

wb.close()
print(OUT)
