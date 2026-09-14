#!/usr/bin/env python3
"""
serve_dashboard.py
--------------------------------------------------
Memory Claude 인터랙티브 웹 대시보드 로컬 서버.
별도의 외부 패키지 설치 없이 Python 표준 라이브러리(http.server, sqlite3)로 실행됩니다.

사용법:
    python3 scripts/serve_dashboard.py
    브라우저에서 http://localhost:8501 접속
"""

import http.server
import socketserver
import json
import sqlite3
import os
import webbrowser

PORT = 8501
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "memory_claude.db")
WEB_DIR = os.path.join(BASE_DIR, "dashboard")

def get_db_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. entities
    cur.execute("SELECT entity_id, name_ko, layer, ticker, country, description FROM entities ORDER BY layer, name_ko;")
    entities = [dict(row) for row in cur.fetchall()]

    # 2. earnings_reports (시계열)
    cur.execute("""
        SELECT r.entity_id, e.name_ko, r.period, r.report_date, r.revenue, r.op_income, 
               r.op_margin_pct, r.gross_margin_pct, r.beat_miss_status, r.is_forecast,
               r.revenue_breakdown, r.guidance_next_q
        FROM earnings_reports r
        JOIN entities e ON r.entity_id = e.entity_id
        ORDER BY r.entity_id, r.period ASC;
    """)
    earnings = [dict(row) for row in cur.fetchall()]

    # 3. fab_capacity
    cur.execute("""
        SELECT f.*, e.name_ko 
        FROM fab_capacity f
        JOIN entities e ON f.entity_id = e.entity_id
        ORDER BY f.wspm_target DESC;
    """)
    fabs = [dict(row) for row in cur.fetchall()]

    # 4. datacenter_capacity
    cur.execute("""
        SELECT d.*, e.name_ko 
        FROM datacenter_capacity d
        JOIN entities e ON d.entity_id = e.entity_id
        ORDER BY d.power_mw_target DESC;
    """)
    datacenters = [dict(row) for row in cur.fetchall()]

    # 5. milestones
    cur.execute("""
        SELECT m.*, e.name_ko 
        FROM milestones m
        JOIN entities e ON m.entity_id = e.entity_id
        ORDER BY m.event_date ASC;
    """)
    milestones = [dict(row) for row in cur.fetchall()]

    # 6. contracts
    cur.execute("""
        SELECT c.*, eb.name_ko AS buyer_name, es.name_ko AS seller_name
        FROM contracts c
        JOIN entities eb ON c.buyer_id = eb.entity_id
        JOIN entities es ON c.seller_id = es.entity_id
        ORDER BY c.value_b DESC;
    """)
    contracts = [dict(row) for row in cur.fetchall()]

    conn.close()

    return {
        "entities": entities,
        "earnings": earnings,
        "fabs": fabs,
        "datacenters": datacenters,
        "milestones": milestones,
        "contracts": contracts
    }

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data = get_db_data()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        else:
            super().do_GET()

def run():
    os.makedirs(WEB_DIR, exist_ok=True)
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print("="*60)
        print(f"🚀 Memory Claude 인터랙티브 대시보드 서버 실행 중")
        print(f"👉 브라우저 접속 주소: {url}")
        print("종료하려면 터미널에서 Ctrl+C를 누르세요.")
        print("="*60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버를 종료합니다.")

if __name__ == "__main__":
    run()
