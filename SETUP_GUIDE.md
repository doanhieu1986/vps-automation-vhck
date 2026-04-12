# 🚀 VPS Automation VHCK - Setup & Usage Guide

## 📋 Overview

Hệ thống tự động hóa thu thập thông tin quyền chứng khoán từ các sàn giao dịch Việt Nam (VSD, HNX, HOSE).

**Các thành phần:**
1. ✅ **Python Scripts** - Crawl dữ liệu từ VSD, HNX, HOSE
2. ✅ **N8n Workflow** - Tự động hóa quy trình
3. ✅ **Flask Server** - Lưu trữ kết quả
4. ✅ **Web Interface** - Review và xác nhận

---

## 🔧 Cài Đặt & Khởi Động

### Bước 1: Cài Đặt Dependencies

```bash
cd /Users/hieudt/vps-automation-vhck/scripts
pip install -r requirements.txt
```

**Packages cần:**
- `requests` - HTTP requests
- `beautifulsoup4` - Web scraping

### Bước 2: Start Flask Server

Mở terminal và chạy:

```bash
python3 /Users/hieudt/vps-automation-vhck/save_result.py
```

Server sẽ chạy tại: **http://localhost:3000**

```
🚀 Starting VPS Automation Helper Server...
📍 Server running at: http://localhost:3000
💾 Result file location: /Users/hieudt/vps-automation-vhck/result.md
```

⚠️ **Giữ terminal này mở** trong suốt quá trình sử dụng

### Bước 3: Chọn & Chạy N8n Workflow

**Các phiên bản có sẵn:**

| Workflow | ID | Mô Tả |
|----------|----|----|
| v1 (cũ) | `2B7pEkca1A9eh13p` | ❌ Có lỗi file system - XÓA |
| v2 | `Hk89HwyZoWTrnpwg` | ✅ HTTP fetch cơ bản |
| **v3 (mới)** | `3tj17VPgJugvImnz` | ✅ **Python Scripts Integration (Recommended)** |

**Khuyến cáo:** Sử dụng **v3** vì nó gọi Python scripts để crawl dữ liệu thực

#### Chạy Workflow v3 (Recommended):

1. Vào N8n: http://localhost:5678
2. Tìm: `VPS Automation VHCK v3 - Python Scripts Integration`
3. Click **Activate** (nếu chưa)
4. Click **Execute Workflow** (▶️)

**Workflow sẽ:**
- ✓ Đọc 5 mã từ symbol.md
- ✓ Gọi Python scripts (fetch_all.py)
- ✓ Crawl từ VSD, HNX, HOSE
- ✓ Xử lý & cấu trúc dữ liệu
- ✓ Tạo markdown file
- ✓ Save vào result.md qua Flask API

---

## 📁 Cấu Trúc Thư Mục

```
vps-automation-vhck/
├── 📄 CLAUDE.md                      # Hướng dẫn dự án
├── 📄 workflow.md                    # Quy trình chi tiết
├── 📄 symbol.md                      # Danh sách mã cần xử lý
├── 📄 output_requirement.md          # Yêu cầu output
├── 📄 result.md                      # Kết quả (tự động generate)
├── 📄 SETUP_GUIDE.md                 # File này
│
├── 📂 scripts/
│   ├── fetch_all.py                 # Unified fetcher (tất cả 3 sources)
│   ├── fetch_vsd.py                 # Fetch từ VSD
│   ├── fetch_hnx.py                 # Fetch từ HNX
│   ├── fetch_hose.py                # Fetch từ HOSE
│   ├── requirements.txt              # Python dependencies
│   └── README.md                     # Scripts documentation
│
├── 📂 n8n/
│   ├── vps_automation_vhck.json     # v1 (xóa sau)
│   ├── vps_automation_vhck_v2.json  # v2 (HTTP fetch)
│   └── vps_automation_vhck_v3.json  # v3 (Python Scripts) ⭐
│
├── 📂 web/
│   └── vps_automation_vhck.html     # Web interface
│
└── 📄 save_result.py                # Flask helper server
```

---

