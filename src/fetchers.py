"""Lấy dữ liệu từ các nguồn RSS/Atom/JSON."""
from __future__ import annotations

import gzip
import json
import logging
import re
import ssl
import urllib.request
from datetime import datetime, timezone

import certifi
import feedparser

log = logging.getLogger("fetchers")

UA = (
    "Mozilla/5.0 (compatible; CyberNewsBot/1.0; "
    "+https://github.com/yourname/cyber-news-bot)"
)

# Dùng CA bundle của certifi để tránh lỗi chứng chỉ ở môi trường thiếu root CA
_SSL_CTX = ssl.create_default_context(cafile=certifi.where())


def fetch_text(url: str, timeout: int = 25) -> str:
    """GET một URL, trả về nội dung text (tự giải nén gzip nếu cần)."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "*/*",
            "Accept-Encoding": "gzip",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as r:
        data = r.read()
        if (
            r.headers.get("Content-Encoding", "").lower() == "gzip"
            or data[:2] == b"\x1f\x8b"
        ):
            data = gzip.decompress(data)
        return data.decode("utf-8", errors="replace")


def _pub(entry, feed) -> str:
    """Trích thời gian đăng bài -> ISO 8601 UTC."""
    for k in ("published_parsed", "updated_parsed"):
        v = entry.get(k)
        if v:
            try:
                return datetime(*v[:6], tzinfo=timezone.utc).isoformat()
            except Exception:
                pass
    _ = feed
    return datetime.now(timezone.utc).isoformat()


def fetch_rss(url: str, source_name: str, limit: int = 25) -> list[dict]:
    """Đọc một feed RSS/Atom, trả về list các tin (dict thô)."""
    xml = fetch_text(url)
    parsed = feedparser.parse(xml)
    out = []
    for e in parsed.entries[:limit]:
        link = e.get("link") or ""
        title = (e.get("title") or "").strip()
        if not title or not link:
            continue
        summary = re.sub(r"<[^>]+>", " ", e.get("summary") or e.get("description") or "")
        summary = re.sub(r"\s+", " ", summary).strip()[:600]
        out.append(
            {
                "source": source_name,
                "title": title,
                "link": link,
                "published": _pub(e, parsed.feed),
                "summary": summary,
            }
        )
    return out


def _parse_kev(data: dict) -> list[dict]:
    out = []
    for v in data.get("vulnerabilities", []):
        cve = v.get("cveID", "")
        name = v.get("vulnerabilityName", "")
        title = f"{cve} — {name}".strip(" —")
        out.append(
            {
                "source": "CISA KEV",
                "title": title,
                "link": f"https://nvd.nist.gov/vuln/detail/{cve}",
                "published": v.get("dateAdded")
                or datetime.now(timezone.utc).date().isoformat(),
                "summary": (v.get("shortDescription") or "")[:600],
                "extra": {
                    "cve": cve,
                    "vendor": v.get("vendorProject", ""),
                    "product": v.get("product", ""),
                    "due_date": v.get("dueDate", ""),
                    "required_action": v.get("requiredAction", ""),
                },
            }
        )
    return out


def fetch_kev(urls: list[str]) -> list[dict]:
    """Đọc CISA KEV; thử lần lượt nhiều URL (dự phòng mirror)."""
    last_err = None
    for u in urls:
        try:
            return _parse_kev(json.loads(fetch_text(u)))
        except Exception as e:  # noqa: BLE001
            last_err = e
            log.warning("KEV URL thất bại %s: %s", u, e)
    raise last_err  # type: ignore[misc]


def fetch_nvd(url: str, lookback_hours: int = 12) -> list[dict]:
    """Đọc CVE mới công bố từ NVD API v2 (không cần API key)."""
    from datetime import timedelta

    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=lookback_hours)
    full = (
        f"{url}?pubStartDate={start:%Y-%m-%dT%H:%M:%S.000}"
        f"&pubEndDate={end:%Y-%m-%dT%H:%M:%S.999}"
    )
    data = json.loads(fetch_text(full))
    out = []
    for v in data.get("vulnerabilities", []):
        c = v.get("cve", {})
        cid = c.get("id", "")
        if not cid:
            continue
        desc = next(
            (d.get("value", "") for d in c.get("descriptions", [])
             if d.get("lang") == "en"), ""
        )
        score = None
        for mkey in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            m = c.get("metrics", {}).get(mkey)
            if m:
                score = m[0].get("cvssData", {}).get("baseScore")
                break
        ref = ""
        refs = c.get("references", [])
        if refs:
            ref = refs[0].get("url", "")
        title = cid
        if desc:
            short = re.sub(r"\s+", " ", desc.split(".")[0].strip())[:150]
            if short:
                title = f"{cid} — {short}"
        out.append(
            {
                "source": "NVD",
                "title": title,
                "link": f"https://nvd.nist.gov/vuln/detail/{cid}",
                "published": c.get("published") or start.isoformat(),
                "summary": desc[:600],
                "extra": {"cve": cid, "cvss": score, "ref": ref},
            }
        )
    return out
