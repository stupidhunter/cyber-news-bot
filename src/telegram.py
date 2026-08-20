"""Gửi điểm tin ngắn gọn qua Telegram Bot API."""
from __future__ import annotations

import html as html_mod
import json
import logging
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from .classify import best_category
from .config import CATEGORIES, CATEGORY_ORDER

log = logging.getLogger("telegram")

MAX_MSG = 3800  # Telegram giới hạn 4096 ký tự, chừa chút an toàn
MAX_PER_CAT = 10


def _esc(t: str) -> str:
    return html_mod.escape(t, quote=False)


def _link(title: str, url: str) -> str:
    return f'<a href="{url}">{_esc(title)}</a>'


def _fmt_time(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).astimezone(timezone.utc).strftime("%d/%m %H:%M")
    except Exception:
        return ""


def _item_line(it) -> str:
    title = it.title_vi or it.title
    line = f"• {_link(title, it.link)} <i>— {_esc(it.source)}</i>"
    t = _fmt_time(it.published)
    if t:
        line += f" <i>({t})</i>"
    if it.extra.get("due_date"):
        line += f" ⏰<i>{_esc(it.extra['due_date'])}</i>"
    elif it.extra.get("cvss"):
        try:
            line += f" 🔥<i>CVSS {float(it.extra['cvss']):.1f}</i>"
        except Exception:
            line += f" 🔥<i>CVSS {_esc(str(it.extra['cvss']))}</i>"
    return line


def build_messages(items: list, site_url: str = "") -> list[str]:
    """Chia điểm tin thành 1..n tin nhắn (mỗi tin nhắn <= MAX_MSG ký tự)."""
    groups = {c: [] for c in CATEGORY_ORDER}
    for it in items:
        groups[best_category(it.categories)].append(it)

    header = f"🛡️ <b>Cyber News Digest</b> — {len(items)} tin mới\n"
    msgs: list[str] = []
    buf = header
    for cat in CATEGORY_ORDER:
        g = groups[cat]
        if not g:
            continue
        emoji, label = CATEGORIES[cat][1], CATEGORIES[cat][0]
        block = [f"\n{emoji} <b>{label}</b> ({len(g)})"]
        for it in g[:MAX_PER_CAT]:
            block.append(_item_line(it))
        chunk = "\n".join(block)
        if len(buf) + len(chunk) > MAX_MSG and buf.strip() != header.strip():
            msgs.append(buf.rstrip())
            buf = header + "\n<i>(tiếp theo)</i>"
        buf += chunk

    if site_url:
        buf += f"\n\n📊 Xem đầy đủ: {_esc(site_url)}"
    msgs.append(buf.rstrip())
    return [m for m in msgs if m.strip()]


def build_kev_alert(items: list) -> list[str]:
    """Cảnh báo riêng cho lỗ hổng đang bị khai thác (được gửi trước digest)."""
    kev = [it for it in items if "kev" in it.categories]
    if not kev:
        return []
    lines = ["🚨 <b>ALERT: Lỗ hổng MỚI đang bị khai thác (CISA KEV)</b>"]
    for it in kev[:10]:
        title = it.title_vi or it.title
        lines.append(f"• {_link(title, it.link)}")
        if it.extra.get("required_action"):
            action = _esc(it.extra["required_action"])[:140]
            lines.append(f"   <i>{action}</i>")
    return ["\n".join(lines)]


def send_message(token: str, chat_id: str, text: str,
                 parse_mode: str = "HTML") -> dict:
    """Gửi 1 tin nhắn tới Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API lỗi: {data.get('description')}")
    return data


def send_digest(token: str, chat_id: str, items: list,
                site_url: str = "", dry_run: bool = False) -> int:
    """Gửi alert KEV (nếu có) rồi điểm tin. Trả về số tin nhắn đã gửi."""
    msgs: list[str] = []
    msgs += build_kev_alert(items)
    msgs += build_messages(items, site_url)
    sent = 0
    for m in msgs:
        if dry_run:
            log.info("---- DRY RUN message ----\n%s", m)
        else:
            send_message(token, chat_id, m)
        sent += 1
    return sent


def send_test(token: str, chat_id: str) -> None:
    """Gửi tin nhắn kiểm tra kết nối."""
    send_message(
        token, chat_id,
        "✅ <b>Cyber News Bot hoạt động!</b>\n"
        "Kết nối Telegram thành công. Tin tức sẽ được gửi mỗi 4 giờ.",
    )
