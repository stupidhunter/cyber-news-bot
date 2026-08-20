#!/usr/bin/env python3
"""Điểm vào chính: thu thập tin, lưu lịch sử, gửi Telegram, sinh trang web.

Cách dùng:
  python src/collect.py                  # chạy đầy đủ (dùng trong GitHub Actions)
  python src/collect.py --dry-run        # không gửi Telegram, in digest ra stdout
  python src/collect.py --test-telegram  # gửi tin nhắn test rồi thoát
  python src/collect.py --no-telegram --no-site   # chỉ thu thập + lưu

Biến môi trường:
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SITE_URL, DATA_DIR, SITE_DIR,
  MAX_ITEMS, LOOKBACK_HOURS
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from collections import Counter

from . import sitegen, telegram
from .classify import classify, is_vi_security
from .config import SOURCES
from .fetchers import fetch_kev, fetch_nvd, fetch_rss
from .models import NewsItem
from .store import Store

log = logging.getLogger("collect")


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def fetch_all(store: Store, lookback_hours: int) -> tuple[list, list]:
    """Thu thập tất cả nguồn. Trả về (tin mới, danh sách lỗi)."""
    all_new: list[NewsItem] = []
    errors: list[str] = []
    for src in SOURCES:
        try:
            if src["type"] == "rss":
                raw = fetch_rss(src["url"], src["name"])
            elif src["type"] == "kev":
                raw = fetch_kev(src["urls"])
            elif src["type"] == "nvd":
                raw = fetch_nvd(src["url"], lookback_hours=lookback_hours)
            else:
                continue
            items: list[NewsItem] = []
            for r in raw:
                text = f'{r.get("title", "")} {r.get("summary", "")}'
                if src.get("security_only") and not is_vi_security(text):
                    continue  # bỏ tin tiếng Việt không liên quan bảo mật
                items.append(
                    NewsItem(
                        source=r["source"],
                        title=r["title"],
                        link=r["link"],
                        published=r["published"],
                        summary=r.get("summary", ""),
                        categories=classify(text, src["categories"]),
                        lang=src["lang"],
                        extra=r.get("extra", {}),
                    )
                )
            fresh = store.add_new(items)
            all_new.extend(fresh)
            log.info("%-22s đọc %2d | mới %2d", src["name"], len(items), len(fresh))
        except Exception as e:  # noqa: BLE001
            errors.append(f"{src['name']}: {e}")
            log.warning("LỖI %s: %s", src["name"], e)
    return all_new, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Cyber News Bot")
    ap.add_argument("--dry-run", action="store_true",
                    help="không gửi Telegram, in digest ra stdout")
    ap.add_argument("--test-telegram", action="store_true",
                    help="gửi tin nhắn test tới Telegram rồi thoát")
    ap.add_argument("--no-site", action="store_true", help="không sinh trang web")
    ap.add_argument("--no-telegram", action="store_true", help="không gửi Telegram")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    data_dir = os.environ.get("DATA_DIR", "data")
    site_dir = os.environ.get("SITE_DIR", "docs")
    max_items = _env_int("MAX_ITEMS", 4000)
    lookback = _env_int("LOOKBACK_HOURS", 12)
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    site_url = os.environ.get("SITE_URL", "")

    if args.test_telegram:
        if not token or not chat_id:
            log.error("Cần TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID")
            return 2
        telegram.send_test(token, chat_id)
        print("OK: đã gửi tin nhắn test.")
        return 0

    store = Store(os.path.join(data_dir, "items.json"), max_items=max_items)
    all_new, errors = fetch_all(store, lookback)

    counts = Counter(it.categories[0] for it in all_new if it.categories)
    summary = ", ".join(f"{c}={n}" for c, n in counts.most_common())
    log.info("==> Tin mới kỳ này: %d (%s)", len(all_new), summary or "không có")

    # Sinh trang web
    if not args.no_site:
        site_path = os.path.join(site_dir, "index.html")
        sitegen.generate(store.items, site_path)
        log.info("Đã sinh trang web: %s (%d tin)", site_path, len(store.items))

    # Gửi Telegram
    sent = 0
    if not args.no_telegram:
        if args.dry_run:
            if all_new:
                for m in telegram.build_kev_alert(all_new) + telegram.build_messages(all_new, site_url):
                    print("\n" + "=" * 60 + "\n" + m)
            else:
                print("(dry-run) Không có tin mới trong kỳ này.")
        else:
            if not token or not chat_id:
                log.error("Thiếu TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID — bỏ qua gửi")
            elif all_new:
                try:
                    sent = telegram.send_digest(token, chat_id, all_new, site_url)
                    log.info("Đã gửi %d tin nhắn tới Telegram", sent)
                except Exception as e:  # noqa: BLE001
                    errors.append(f"Telegram: {e}")
                    log.error("Gửi Telegram thất bại: %s", e)
            else:
                log.info("Không có tin mới — không gửi Telegram (tránh spam).")

    if errors:
        log.warning("Có %d lỗi: %s", len(errors), "; ".join(errors))
    # Exit 1 nếu KHÔNG nguồn nào hoạt động hoặc Telegram lỗi
    if not all_new and len(errors) >= len(SOURCES):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
