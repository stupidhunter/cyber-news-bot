# 🛡️ Cyber News Bot

Hệ thống **thu thập tin tức an ninh mạng tự động** — chạy 100% trên các nền tảng **miễn phí**:

- 🐙 **GitHub** (repo + GitHub Actions + GitHub Pages) — không tốn phí
- ✈️ **Telegram** — gửi điểm tin ngắn gọn
- 📡 Nguồn tin: RSS/API công khai, không cần API key

Mỗi **4 giờ**, bot tự động:
1. Thu thập tin từ 20+ nguồn (NVD, CISA KEV, The Hacker News, SecurityWeek, Krebs, DarkReading, AWS/Cloudflare/CSA cloud, OpenAI, VnExpress, Znews, GenK, Dân Trí, VTC, VietnamNet, Thanh Niên...)
2. Chống trùng lặp, phân loại theo chủ đề
3. Gửi **điểm tin ngắn gọn** vào Telegram của bạn
4. Cập nhật **trang web lịch sử** (GitHub Pages) kèm ô tìm kiếm

---

## ✨ Tính năng

| Tính năng | Mô tả |
|---|---|
| 🔴 **Lỗ hổng mới (CVE)** | CVE mới công bố từ NVD, kèm điểm CVSS |
| ⚠️ **Đang bị khai thác** | Cảnh báo RIÊNG khi CISA KEV thêm lỗ hổng mới đang bị khai thác ngoài thực tế |
| 🕳️ **Lộ lọt dữ liệu / Ransomware** | Tin về breach, ransomware từ DataBreaches.net + lọc từ khóa |
| 🤖 **AI Security** | Tin về bảo mật AI: prompt injection, LLM, deepfake... |
| ☁️ **Cloud Security** | AWS, Azure, GCP, Kubernetes, Docker... |
| 🇻🇳 **Tin tiếng Việt** | VnExpress, Znews, GenK, Dân Trí, VTC, VietnamNet, Thanh Niên, TTXVN, Tuổi Trẻ, VietnamPlus — **chỉ giữ tin liên quan bảo mật** (tự động bỏ tin công nghệ thông thường) |
| 🌐 **Dịch tự động EN→VI** | Tiêu đề tin tiếng Anh được dịch sang tiếng Việt (Google Translate miễn phí, có cache `data/translations.json`, mỗi kỳ dịch tối đa 40 tin — tin mới nhất trước) |
| 📄 **Trang web lịch sử** | GitHub Pages hiển thị 400 tin gần nhất, có ô tìm kiếm |
| 🧹 **Chống trùng lặp** | Cùng 1 tin không bao giờ gửi lại |
| 🔌 **Chạy tay được** | Chạy workflow thủ công bất cứ lúc nào từ tab Actions |

## 💰 Chi phí: 0 đồng

| Thành phần | Nền tảng | Phí |
|---|---|---|
| Mã nguồn + lịch sử tin | GitHub repo | Miễn phí |
| Chạy định kỳ (cron 4h) | GitHub Actions | Miễn phí (≈ 45 phút chạy/tháng, hạn mức 2000 phút) |
| Trang web | GitHub Pages | Miễn phí |
| Nhận tin | Telegram Bot | Miễn phí |
| Dữ liệu tin tức | RSS/API công khai | Miễn phí, không cần key |

---

## 🗂️ Kiến trúc

```
GitHub Actions (cron mỗi 4h)
        │
        ▼
python run.py  ──┬── Đọc 20+ nguồn RSS/API (NVD, CISA KEV, THN, ...)
        │        ├── Lọc trùng lặp, phân loại chủ đề
        │        ├── Lưu lịch sử → data/items.json (commit lên repo)
        │        ├── Gửi Telegram: alert KEV + điểm tin (HTML, link tắt)
        │        └── Sinh trang web → docs/index.html
        │
        ▼
GitHub Pages (Settings → main → /docs)  +  Telegram chat của bạn
```

## 📂 Cấu trúc thư mục

```
cyber-news-bot/
├── run.py                        # điểm vào chính
├── requirements.txt              # feedparser, certifi
├── .github/workflows/collect.yml # cron 4h + tự commit
├── src/
│   ├── config.py                 # ⚙️ danh sách nguồn tin + danh mục
│   ├── classify.py               # từ khóa phân loại breach/AI/cloud
│   ├── fetchers.py               # đọc RSS/Atom/JSON (NVD API, CISA KEV)
│   ├── store.py                  # chống trùng lặp + lịch sử
│   ├── telegram.py               # dựng & gửi điểm tin
│   ├── sitegen.py                # sinh trang web tĩnh
│   └── collect.py                # logic chính
├── scripts/check_feeds.py        # kiểm tra nguồn còn sống không
├── data/items.json               # lịch sử tin (tự tạo khi chạy)
└── docs/index.html               # trang web (tự sinh khi chạy)
```

---

## 🚀 Triển khai (khoảng 10 phút)

### Bước 1 — Tạo repo và đẩy code lên GitHub

```bash
# Trên máy bạn
cd cyber-news-bot
git init
git add .
git commit -m "Cyber News Bot"
git branch -M main
git remote add origin https://github.com/<username>/cyber-news-bot.git
git push -u origin main
```

### Bước 2 — Tạo Telegram Bot (nếu chưa có)

