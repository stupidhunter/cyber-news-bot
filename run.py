#!/usr/bin/env python3
"""Chạy bot từ thư mục gốc repo:

    python run.py                # chạy đầy đủ (thu thập + gửi Telegram + trang web)
    python run.py --dry-run      # chỉ in digest, không gửi
    python run.py --test-telegram
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.collect import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
