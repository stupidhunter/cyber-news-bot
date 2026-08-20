#!/usr/bin/env python3
"""Kiểm tra nhanh xem các nguồn trong src/config.py còn hoạt động không.

Cách dùng:
    python scripts/check_feeds.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src import fetchers  # noqa: E402
from src.config import SOURCES  # noqa: E402


def check_one(src: dict) -> tuple[bool, str]:
    try:
        if src["type"] == "rss":
            items = fetchers.fetch_rss(src["url"], src["name"], limit=3)
        elif src["type"] == "kev":
            items = fetchers.fetch_kev(src["urls"])
        elif src["type"] == "nvd":
            items = fetchers.fetch_nvd(src["url"], lookback_hours=24)
        else:
            return False, f"type không hợp lệ: {src['type']}"
        first = items[0]["title"][:90] if items else "(feed rỗng — không có entry)"
        return True, f"{len(items)} tin | ví dụ: {first}"
    except Exception as e:  # noqa: BLE001
        return False, str(e)[:200]


def main() -> int:
    ok = fail = 0
    for src in SOURCES:
        good, msg = check_one(src)
        status = "OK  " if good else "FAIL"
        print(f"{status} {src['name']}: {msg}")
        ok += good
        fail += not good
    print(f"\n==> {ok} OK, {fail} FAIL")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
