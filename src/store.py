"""Lưu trữ lịch sử tin tức dạng JSON (được commit lên GitHub)."""
from __future__ import annotations

import json
import os

from .models import NewsItem


class Store:
    """Quản lý file data/items.json: chống trùng lặp + giữ lịch sử."""

    def __init__(self, path: str, max_items: int = 4000):
        self.path = path
        self.max_items = max_items
        self.items, self.seen = self._load()

    def _load(self) -> tuple[list, set]:
        if not os.path.exists(self.path):
            return [], set()
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            items = [NewsItem.from_dict(d) for d in data]
            return items, {it.key for it in items}
        except Exception:
            # File hỏng thì bắt đầu lại sạch
            return [], set()

    def add_new(self, candidates: list[NewsItem]) -> list[NewsItem]:
        """Trả về các tin MỚI (chưa từng thấy) và lưu vào lịch sử."""
        fresh = []
        for it in candidates:
            if not it.title or not it.link:
                continue
            if it.key in self.seen:
                continue
            self.seen.add(it.key)
            fresh.append(it)
        if fresh:
            self.items = fresh + self.items
            self.items = self.items[: self.max_items]
            self._save()
        return fresh

    def save(self) -> None:
        """Lưu lại trạng thái hiện tại (dùng sau khi cập nhật title_vi...)."""
        self._save()

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(
                [it.to_dict() for it in self.items],
                f, ensure_ascii=False, indent=1,
            )
        os.replace(tmp, self.path)
