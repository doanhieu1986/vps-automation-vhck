# Quy Trình Xử Lý VPS Automation VHCK v8

## 📋 Tổng Quan

Hệ thống tự động 100% - không cần can thiệp thủ công trong quy trình chính.

**Tần suất:** Hàng ngày (có thể setup lặp lại 2 lần/ngày tại 12h00 và 17h00)

---

## 🔄 Luồng Chi Tiết

### **Bước 1: Trigger Workflow**

Workflow được trigger bởi:
- 🔘 Manual trigger từ n8n UI
- 📅 Schedule (cron job - cấu hình trong n8n)
- 🔗 Webhook (có thể setup từ bên ngoài)

```
┌─────────────────┐
│ Manual Trigger  │
│   (n8n UI)      │
└────────┬────────┘
         │
         ▼
    [START WORKFLOW]
```

---

### **Bước 2: Fetch VSD Data**

**Node:** `Fetch VSD (Tin Tuc)` → runs `/scripts/fetch_vsd.py`

**Quy trình scraping:**

```python
1. Kết nối VSD (https://www.vsd.vn/vi/tin-thi-truong-co-so)
   └─ Lấy VPToken từ meta tag

2. Fetch danh sách tin tức (phân trang nếu cần)
   └─ Lọc theo KEEP_DAYS (mặc định = 7 ngày)
   
3. Cho mỗi tin tức:
   └─ Extract mã chứng khoán
   └─ Mở link & scrape chi tiết:
      • Tên tổ chức đăng ký
      • Tên chứng khoán
      • Mã ISIN
      • Loại chứng khoán
      • Nơi giao dịch
      • Các quyền (cổ tức, mua, hoán đổi, etc.)
      • Mục đích & lý do đăng ký
      • Thời gian & địa điểm thực hiện
      
4. Merge dữ liệu mới với cũ:
   └─ Giữ lại records cũ (status unchanged)
   └─ Thêm records mới (status='pending')
   
5. Export JSON → `/data/vsd_records.json`

6. Export Excel → `/data/vsd_records.xlsx`
   └─ Cấu trúc giống JSON
   └─ Định dạng đẹp, dễ xem

7. Return JSON result
   └─ Status: success/error
   └─ Message: log & stats
   └─ excel_info: file path & record count
   └─ json_info: file path & record count
```

**Input:** Không có (fetch tất cả từ VSD)

**Output:**
```json
{
  "status": "success",
  "date": "2026-04-21",
  "records": [...],
  "excel_info": {
    "status": "success",
    "file": "/app/vps-automation-vhck/data/vsd_records.xlsx",
    "records_count": 330,
    "message": "Created with 330 records"
  },
  "json_info": {
    "status": "success",
    "file": "/app/vps-automation-vhck/data/vsd_records.json",
    "records_count": 330,
    "message": "Created with 330 records"
  }
}
```

---

### **Bước 3: Verify Excel File**

**Node:** `Verify Excel File`

**Quy trình:**
```
Input: JSON result từ Fetch VSD
  │
  ├─ Check: status === 'success'? 
  │   └─ NO → Return error
  │
  ├─ Check: excel_info exists?
  │   └─ NO → Return error
  │
  ├─ Check: file exists?
  │   └─ NO → Return error
  │
  └─ Check: file readable?
      └─ NO → Return error
      └─ YES → Continue
      
Output: File metadata
```

**Output:**
```json
{
  "status": "success",
  "file": "/app/vps-automation-vhck/data/vsd_records.json",
  "records_count": 330,
  "timestamp": "2026-04-21T10:30:00Z"
}
```

---

### **Bước 4: Embed JSON into HTML**

**Node:** `Embed JSON into HTML`

**Quy trình:**
```
Input: File metadata từ Verify
  │
  ├─ Read JSON: /data/vsd_records.json
  │
  ├─ Read HTML: /web/vps_automation_vhck.html
  │
  ├─ Remove old embedded data
  │   └─ Regex: <script>...window.EMBEDDED_DATA...</script>
  │
  ├─ Append new embedded data:
  │   └─ <script>window.EMBEDDED_DATA = {...};</script>
  │
  ├─ Write updated HTML → /web/vps_automation_vhck.html
  │
  └─ Output: Embedded successfully
```