## 🎯 Workflow Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      N8N WORKFLOW V3                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 1. Read Symbols (BVBS14199, HCMB18240, ...)               │
│    ↓                                                         │
│ 2. Parse Symbols → [array of symbols]                      │
│    ↓                                                         │
│ 3. Run Python Script: fetch_all.py                         │
│    ├─ fetch_vsd.py BVBS14199                               │
│    ├─ fetch_hnx.py BVBS14199                               │
│    └─ fetch_hose.py BVBS14199                              │
│    ↓                                                         │
│ 4. Parse Script Output (JSON)                              │
│    ↓                                                         │
│ 5. Process Records                                          │
│    ↓                                                         │
│ 6. Generate Markdown                                        │
│    ↓                                                         │
│ 7. Save to Flask API (http://localhost:3000)              │
│    └─ Updates: /Users/hieudt/vps-automation-vhck/result.md │
│    ↓                                                         │
│ 8. ✅ Completion                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌐 Web Interface Usage

### Mở Web Interface:

```bash
# Option 1: Trực tiếp (File URL)
file:///Users/hieudt/vps-automation-vhck/web/vps_automation_vhck.html

# Option 2: Với HTTP server
python3 -m http.server 8000 --directory /Users/hieudt/vps-automation-vhck/web
# Rồi mở: http://localhost:8000/vps_automation_vhck.html
```

### Features:

| Feature | Mô Tả |
|---------|--------|
| 📊 **Dashboard** | Hiển thị tổng số bản ghi, trạng thái |
| 🔍 **Search** | Tìm kiếm theo mã hoặc tên |
| 🏷️ **Filter** | Lọc theo trạng thái (pending/confirmed/rejected) |
| ✓ **Confirm** | Xác nhận thông tin chính xác |
| ✗ **Reject** | Từ chối thông tin sai |
| ✎ **Edit** | Sửa thông tin chi tiết |
| 🔗 **Links** | Links đến VSD, HNX, HOSE |
| 💾 **LocalStorage** | Tự động lưu trong browser |

---

## 📊 Python Scripts Details

### fetch_all.py (Recommended)

Unified script gọi tất cả 3 fetchers:

```bash
python3 fetch_all.py BVBS14199 HCMB18240 TD1429094
```

**Output JSON:**
```json
{
  "status": "success",
  "timestamp": "2026-04-12T17:30:00",
  "total_symbols": 3,
  "records": [
    {
      "symbol": "BVBS14199",
      "sources": {
        "vsd": { "status": "success", "data": [...] },
        "hnx": { "status": "error", "data": [] },
        "hose": { "status": "success", "data": [...] }
      },
      "collection_status": {
        "total_sources": 3,
        "successful_sources": 2,
        "overall": "success"
      }
    }
  ]
}
```

### Individual Scripts:

```bash
# VSD
python3 fetch_vsd.py BVBS14199

# HNX
python3 fetch_hnx.py HCMB18240

# HOSE
python3 fetch_hose.py TD1429094
```

---

## 🔄 Workflow Usage Examples

### Example 1: Run Once & Review

```
1. $ python3 save_result.py          (Terminal 1)
2. N8n: Execute Workflow v3           (Browser)
3. Open Web Interface                 (Browser)
4. Review & Click ✓ Confirm           (Browser)
```

### Example 2: Multiple Executions

```
# Run multiple times to collect more data
1. Execute Workflow v3  (1st run)  → result.md
2. Edit & Confirm data  (Web UI)
3. Execute Workflow v3  (2nd run)  → Append to result.md
4. Continue...
```

---

## 🔧 Troubleshooting

| Issue | Giải Pháp |
|-------|---------|
| Flask server: Port 5000 in use | Dùng port 3000 thay vì (đã config) |
| Python scripts timeout | Tăng timeout trong script (default 10s) |
| HNX fetch failed | HNX có thể block requests - normal |
| Web interface không load | Mở file:// URL hoặc dùng HTTP server |
| N8n workflow error | Check Python scripts có chạy được không |

---

## 📝 Data Format

### Symbol Input (symbol.md):
```
BVBS14199
HCMB18240
TD1429094
HCMB14181
HCMB15313
```

### Result Output (result.md):
```markdown
# Kết Quả Thu Thập Thông Tin Quyền Chứng Khoán

## 1. BVBS14199

| Thông Tin | Chi Tiết |
|-----------|----------|
| Mã chứng khoán | BVBS14199 |
| ... | ... |

### Quyền
- **Quyền nhận lãi:** ...
- ...

**Trạng thái:** pending
**Dữ liệu thu thập:** [JSON from scripts]
```

---

## 🚀 Tối Ưu Hóa

### Performance:
- Scripts có rate limiting 1s/request
- Timeout: 10 giây per request
- BeautifulSoup cho parsing HTML

### Reliability:
- Error handling cho mỗi fetcher
- Fallback nếu một source fail
- LocalStorage backup trong web UI

### Scalability:
- Có thể xử lý hàng trăm mã
- Modular script design
- N8n workflow dễ extend

---

## 📞 Support

Các script files:
- `/Users/hieudt/vps-automation-vhck/scripts/` - Python crawlers
- `/Users/hieudt/vps-automation-vhck/save_result.py` - Flask server
- `/Users/hieudt/vps-automation-vhck/n8n/` - N8n workflows
- `/Users/hieudt/vps-automation-vhck/web/` - Web interface

---

## ✅ Checklist Để Sử Dụng

- [ ] Cài pip packages: `pip install -r scripts/requirements.txt`
- [ ] Start Flask server: `python3 save_result.py`
- [ ] Vào N8n dashboard
- [ ] Activate Workflow v3: `3tj17VPgJugvImnz`
- [ ] Execute Workflow
- [ ] Open Web Interface: `vps_automation_vhck.html`
- [ ] Review & Confirm data

---

**Created:** 2026-04-12
**Last Updated:** 2026-04-12
