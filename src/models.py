"""Mô hình dữ liệu cho một tin tức."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


@dataclass
class NewsItem:
    """Một tin tức / lỗ hổng thu thập được."""

    source: str          # tên nguồn, ví dụ "NVD", "BleepingComputer"
    title: str
    link: str
    published: str       # ISO 8601
    summary: str = ""
    categories: list = field(default_factory=list)   # ví dụ ["cve"], ["ai", "cloud"]
    lang: str = "en"     # "en" | "vi"
    extra: dict = field(default_factory=dict)        # CVSS, KEV details...
    title_vi: str = ""   # tiêu đề đã dịch sang tiếng Việt (nếu có)

    @property
    def key(self) -> str:
        """Khóa định danh duy nhất để chống trùng lặp."""
        raw = f"{self.source}|{self.link}".strip()
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        d = asdict(self)
        d["key"] = self.key
        return d

    @staticmethod
    def from_dict(d: dict) -> "NewsItem":
        return NewsItem(
            source=d.get("source", ""),
            title=d.get("title", ""),
            link=d.get("link", ""),
            published=d.get("published", ""),
            summary=d.get("summary", ""),
            categories=list(d.get("categories", [])),
            lang=d.get("lang", "en"),
            extra=d.get("extra", {}),
            title_vi=d.get("title_vi", ""),
        )

    @property
    def date(self) -> str:
        """Ngày (YYYY-MM-DD) theo UTC để nhóm trên trang web."""
        try:
            return (
                datetime.fromisoformat(self.published)
                .astimezone(timezone.utc)
                .strftime("%Y-%m-%d")
            )
        except Exception:
            return "1970-01-01"
