"""Sinh trang web tĩnh docs/index.html (GitHub Pages) từ lịch sử tin tức."""
from __future__ import annotations

import html as html_mod
import os
from collections import defaultdict
from datetime import datetime, timezone

from .config import CATEGORIES, CATEGORY_ORDER
from .models import NewsItem

BADGE = {
    "kev": ("KEV", "#dc2626"),
    "cve": ("CVE", "#ea580c"),
    "breach": ("Breach", "#9333ea"),
    "ai": ("AI", "#2563eb"),
    "cloud": ("Cloud", "#0891b2"),
    "vietnamese": ("VN", "#16a34a"),
    "general": ("News", "#64748b"),
}


def _esc(s: str) -> str:
    return html_mod.escape(s, quote=False)


def _fmt(iso: str) -> str:
    try:
        return (
            datetime.fromisoformat(iso)
            .astimezone(timezone.utc)
            .strftime("%d/%m/%Y %H:%M UTC")
        )
    except Exception:
        return iso


def generate(items: list[NewsItem], out_path: str,
             site_title: str = "Cyber News Bot") -> None:
    """Viết docs/index.html hiển thị tối đa MAX_SHOW tin mới nhất."""
    MAX_SHOW = 400
    show = items[:MAX_SHOW]

    by_date: dict[str, list] = defaultdict(list)
    for it in show:
        by_date[it.date].append(it)
    dates = sorted(by_date.keys(), reverse=True)

    rows_html = []
    for d in dates:
        rows_html.append(f'<h2 class="date">{_esc(d)}</h2>')
        for it in by_date[d]:
            cats = [c for c in CATEGORY_ORDER if c in it.categories]
            cat = cats[0] if cats else "general"
            label, color = BADGE.get(cat, BADGE["general"])
            extra = ""
            if it.extra.get("cvss"):
                extra = f'<span class="cvss">CVSS {_esc(str(it.extra["cvss"]))}</span>'
            rows_html.append(
                '<div class="item">'
                f'<span class="badge" style="background:{color}">{label}</span>'
                f'<a class="title" href="{_esc(it.link)}" target="_blank" rel="noopener">{_esc(it.title)}</a>'
                f'<span class="meta">{_esc(it.source)} · {_esc(_fmt(it.published))}</span>'
                f'{extra}'
                "</div>"
            )
    items_html = "\n".join(rows_html) if rows_html else "<p>Chưa có dữ liệu.</p>"

    today = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    html_doc = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(site_title)}</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
         background:#0f172a; color:#e2e8f0; }}
  header {{ padding:24px 20px 16px; background:#111c33; border-bottom:1px solid #1e293b; }}
  h1 {{ margin:0 0 4px; font-size:22px; }}
  .sub {{ color:#94a3b8; font-size:13px; }}
  .search {{ margin-top:12px; }}
  input {{ width:100%; max-width:420px; padding:10px 14px; border-radius:8px;
           border:1px solid #334155; background:#0b1220; color:#e2e8f0; font-size:14px; }}
  main {{ max-width:860px; margin:0 auto; padding:20px; }}
  .date {{ color:#7dd3fc; font-size:15px; margin:22px 0 8px; border-bottom:1px solid #1e293b; padding-bottom:6px; }}
  .item {{ padding:8px 4px; border-bottom:1px solid #16213a; display:flex; flex-wrap:wrap;
           align-items:baseline; gap:6px; }}
  .badge {{ color:#fff; font-size:10px; font-weight:700; padding:2px 8px; border-radius:10px;
            flex:none; }}
  .title {{ color:#38bdf8; text-decoration:none; font-size:14.5px; }}
  .title:hover {{ text-decoration:underline; }}
  .meta {{ color:#64748b; font-size:12px; }}
  .cvss {{ color:#fbbf24; font-size:11px; font-weight:600; }}
  footer {{ text-align:center; color:#475569; font-size:12px; padding:24px; }}
  .hide {{ display:none !important; }}
</style>
</head>
<body>
<header>
  <h1>🛡️ {_esc(site_title)}</h1>
  <div class="sub">Cập nhật mỗi 4 giờ · {len(show)} tin gần nhất · {_esc(today)}</div>
  <div class="search">
    <input id="q" type="search" placeholder="Tìm theo tiêu đề, nguồn, danh mục...">
  </div>
</header>
<main id="list">
{items_html}
</main>
<footer>Nguồn: NVD, CISA KEV, The Hacker News, SecurityWeek, Krebs, DarkReading, DataBreaches.net, AWS, Cloudflare, CSA, VnExpress, Znews, GenK, Dân Trí, VTC, VietnamNet, Thanh Niên, TTXVN, Tuổi Trẻ... — tự động thu thập mỗi 4 giờ.</footer>
<script>
  const q = document.getElementById('q');
  q.addEventListener('input', () => {{
    const k = q.value.toLowerCase().trim();
    document.querySelectorAll('.item').forEach(el => {{
      el.classList.toggle('hide', k && !el.textContent.toLowerCase().includes(k));
    }});
    document.querySelectorAll('.date').forEach(el => {{
      let any = false;
      let sib = el.nextElementSibling;
      while (sib && sib.classList.contains('item')) {{
        if (!sib.classList.contains('hide')) any = true;
        sib = sib.nextElementSibling;
      }}
      el.classList.toggle('hide', k && !any);
    }});
  }});
</script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
