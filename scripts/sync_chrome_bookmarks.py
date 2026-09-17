#!/usr/bin/env python3
"""
scripts/sync_chrome_bookmarks.py
크롬 브라우저 북마크에서 10_실적 ~ 40_계약 폴더를 추출하여
docs/bookmarks_feed.md 및 99.raw/ 하위 인덱스로 자동 동기화하는 스크립트.
"""

import os
import json
import datetime
from pathlib import Path

CHROME_BOOKMARKS_PATH = os.path.expanduser(
    "~/Library/Application Support/Google/Chrome/Default/Bookmarks"
)
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = WORKSPACE_ROOT / "docs"
RAW_DIR = WORKSPACE_ROOT / "99.raw"

TARGET_FOLDERS = {
    "10_실적": {
        "raw_dir": RAW_DIR / "financials",
        "category_ko": "실적 및 재무 (Financials)",
        "db_table": "quarterly_earnings / financials"
    },
    "20_마일스톤": {
        "raw_dir": RAW_DIR / "milestones",
        "category_ko": "기술 로드맵 및 사건 (Milestones)",
        "db_table": "milestones"
    },
    "30_전략": {
        "raw_dir": RAW_DIR / "strategy",
        "category_ko": "기업 전략 및 밸류체인 분석 (Strategy)",
        "db_table": "entity_strategy"
    },
    "40_계약": {
        "raw_dir": RAW_DIR / "contracts",
        "category_ko": "공급·컴퓨팅·투자 계약 (Contracts)",
        "db_table": "contracts / datacenter_capacity"
    }
}

def chrome_timestamp_to_datetime(ts_str):
    """크롬 마이크로초 타임스탬프 (1601-01-01 기준)를 YYYY-MM-DD 포맷으로 변환"""
    try:
        ts = int(ts_str)
        epoch_start = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
        dt = epoch_start + datetime.timedelta(microseconds=ts)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return "N/A"

def extract_target_folders(node, targets):
    results = {}
    if node.get("type") == "folder":
        folder_name = node.get("name", "")
        if folder_name in targets:
            results[folder_name] = []
            for child in node.get("children", []):
                if child.get("type") == "url":
                    results[folder_name].append({
                        "name": child.get("name", "No Title"),
                        "url": child.get("url", ""),
                        "date_added": chrome_timestamp_to_datetime(child.get("date_added", 0)),
                        "raw_date_added": child.get("date_added", 0)
                    })
        for child in node.get("children", []):
            if child.get("type") == "folder":
                sub = extract_target_folders(child, targets)
                for k, v in sub.items():
                    results[k] = v
    return results

def main():
    if not os.path.exists(CHROME_BOOKMARKS_PATH):
        print(f"[ERROR] 크롬 북마크 파일을 찾을 수 없습니다: {CHROME_BOOKMARKS_PATH}")
        return

    with open(CHROME_BOOKMARKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    roots = data.get("roots", {})
    all_bookmarks = {}
    for _, root_node in roots.items():
        extracted = extract_target_folders(root_node, TARGET_FOLDERS.keys())
        for k, v in extracted.items():
            all_bookmarks[k] = v

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. docs/bookmarks_feed.md 생성
    feed_md_path = DOCS_DIR / "bookmarks_feed.md"
    total_count = sum(len(items) for items in all_bookmarks.values())
    
    lines = [
        "# 브라우저 북마크 인텔리전스 피드 (10_실적 ~ 40_계약)",
        "",
        f"**동기화 일시**: `{now_str}`  ",
        f"**북마크 소스**: `{CHROME_BOOKMARKS_PATH}`  ",
        f"**총 수집 항목**: `{total_count}건`  ",
        "",
        "> 이 문서는 사용자 크롬 브라우저의 `10_실적` ~ `40_계약` 북마크 폴더를 자동으로 스캔하여 생성된 원천 인텔리전스 인덱스입니다.  ",
        "> 각 북마크는 `99.raw/`의 해당 카테고리와 매핑되며, 핵심 수치는 SQLite DB(`data/memory_claude.db`)로 추출·적재됩니다.",
        "",
        "---",
        ""
    ]

    for folder_name, meta in TARGET_FOLDERS.items():
        items = all_bookmarks.get(folder_name, [])
        lines.append(f"## 📁 {folder_name} — {meta['category_ko']} ({len(items)}건)")
        lines.append(f"- **연계 디렉터리**: `99.raw/{meta['raw_dir'].name}/`")
        lines.append(f"- **주요 DB 테이블**: `{meta['db_table']}`")
        lines.append("")
        lines.append("| No | 제목 | 저장일자 | 링크 |")
        lines.append("|---|---|:---:|---|")
        for idx, item in enumerate(items, 1):
            clean_title = item['name'].replace("|", "-").strip()
            lines.append(f"| {idx} | **{clean_title}** | `{item['date_added']}` | [원문보기]({item['url']}) |")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(feed_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[SUCCESS] {feed_md_path} 생성 완료 (총 {total_count}건)")

    # 2. 99.raw/ 하위 카테고리별 bookmarks_index.json 내보내기 (기존 파일 침범 없음)
    for folder_name, meta in TARGET_FOLDERS.items():
        meta["raw_dir"].mkdir(parents=True, exist_ok=True)
        items = all_bookmarks.get(folder_name, [])
        index_file = meta["raw_dir"] / "bookmarks_index.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump({
                "folder": folder_name,
                "category": meta["category_ko"],
                "updated_at": now_str,
                "count": len(items),
                "items": items
            }, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] {index_file} 갱신 완료 ({len(items)}건)")

if __name__ == "__main__":
    main()
