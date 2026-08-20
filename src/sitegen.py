"""Sinh trang web tĩnh docs/index.html (GitHub Pages) từ lịch sử tin tức."""
from __future__ import annotations

import html as html_mod
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from string import Template

from .classify import best_category
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
EMOJI = {"kev": "⚠️", "cve": "🔴", "breach": "🕳️", "ai": "🤖",
         "cloud": "☁️", "vietnamese": "🇻🇳", "general": "📰"}


def _esc(s: str) -> str:
    return html_mod.escape(s, quote=False)


def _fmt(iso: str, with_year: bool = True) -> str:
    try:
        fmt = "%d/%m/%Y %H:%M" if with_year else "%d/%m %H:%M"
        return (
            datetime.fromisoformat(iso)
            .astimezone(timezone.utc)
            .strftime(fmt) + " UTC"
        )
    except Exception:
        return iso


def _label(date_str: str, today: str, yesterday: str) -> str:
    if date_str == today:
        return "📅 Hôm nay"
    if date_str == yesterday:
        return "📅 Hôm qua"
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return f"📅 {d.strftime('%d/%m/%Y')}"


def generate(items: list[NewsItem], out_path: str,
             site_title: str = "Cyber News Bot") -> None:
    """Viết docs/index.html: dashboard + lọc theo danh mục + tìm kiếm."""
    MAX_SHOW = 400
    # 400 tin MỚI NHẤT theo ngày đăng (không phải thứ tự thu thập)
    shown = sorted(items, key=lambda x: x.published, reverse=True)[:MAX_SHOW]
    total_store = len(items)
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    # Nhóm theo ngày; trong mỗi ngày sắp theo giờ đăng mới nhất
    by_date: dict[str, list] = defaultdict(list)
    for it in sorted(shown, key=lambda x: x.published, reverse=True):
        by_date[it.date].append(it)
    dates = sorted(by_date.keys(), reverse=True)

    # Thống kê
    cats = [best_category(it.categories) for it in shown]
    cat_counts = Counter(cats)
    today_count = sum(1 for it in shown if it.date == today)
    kev_count = cat_counts.get("kev", 0)

    # --- Thẻ thống kê ---
    stat_defs = [
        ("Tổng hiển thị", str(len(shown)), "#38bdf8"),
        ("Hôm nay", str(today_count), "#4ade80"),
        ("Đang khai thác (KEV)", str(kev_count), "#f87171"),
        ("CVE mới", str(cat_counts.get("cve", 0)), "#fb923c"),
        ("Breach/Ransomware", str(cat_counts.get("breach", 0)), "#c084fc"),
        ("AI Security", str(cat_counts.get("ai", 0)), "#60a5fa"),
        ("Cloud Security", str(cat_counts.get("cloud", 0)), "#22d3ee"),
        ("Tin tiếng Việt", str(cat_counts.get("vietnamese", 0)), "#4ade80"),
    ]
    stats_html = "\n".join(
        f'<div class="stat"><span class="stat-num" style="color:{c}">{_esc(v)}</span>'
        f'<span class="stat-label">{_esc(k)}</span></div>'
        for k, v, c in stat_defs
    )

    # --- Banner KEV ---
    kev_banner = ""
    if kev_count:
        kev_banner = (
            '<div class="kev-banner">🚨 <b>'
            f'{kev_count} lỗ hổng đang bị khai thác ngoài thực tế (CISA KEV)</b>'
            " — ưu tiên kiểm tra & vá ngay. Xem mục ⚠️ KEV bên dưới.</div>"
        )

    # --- Nút lọc danh mục ---
    pills = ['<button class="pill active" data-cat="all">Tất cả'
             f'<span class="pill-n">{len(shown)}</span></button>']
    for cat in CATEGORY_ORDER:
        n = cat_counts.get(cat, 0)
        if not n:
            continue
        _, color = BADGE[cat]
        pills.append(
            f'<button class="pill" data-cat="{cat}" style="--c:{color}">'
            f'{EMOJI[cat]} {CATEGORIES[cat][0]}'
            f'<span class="pill-n">{n}</span></button>'
        )
    pills_html = "\n".join(pills)

    # --- Danh sách tin ---
    rows = []
    for d in dates:
        rows.append(f'<h2 class="date">{_esc(_label(d, today, yesterday))}'
                    f'<span class="date-count">{len(by_date[d])} tin</span></h2>')
        for it in by_date[d]:
            cats_it = [c for c in CATEGORY_ORDER if c in it.categories]
            cat = cats_it[0] if cats_it else "general"
            label, color = BADGE.get(cat, BADGE["general"])
            chips = []
            if it.extra.get("cvss"):
                try:
                    chips.append(f'<span class="chip cvss">🔥 CVSS {float(it.extra["cvss"]):.1f}</span>')
                except Exception:
                    chips.append(f'<span class="chip cvss">🔥 CVSS {_esc(str(it.extra["cvss"]))}</span>')
            if it.extra.get("due_date"):
                chips.append(f'<span class="chip due">⏰ Hạn: {_esc(it.extra["due_date"])}</span>')
            if it.extra.get("vendor"):
                chips.append(f'<span class="chip vendor">{_esc(it.extra["vendor"])}</span>')
            chips_html = "".join(chips)
            title = it.title_vi or it.title
            orig = ""
            if it.title_vi and it.title_vi != it.title:
                orig = f'<span class="orig">EN: {_esc(it.title)}</span>'
            rows.append(
                f'<div class="item" data-cat="{cat}" data-date="{d}">'
                f'<span class="badge" style="--c:{color}">{label}</span>'
                f'<a class="title" href="{_esc(it.link)}" target="_blank" rel="noopener">{_esc(title)}</a>'
                f'{chips_html}'
                f'<span class="meta">{_esc(it.source)} · {_esc(_fmt(it.published, with_year=False))}{orig}</span>'
                f'</div>'
            )
    items_html = "\n".join(rows) if rows else "<p>Chưa có dữ liệu.</p>"
    empty_html = '<div id="empty" class="empty hide">🔍 Không tìm thấy tin nào khớp.</div>'

    page = Template(HTML_TEMPLATE).substitute(
        site_title=_esc(site_title),
        stats_html=stats_html,
        kev_banner=kev_banner,
        pills_html=pills_html,
        items_html=items_html,
        empty_html=empty_html,
        total_store=str(total_store),
        updated=_fmt(now.isoformat()),
    )

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$site_title</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🛡️</text></svg>">
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
         background:#0a0f1e; color:#e2e8f0; }
  a { color:inherit; text-decoration:none; }

  header { background:linear-gradient(135deg,#0b1220 0%,#14213d 55%,#1d2b52 100%);
           border-bottom:1px solid #1e293b; padding:28px 20px 18px; }
  .wrap { max-width:900px; margin:0 auto; }
  h1 { margin:0; font-size:26px; letter-spacing:.3px; }
  .sub { color:#94a3b8; font-size:13px; margin-top:6px; }
  .search { margin-top:16px; position:relative; max-width:520px; }
  .search input { width:100%; padding:12px 16px 12px 42px; border-radius:12px;
           border:1px solid #2b3a5c; background:#0b1220; color:#e2e8f0;
           font-size:15px; outline:none; transition:border .15s, box-shadow .15s; }
  .search input:focus { border-color:#38bdf8; box-shadow:0 0 0 3px rgba(56,189,248,.15); }
  .search::before { content:'🔍'; position:absolute; left:14px; top:50%;
           transform:translateY(-50%); font-size:15px; opacity:.7; }

  .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr));
           gap:10px; margin-top:18px; }
  .stat { background:#111a30; border:1px solid #1e2a4a; border-radius:12px;
          padding:12px 14px; }
  .stat-num { display:block; font-size:22px; font-weight:800; }
  .stat-label { display:block; color:#8ea0c0; font-size:11.5px; margin-top:2px; }

  .kev-banner { margin-top:16px; background:#3b0f14; border:1px solid #7f1d1d;
          color:#fecaca; border-radius:12px; padding:12px 16px; font-size:14px; }

  .pills { display:flex; flex-wrap:wrap; gap:8px; margin:16px 0 6px; }
  .pill { display:inline-flex; align-items:center; gap:6px; padding:7px 14px;
          border-radius:999px; border:1px solid #26355a; background:#111a30;
          color:#cbd5e1; font-size:13px; cursor:pointer; transition:all .15s; }
  .pill:hover { border-color:#38bdf8; }
  .pill.active { background:var(--c,#38bdf8); border-color:var(--c,#38bdf8); color:#fff; }
  .pill-n { background:rgba(255,255,255,.15); border-radius:999px; padding:1px 8px;
            font-size:11.5px; font-weight:700; }

  main { max-width:900px; margin:0 auto; padding:6px 20px 40px; }
  .date { position:sticky; top:0; z-index:5; background:rgba(10,15,30,.92);
          backdrop-filter:blur(6px); color:#7dd3fc; font-size:14.5px;
          margin:22px 0 10px; padding:8px 0 8px; border-bottom:1px solid #1e2a4a; }
  .date-count { color:#64748b; font-weight:400; margin-left:8px; font-size:12px; }

  .item { background:#111a30; border:1px solid #1c2745; border-radius:12px;
          padding:12px 16px; margin-bottom:8px; display:flex; flex-wrap:wrap;
          align-items:center; gap:8px 10px; transition:border-color .15s, transform .12s;
          animation:fadeIn .35s ease both; }
  .item:hover { border-color:#38bdf8; transform:translateX(3px); }
  @keyframes fadeIn { from { opacity:0; transform:translateY(4px);} to { opacity:1; } }
  .badge { color:#fff; font-size:10.5px; font-weight:800; padding:3px 10px;
           border-radius:999px; background:var(--c,#64748b); flex:none; letter-spacing:.4px; }
  .title { color:#dbeafe; font-size:15px; flex:1 1 280px; line-height:1.45; }
  .title:hover { color:#7dd3fc; text-decoration:underline; }
  .chips { display:inline-flex; gap:6px; flex-wrap:wrap; }
  .chip { font-size:11px; font-weight:700; padding:3px 9px; border-radius:8px; }
  .chip.cvss { background:#451a03; color:#fbbf24; }
  .chip.due { background:#3b0f14; color:#fca5a5; }
  .chip.vendor { background:#0c2a3a; color:#67e8f9; }
  .meta { flex-basis:100%; color:#64748b; font-size:11.5px; }
  .orig { color:#7c8db0; font-style:italic; margin-left:6px; }
  .empty { text-align:center; color:#64748b; padding:40px 0; font-size:15px; }
  .hide { display:none !important; }
  footer { text-align:center; color:#475569; font-size:12px; padding:24px; }
</style>
</head>
<body>
<header>
  <div class="wrap">
    <h1>🛡️ $site_title</h1>
    <div class="sub">Tự động thu thập mỗi 4 giờ · hiển thị 400 tin gần nhất
      (tổng lịch sử: $total_store) · cập nhật lúc $updated</div>
    <div class="search"><input id="q" type="search"
      placeholder="Tìm theo tiêu đề, nguồn, từ khóa..."></div>
    <div class="stats">$stats_html</div>
    $kev_banner
    <div class="pills" id="pills">$pills_html</div>
  </div>
</header>
<main>
  $items_html
  $empty_html
</main>
<footer>Nguồn: NVD, CISA KEV, The Hacker News, SecurityWeek, Krebs, DarkReading,
  DataBreaches.net, AWS, Cloudflare, CSA, VnExpress, Znews, GenK, Dân Trí, VTC,
  VietnamNet, Thanh Niên, TTXVN, Tuổi Trẻ... · mã nguồn mở · miễn phí.</footer>
<script>
  var state = { q: '', cat: 'all' };
  var q = document.getElementById('q');
  var pills = document.querySelectorAll('.pill');
  var empty = document.getElementById('empty');

  function apply() {
    var visible = 0;
    document.querySelectorAll('.item').forEach(function (el) {
      var cat = el.getAttribute('data-cat');
      var okCat = state.cat === 'all' || cat === state.cat;
      var okQ = !state.q || el.textContent.toLowerCase().indexOf(state.q) !== -1;
      var show = okCat && okQ;
      el.classList.toggle('hide', !show);
      if (show) visible++;
    });
    document.querySelectorAll('.date').forEach(function (el) {
      var any = false;
      var sib = el.nextElementSibling;
      while (sib && sib.classList.contains('item')) {
        if (!sib.classList.contains('hide')) any = true;
        sib = sib.nextElementSibling;
      }
      el.classList.toggle('hide', !any);
    });
    empty.classList.toggle('hide', visible > 0);
  }

  q.addEventListener('input', function () {
    state.q = q.value.trim().toLowerCase();
    apply();
  });

  pills.forEach(function (p) {
    p.addEventListener('click', function () {
      pills.forEach(function (x) { x.classList.remove('active'); });
      p.classList.add('active');
      state.cat = p.getAttribute('data-cat');
      apply();
    });
  });
</script>
</body>
</html>
"""
