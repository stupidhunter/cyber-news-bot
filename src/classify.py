"""Phân loại tin tức theo từ khóa: breach / ai / cloud / general."""
from __future__ import annotations

# Thứ tự ưu tiên hiển thị (mỗi tin chỉ nằm ở 1 danh mục "tốt nhất")
PRIORITY = ["kev", "cve", "vietnamese", "breach", "ai", "cloud", "general"]

KEYWORDS = {
    "breach": [
        "data breach", "data leak", "leaked", "exposed data", "stolen data",
        "credentials", "ransomware", "lockbit", "clop", "hacked", "breach",
        "leak", "stolen", "cyberattack", "cyber attack", "intrusion",
        "compromised", "exfiltration",
        # Tiếng Việt
        "lộ lọt", "rò rỉ", "đánh cắp", "tấn công mạng", "mã độc", "lừa đảo",
        "tống tiền", "tin tặc", "vi phạm dữ liệu", "chiếm đoạt",
    ],
    "ai": [
        "artificial intelligence", "machine learning", "llm", "prompt injection",
        "chatgpt", "gpt-", "openai", "anthropic", "claude", "gemini",
        "deepfake", "ai-powered", "ai security", "model poisoning", "jailbreak",
        " ai ", "ai model", "agentic",
        # Tiếng Việt
        "trí tuệ nhân tạo", "ai tạo sinh", "deepfake",
    ],
    "cloud": [
        "aws", "azure", "gcp", "google cloud", "kubernetes", "k8s", "docker",
        "container", "serverless", "s3 bucket", "terraform", "okta",
        "snowflake", "entra", "cloud security", "cloudflare", "misconfigured",
        # Tiếng Việt
        "điện toán đám mây",
    ],
}


def classify(text: str, base_cats: list[str]) -> list[str]:
    """Gán danh mục cho một tin: danh mục mặc định của nguồn + từ khóa."""
    cats = set(base_cats)
    low = text.lower()
    for cat, words in KEYWORDS.items():
        if any(w in low for w in words):
            cats.add(cat)
    if not cats:
        cats.add("general")
    return sorted(c for c in cats if c != "general") or ["general"]


def best_category(cats: list[str]) -> str:
    """Chọn 1 danh mục hiển thị ưu tiên nhất."""
    s = set(cats)
    for c in PRIORITY:
        if c in s:
            return c
    return "general"