1. Mở Telegram, tìm **@BotFather** → gõ `/newbot` → đặt tên → nhận **token** dạng `123456:ABC-DEF...`
2. Mở chat với bot vừa tạo, bấm **Start**, gửi 1 tin nhắn bất kỳ (ví dụ `hi`).
3. Lấy `chat_id`: chạy lệnh sau (thay TOKEN), tìm `"chat":{"id":...}`:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getUpdates"
   ```
   Chat cá nhân thường là số âm 10 chữ số. Nếu muốn gửi vào group: thêm bot vào group rồi làm lại bước trên.

### Bước 3 — Cấu hình secrets trên GitHub

Vào repo → **Settings → Secrets and variables → Actions**:

| Loại | Tên | Giá trị |
|---|---|---|
| Secret | `TELEGRAM_BOT_TOKEN` | Token lấy ở Bước 2 |
| Secret | `TELEGRAM_CHAT_ID` | Chat ID lấy ở Bước 2 |
| Variable | `SITE_URL` | `https://<username>.github.io/cyber-news-bot/` (để điểm tin có link vào trang web) |

### Bước 4 — Bật GitHub Pages

**Settings → Pages →** *Build and deployment* → *Source*: **Deploy from a branch** → Branch: `main` → thư mục: **`/docs`** → **Save**.

Sau ~1 phút, truy cập `https://<username>.github.io/cyber-news-bot/` để xem trang tin.

### Bước 5 — Chạy thử

**Actions** tab → chọn workflow **"Thu thập tin tức an ninh mạng"** → **Run workflow** → chờ ~1-2 phút.

Kiểm tra:
- ✅ Telegram nhận **alert KEV** (nếu có) + **điểm tin** (có link `Xem đầy đủ`)
- ✅ Trang web có dữ liệu mới

Từ đó, workflow tự chạy mỗi 4 giờ (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC).

---

## 🧪 Chạy thử trên máy local

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Chỉ thu thập + in điểm tin ra màn hình (không gửi Telegram)
.venv/bin/python run.py --dry-run

# Kiểm tra nguồn nào còn hoạt động
.venv/bin/python scripts/check_feeds.py

# Gửi tin nhắn test tới Telegram (cần env đã set)
TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... .venv/bin/python run.py --test-telegram
```

---

## ⚙️ Tùy chỉnh

### Đổi giờ chạy
Sửa dòng `cron` trong `.github/workflows/collect.yml` (tham khảo [crontab.guru](https://crontab.guru)) — ví dụ mỗi 6 giờ: `0 */6 * * *`.

### Thêm / bớt nguồn tin
Sửa danh sách `SOURCES` trong `src/config.py` — mỗi nguồn cần:
```python
{"name": "Tên", "type": "rss", "lang": "en", "categories": ["cve"], "url": "https://.../feed"}
```
- `type`: `rss` (RSS/Atom) | `kev` (CISA KEV JSON) | `nvd` (NVD API)
- `categories`: `cve`, `kev`, `breach`, `ai`, `cloud`, `vietnamese`
- `security_only: True` (chỉ nguồn tiếng Việt): chỉ giữ tin liên quan bảo mật — lọc bằng từ khóa tiếng Việt trong `src/classify.py` (tự bỏ dấu, so khớp nguyên từ)
- Sau khi thêm, chạy `scripts/check_feeds.py` để xác minh nguồn còn sống.

### Thêm từ khóa phân loại
Sửa `KEYWORDS` trong `src/classify.py` (Anh + Việt).

### Giới hạn số tin
- Mỗi danh mục tối đa 10 tin/tin nhắn (`MAX_PER_CAT` trong `src/telegram.py`)
- Lịch sử tối đa 4000 tin (`MAX_ITEMS`, có thể set qua env)

### Dịch tiêu đề sang tiếng Việt
- Mặc định **bật** (dịch tối đa 40 tin mỗi kỳ, tin mới nhất trước — dần dần backfill lịch sử gần nhất)
- Tắt bằng `--no-translate` hoặc env `TRANSLATE=0`
- Điều chỉnh: `TRANSLATE_MAX` (số tin mỗi kỳ), `TRANSLATE_DELAY` (giây giữa 2 lần gọi API, mặc định 0.25)
- Bản dịch được cache trong `data/translations.json` (commit lên repo nên không dịch lại lần sau)

---

## 🩺 Khắc phục sự cố

| Hiện tượng | Nguyên nhân & cách xử lý |
|---|---|
| Workflow chạy thủ công OK nhưng cron không chạy | GitHub **tạm dừng cron** nếu repo không có hoạt động nào trong **60 ngày**. Vào tab Actions → Run workflow 1 lần để kích hoạt lại. |
| Một vài nguồn báo `LỖI` trong log | Bình thường — nguồn đó chặn bot/đang lỗi; các nguồn khác vẫn chạy. Chạy `check_feeds.py` để rà. |
| Cron chạy trễ vài chục phút | GitHub Actions free tier có thể trễ giờ khi cao điểm — chấp nhận được. |
| Không nhận tin Telegram | Kiểm tra token/chat_id trong Secrets; thử `--test-telegram`; nhớ bấm **Start** bot trước. |
| Trang web 404 | Bật Pages đúng branch `main` + thư mục `/docs` (Bước 4), chờ 1-2 phút. |

---

## 📌 Lưu ý về giới hạn free

- **GitHub Actions**: 2000 phút/tháng (miễn phí) — hệ thống này chỉ dùng ~45 phút/tháng.
- **GitHub Pages**: 10 GB/tháng băng thông — quá đủ cho trang tin cá nhân.
- **NVD API**: giới hạn 5 request/30 giây nếu không có API key — hệ thống chỉ gọi 1 lần mỗi kỳ nên không ảnh hưởng.
- Nguồn chính phủ VN (VietnamCERT, AIS, Chống lừa đảo) **không có RSS công khai** nên chưa đưa vào; nếu cần, có thể thêm crawler HTML riêng.

---

*Dự án mã nguồn mở, dựa trên các nguồn dữ liệu công khai. Tin tức chỉ mang tính tham khảo — hãy kiểm tra nguồn gốc trước khi hành động.*