**Output:**
```json
{
  "status": "success",
  "message": "Embedded 330 records into HTML",
  "records_embedded": 330,
  "html_size": 1400000,
  "timestamp": "2026-04-21T10:30:30Z"
}
```

---

### **Bước 5: Commit to GitHub**

**Node:** `Commit to GitHub` 

**Quy trình:**
```
Input: Embedded HTML metadata
  │
  ├─ Load GitHub token: .github-token.json
  │   └─ token, owner, repo
  │
  ├─ Commit 1: JSON file
  │   ├─ Read: /data/vsd_records.json
  │   ├─ Base64 encode
  │   └─ GitHub API PUT /repos/{owner}/{repo}/contents/data/vsd_records.json
  │       └─ Message: "ci: update VSD data (330 records)"
  │
  ├─ Commit 2: HTML file  
  │   ├─ Read: /web/vps_automation_vhck.html
  │   ├─ Base64 encode
  │   └─ GitHub API PUT /repos/{owner}/{repo}/contents/web/vps_automation_vhck.html
  │       └─ Message: "ci: update HTML with embedded data (330 records)"
  │
  └─ Return: Commit result
```

**Output:**
```json
{
  "status": "success",
  "message": "Committed 330 records to GitHub",
  "github_url": "https://github.com/doanhieu1986/vps-automation-vhck",
  "records_committed": 330,
  "timestamp": "2026-04-21T10:31:00Z"
}
```

---

### **Bước 6: Push to GitHub Pages**

**Node:** `Push to GitHub`

**Quy trình:**
```
Input: Commit result
  │
  ├─ Copy HTML → /docs/index.html
  │   └─ GitHub Pages serves from /docs folder
  │
  └─ GitHub auto-deploys to GitHub Pages:
     └─ https://doanhieu1986.github.io/vps-automation-vhck/
```

**Output:**
```json
{
  "status": "success",
  "message": "Workflow completed! Data committed to GitHub",
  "github_url": "https://github.com/doanhieu1986/vps-automation-vhck",
  "pages_url": "https://doanhieu1986.github.io/vps-automation-vhck/",
  "records_committed": 330,
  "timestamp": "2026-04-21T10:31:30Z"
}
```

---

### **Bước 7: Dashboard Interactive (Web UI)**

**Tài liệu:** `DASHBOARD_UI.md` (chi tiết đầy đủ)

**Dashboard tính năng:**

1. **Hiển Thị Dữ Liệu**
   - Bảng 6 cột: Mã CK | Tên Chứng Khoán | Tổ Chức Đăng Ký | Nơi Giao Dịch | Loại CK | Trạng Thái
   - Thống kê: Tổng bản ghi | Đã xác nhận | Từ chối | Chờ xử lý
   - Auto-update khi workflow chạy

2. **Tìm Kiếm & Lọc**
   - Tìm kiếm theo mã CK, tên chứng khoán, tổ chức (real-time)
   - Lọc theo khoảng thời gian (từ ngày - đến ngày)
   - Lọc theo trạng thái (pending/confirmed/rejected)
   - Kết hợp 3 bộ lọc (search + date + status)

3. **Chi Tiết Modal** (Click vào dòng để xem)
   - **Kích thước**: 1400px × 85vh (lớn, căn giữa)
   - **Bố cục 2 cột**:
     - **Cột trái**: Thông tin chi tiết (basic info + implementation + rights + source)
     - **Cột phải**: Nội dung tin tức gốc (để so sánh)
   - **Dark overlay**: 80% opacity để tập trung vào modal
   - **3 nút**: Xác Nhận | Từ Chối | Đóng

4. **Giao Diện Features**
   - Responsive design (desktop, tablet, mobile)
   - Dark theme (slate colors)
   - Smooth animations (fade, slide)
   - Professional styling

**Truy cập:**
- Local: `file:///path/to/index.html`
- GitHub Pages: `https://doanhieu1986.github.io/vps-automation-vhck/`

---

## 📊 Data Flow Diagram

