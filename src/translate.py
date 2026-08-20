"""Dịch tiêu đề tin tiếng Anh sang tiếng Việt — API miễn phí, không cần key.

Ưu tiên Google Translate endpoint (chất lượng cao), dự phòng MyMemory.
Có cache (data/translations.json) để không dịch lặp lại.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import ssl
import urllib.parse
import urllib.request

import certifi

log = logging.getLogger("translate")

UA = "Mozilla/5.0 (compatible; CyberNewsBot/1.0)"
_SSL = ssl.create_default_context(cafile=certifi.where())


def _get(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=_SSL) as r:
        return r.read().decode("utf-8", errors="replace")


def _google(text: str) -> str:
    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl=en&tl=vi&dt=t&q={urllib.parse.quote(text)}"
    )
    data = json.loads(_get(url))
    return "".join(seg[0] for seg in data[0] if seg and seg[0]).strip()


def _mymemory(text: str) -> str:
    url = (
        "https://api.mymemory.translated.net/get"
        f"?q={urllib.parse.quote(text)}&langpair=en|vi"
    )
    data = json.loads(_get(url))
    return data.get("responseData", {}).get("translatedText", "").strip()


def translate_text(text: str) -> str:
    """Dịch en -> vi. Trả về "" nếu thất bại (gọi bên ngoài giữ nguyên bản gốc)."""
    for fn in (_google, _mymemory):
        try:
            t = fn(text)
            if t:
                return t
        except Exception as e:  # noqa: BLE001
            log.warning("Dịch qua %s lỗi: %s", fn.__name__, e)
    return ""


class TranslationCache:
    """Cache bản dịch theo hash của văn bản gốc."""

    def __init__(self, path: str):
        self.path = path
        self.data: dict = self._load()

    def _load(self) -> dict:
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _key(text: str) -> str:
        return hashlib.sha1(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> str | None:
        return self.data.get(self._key(text))

    def put(self, text: str, vi: str) -> None:
        self.data[self._key(text)] = vi

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, self.path)
