#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT = Path('/Users/boon/Dropbox/03_code/b_0910_memory_claude')
sys.path.insert(0, str(ROOT / 'scripts'))
import populate_p0_sec_earnings as p0

TARGETS = {
    'AMD': '0000002488',
    'BROADCOM': '0001730168',
    'MICRON': '0000723125',
    'ORACLE': '0001341439',
    'WDC': '0000106040',
    'MARVELL': '0001835632',
    'COHERENT': '0000820318',
    'APPLE': '0000320193',
    'EATON': '0001551182',
    'GE_VERNOVA': '0001996810'
}

for entity_id, cik in TARGETS.items():
    path = p0.download(entity_id, cik, refresh=False)
    with open(path) as f:
        data = p0.json.load(f)
    rows = p0.build_rows(entity_id, cik, data, path)
    print(f"=== {entity_id} ({len(rows)} quarters) ===")
    for r in rows[-4:]:
        op = f"${r['op_income']:.2f}B" if r['op_income'] is not None else "N/A"
        print(f"  {r['period']} | Rev: ${r['revenue']:.2f}B | OpInc: {op} | OPM: {r['op_margin_pct']}% | GPM: {r['gross_margin_pct']}% | Date: {r['report_date']}")