```
                    ┌─────────────────────┐
                    │  n8n Workflow v8    │
                    │  Manual/Schedule    │
                    └──────────┬──────────┘
                               │
                ┌──────────────▼──────────────┐
                │ 1. Fetch VSD (Python)       │
                │    fetch_vsd.py KEEP_DAYS=7│
                │    Output: JSON + Excel     │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │ 2. Verify Excel            │
                │    Check files exist       │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │ 3. Embed JSON→HTML          │
                │    Merge data into page     │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │ 4. Commit to GitHub         │
                │    Push JSON + HTML         │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │ 5. Deploy to GitHub Pages   │
                │    Auto-published           │
                └──────────────┬──────────────┘
                               │
                    ┌──────────▼─────────┐
                    │  🌐 Live Dashboard  │
                    │ https://doanhieu... │
                    └────────────────────┘
```

---

## 💾 Output Files

| File | Purpose | Auto-generated | Format |
|------|---------|---|---|
| `/data/vsd_records.json` | Main data store | ✅ Yes | JSON |
| `/data/vsd_records.xlsx` | Excel export | ✅ Yes | Excel |
| `/web/vps_automation_vhck.html` | Source HTML | ✅ Updated | HTML |
| `/docs/index.html` | GitHub Pages | ✅ Synced | HTML |
| `/index.html` | Backup copy | ✅ Synced | HTML |

---

## 🔍 Data Processing

### Field Extraction Logic
Từ text content của VSD news, extract:

```
"Tên tổ chức đăng ký:" → tên_tổ_chức_đăng_ký
"Tên chứng khoán:" → tên_chứng_khoán
"Mã chứng khoán:" → code (mã CK)
"Mã ISIN:" → mã_isin
"Nơi giao dịch:" → nơi_giao_dịch
"Loại chứng khoán:" → loại_chứng_khoán
"Ngày đăng ký:" → ngày_đăng_ký_cuối
"Lý do/Mục đích:" → lý_do_mục_đích
"Tỷ lệ thực hiện:" → tỷ_lệ_thực_hiện
"Thời gian thực hiện:" → thời_gian_thực_hiện
"Địa điểm thực hiện:" → địa_điểm_thực_hiện
...
```

### Status Management

```
                   ┌─────────────┐
                   │   pending   │  🟠 Chờ xử lý
                   │ (dữ liệu    │
                   │  mới)       │
                   └──────┬──────┘
                          │
                ┌─────────▼─────────┐
                │  VHCK Review UI   │
                │  (Dashboard)      │
                └────┬──────┬───────┘
                     │      │
         ┌───────────┘      └──────────┐
         │                             │
    ┌────▼──────┐           ┌─────────▼──┐
    │ confirmed │ 🟢        │  rejected  │ 🔴
    │ (xác nhận)│           │  (từ chối) │
    └───────────┘           └────────────┘
```

---

## ⚠️ Error Handling

Nếu bất kỳ bước nào fail:
- n8n dừng workflow
- Log error message
- Có thể setup error handling workflow (tùy chọn)
- Data không được push lên GitHub

---

## 📈 Monitoring

### Check Execution
```bash
# Via n8n UI
http://localhost:5678/workflow/execution-history

# Via logs
tail -f /path/to/n8n/logs
```

### Success Indicator
- ✅ Workflow Complete node được hit
- ✅ Commit message trên GitHub
- ✅ Data hiển thị trên GitHub Pages

---

## 🔧 Configuration

### Adjust Data Collection Period
```python
# File: /scripts/fetch_vsd.py (line 34)
KEEP_DAYS = 7  # Change this value

# Examples:
KEEP_DAYS = 1   # Only today
KEEP_DAYS = 7   # Last 7 days (default)
KEEP_DAYS = 30  # Last 30 days
```

### Schedule Execution
n8n UI → Workflow Settings → Triggers → Add Schedule
```
Time: 12:00 & 17:00 (2x per day)
Days: Every day (Mon-Sun)
```

---

## 📚 Related Files

- **README.md** - System overview
- **DASHBOARD_UI.md** - 🆕 Web UI dashboard & interactive features (v8.1)
- **FETCH_VSD_LOGIC.md** - Scraping details
- **COLUMN_DETERMINATION_LOGIC.md** - Field extraction
- **DEPLOYMENT_GUIDE.md** - Deploy instructions
- **output_requirement.md** - Output specifications

---

**Last Updated:** 2026-04-23  
**Version:** v8.1 - Dashboard Interactive  
**Status:** ✅ Production Ready
