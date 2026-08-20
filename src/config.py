"""Cấu hình nguồn tin và danh mục cho Cyber News Bot."""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Danh mục: key -> (nhãn tiếng Việt, emoji, thứ tự hiển thị)
# ---------------------------------------------------------------------------
CATEGORIES = {
    "kev":        ("Đang bị khai thác (CISA KEV)", "⚠️", 0),
    "cve":        ("Lỗ hổng mới (CVE)", "🔴", 1),
    "vietnamese": ("Tin tiếng Việt", "🇻🇳", 2),
    "breach":     ("Lộ lọt dữ liệu / Ransomware", "🕳️", 3),
    "ai":         ("AI Security", "🤖", 4),
    "cloud":      ("Cloud Security", "☁️", 5),
    "general":    ("Tin tức khác", "📰", 6),
}

CATEGORY_ORDER = [k for k, _ in sorted(CATEGORIES.items(), key=lambda kv: kv[1][2])]

# ---------------------------------------------------------------------------
# Nguồn tin. Mỗi nguồn:
#   type       : "rss" (RSS/Atom) | "kev" (CISA KEV JSON) | "nvd" (NVD API v2)
#   categories : danh mục mặc định gán cho mọi tin của nguồn
#   lang       : "en" | "vi"
# ---------------------------------------------------------------------------
SOURCES = [
    # --- Lỗ hổng / CVE ------------------------------------------------------
    {
        "name": "NVD",
        "type": "nvd",
        "lang": "en",
        "categories": ["cve"],
        "url": "https://services.nvd.nist.gov/rest/json/cves/2.0",
    },
    {
        "name": "CISA KEV",
        "type": "kev",
        "lang": "en",
        "categories": ["kev"],
        "urls": [
            "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
            "https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities.json",
            "https://raw.githubusercontent.com/cisagov/kev-data/main/known_exploited_vulnerabilities.json",
        ],
    },

    # --- Tin tức bảo mật tổng hợp ------------------------------------------
    {
        "name": "The Hacker News",
        "type": "rss",
        "lang": "en",
        "categories": [],
        "url": "https://feeds.feedburner.com/TheHackersNews",
    },
    {
        "name": "SecurityWeek",
        "type": "rss",
        "lang": "en",
        "categories": [],
        "url": "https://www.securityweek.com/feed/",
    },
    {
        "name": "Krebs on Security",
        "type": "rss",
        "lang": "en",
        "categories": [],
        "url": "https://krebsonsecurity.com/feed/",
    },
    {
        "name": "The Record",
        "type": "rss",
        "lang": "en",
        "categories": [],
        "url": "https://therecord.media/feed",
    },
    {
        "name": "DarkReading",
        "type": "rss",
        "lang": "en",
        "categories": [],
        "url": "https://www.darkreading.com/rss.xml",
    },
    {
        "name": "Unit 42",
        "type": "rss",
        "lang": "en",
        "categories": [],
        "url": "https://unit42.paloaltonetworks.com/feed/",
    },
    {
        "name": "Google Security Blog",
        "type": "rss",
        "lang": "en",
        "categories": [],
        "url": "https://security.googleblog.com/feeds/posts/default",
    },
    {
        "name": "Talos Blog",
        "type": "rss",
        "lang": "en",
        "categories": [],
        "url": "https://blog.talosintelligence.com/rss/",
    },
    {
        "name": "Schneier on Security",
        "type": "rss",
        "lang": "en",
        "categories": [],
        "url": "https://www.schneier.com/feed/atom/",
    },

    # --- Lộ lọt dữ liệu / Ransomware ---------------------------------------
    {
        "name": "DataBreaches.net",
        "type": "rss",
        "lang": "en",
        "categories": ["breach"],
        "url": "https://www.databreaches.net/feed/",
    },

    # --- AI Security ---------------------------------------------------------
    {
        "name": "OpenAI News",
        "type": "rss",
        "lang": "en",
        "categories": [],
        "url": "https://openai.com/news/rss.xml",
    },

    # --- Cloud Security ------------------------------------------------------
    {
        "name": "AWS Security Blog",
        "type": "rss",
        "lang": "en",
        "categories": ["cloud"],
        "url": "https://aws.amazon.com/blogs/security/feed/",
    },
    {
        "name": "Cloudflare Blog",
        "type": "rss",
        "lang": "en",
        "categories": ["cloud"],
        "url": "https://blog.cloudflare.com/rss/",
    },
    {
        "name": "Cloud Security Alliance",
        "type": "rss",
        "lang": "en",
        "categories": ["cloud"],
        "url": "https://cloudsecurityalliance.org/blog/feed",
    },

    # --- Nguồn tiếng Việt ----------------------------------------------------
    # security_only=True: chỉ giữ tin liên quan bảo mật/an ninh mạng (lọc từ
    # khóa tiếng Việt), vì feed công nghệ VN lẫn nhiều tin không phải ATTT.
    {
        "name": "VnExpress Số hóa",
        "type": "rss",
        "lang": "vi",
        "categories": ["vietnamese"],
        "security_only": True,
        "url": "https://vnexpress.net/rss/so-hoa.rss",
    },
    {
        "name": "Znews Công nghệ",
        "type": "rss",
        "lang": "vi",
        "categories": ["vietnamese"],
        "security_only": True,
        "url": "https://znews.vn/rss/cong-nghe.rss",
    },
    {
        "name": "GenK",
        "type": "rss",
        "lang": "vi",
        "categories": ["vietnamese"],
        "security_only": True,
        "url": "https://genk.vn/rss/home.rss",
    },
    {
        "name": "Dân Trí Sức mạnh số",
        "type": "rss",
        "lang": "vi",
        "categories": ["vietnamese"],
        "security_only": True,
        "url": "https://dantri.com.vn/rss/suc-manh-so.rss",
    },
    {
        "name": "VTC News Công nghệ",
        "type": "rss",
        "lang": "vi",
        "categories": ["vietnamese"],
        "security_only": True,
        "url": "https://vtcnews.vn/rss/cong-nghe.rss",
    },
    {
        "name": "VietnamNet Công nghệ",
        "type": "rss",
        "lang": "vi",
        "categories": ["vietnamese"],
        "security_only": True,
        "url": "https://vietnamnet.vn/cong-nghe.rss",
    },
    {
        "name": "Thanh Niên Công nghệ",
        "type": "rss",
        "lang": "vi",
        "categories": ["vietnamese"],
        "security_only": True,
        "url": "https://thanhnien.vn/rss/cong-nghe.rss",
    },
    {
        "name": "Báo Tin tức (TTXVN) KH-CN",
        "type": "rss",
        "lang": "vi",
        "categories": ["vietnamese"],
        "security_only": True,
        "url": "https://baotintuc.vn/khoa-hoc-cong-nghe.rss",
    },
    {
        "name": "Tuổi Trẻ Công nghệ",
        "type": "rss",
        "lang": "vi",
        "categories": ["vietnamese"],
        "security_only": True,
        "url": "https://tuoitre.vn/rss/cong-nghe.rss",
    },
    {
        "name": "VietnamPlus Kinh tế số",
        "type": "rss",
        "lang": "vi",
        "categories": ["vietnamese"],
        "security_only": True,
        "url": "https://www.vietnamplus.vn/rss/kinh-te-so.rss",
    },
]
