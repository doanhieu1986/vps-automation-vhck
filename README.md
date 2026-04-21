# VPS Automation VHCK v8 - Hệ Thống Tự Động Cập Nhật Thông Tin Quyền Chứng Khoán

## 📋 Tổng Quan

**VPS Automation VHCK v8** là hệ thống tự động hoàn toàn dùng để:
- 🔄 Thu thập thông tin quyền chứng khoán từ VSD hàng ngày
- 📊 Lưu dữ liệu vào JSON và Excel
- 🌐 Hiển thị trên dashboard web với chức năng tìm kiếm, lọc
- 💾 Cập nhật tự động lên GitHub Pages
- ✅ Cho phép VHCK xác nhận trạng thái dữ liệu trên web UI

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────┐
│                    n8n Workflow (v8)                    │
│                  Manual Trigger / Webhook               │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │ 1. Fetch VSD (Python)│
        │  fetch_vsd.py       │
        │  - Scrape VSD news  │
        │  - Extract details  │
        │  - Generate JSON    │
        │  - Create Excel     │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ 2. Verify & Embed   │
        │  - Check files      │
        │  - Embed JSON→HTML  │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ 3. GitHub Commit    │
        │  - Push JSON        │
        │  - Push HTML        │
        └──────────┬──────────┘
                   │
                   ▼
        📁 GitHub Repository
        📊 GitHub Pages Deploy
        🌐 Live Dashboard
```

---

## 📂 Cấu Trúc Dự Án

```
vps-automation-vhck/
├── README.md                              # File này
├── CLAUDE.md                              # Project instructions
├── FETCH_VSD_LOGIC.md                     # Chi tiết logic scraping
├── COLUMN_DETERMINATION_LOGIC.md          # Logic xác định columns
├── DEPLOYMENT_GUIDE.md                    # Hướng dẫn deploy workflow
├── output_requirement.md                  # Yêu cầu output format
├── workflow.md                            # Mô tả quy trình luồng
│
├── scripts/
│   ├── fetch_vsd.py                       # ⭐ Script scraper chính
│   ├── requirements.txt                   # Python dependencies
│   └── deploy-v8.js                       # Deploy script cho v8
│
├── n8n/
│   └── VPS Automation VHCK v8 - Complete Flow.json  # ⭐ Active workflow
│
├── data/
│   ├── vsd_records.json                   # Output JSON (330+ records)
│   └── vsd_records.xlsx                   # Output Excel
│
├── web/
│   └── vps_automation_vhck.html            # Source HTML dashboard
│
└── docs/
    └── index.html                         # GitHub Pages (deployed)
```

---

## 🚀 Quy Trình Hoạt Động

### **Bước 1: Trigger Workflow**
```bash
# Manual trigger từ n8n UI
- Vào n8n Dashboard → Click "VPS Automation VHCK v8 - Complete Flow"
- Click "Execute Workflow" (hoặc setup schedule/webhook)
```

### **Bước 2: Fetch VSD Data** 
Script `fetch_vsd.py` thực hiện:
```python
KEEP_DAYS = 7  # Lấy dữ liệu 7 ngày gần nhất

1. Kết nối VSD (https://www.vsd.vn/vi/tin-thi-truong-co-so)
2. Extract danh sách tin tức & mã chứng khoán
3. Mở từng bài để lấy chi tiết quyền:
   - Tên tổ chức đăng ký
   - Tên chứng khoán
   - Mã ISIN
   - Nơi giao dịch
   - Loại chứng khoán
   - Các quyền (voting, dividend, etc.)
4. Xuất JSON → /data/vsd_records.json
5. Xuất Excel → /data/vsd_records.xlsx
```

**Kết quả:**
- JSON với mảng `records[]` chứa 330+ bản ghi
- Excel file với cấu trúc na ná
- Mỗi record có status: `'pending'` (chờ xử lý)

### **Bước 3: Verify Excel & Embed Data**
n8n kiểm tra:
- ✅ Excel file được tạo thành công
- ✅ JSON file hợp lệ
- ✅ Nhúng JSON vào HTML: `window.EMBEDDED_DATA = {...}`

### **Bước 4: Commit to GitHub**
n8n tự động commit:
```bash
git add data/vsd_records.json
git commit -m "ci: update VSD data (330 records)"

git add docs/index.html web/vps_automation_vhck.html  
git commit -m "ci: update HTML with embedded data (330 records)"
```

### **Bước 5: Deploy to GitHub Pages**
- Dữ liệu tự động hiển thị trên: 
  - 🌐 https://doanhieu1986.github.io/vps-automation-vhck/

---

## 💾 Định Dạng Dữ Liệu

### JSON Output (`/data/vsd_records.json`)
```json
{
  "status": "success",
  "date": "2026-04-21",
  "records": [
    {
      "code": "LPB126018",
      "title": "LPB126018: Đăng ký trái phiếu",
      "url": "https://www.vsd.vn/vi/ad/194825",
      "date": "21/04/2026",
      "collected_date": "21/04/2026",
      "source": "VSD",
      "status": "pending",
      "tên_chứng_khoán": "Trái phiếu phát hành ra công chúng LPBank",
      "mã_isin": "VNLPB1260188",
      "tên_tổ_chức_đăng_ký": "Ngân hàng TMCP Lộc Phát Việt Nam",
      "nơi_giao_dịch": null,
      "loại_chứng_khoán": "Trái phiếu doanh nghiệp phát hành ra công chúng",
      ...
    }
  ]
}
```

### Status Types
- **pending** 🟠 - Chờ xử lý (dữ liệu mới vừa scrape)
- **confirmed** 🟢 - Đã xác nhận (VHCK đã review)
- **rejected** 🔴 - Bị từ chối (sai hoặc không cần)

---

## 🌐 Web Dashboard

### Tính Năng
- ✅ Hiển thị 330+ bản ghi trong bảng
- ✅ Tìm kiếm theo mã, tên, tổ chức
- ✅ Lọc theo ngày (date range)
- ✅ Lọc theo status (pending/confirmed/rejected)
- ✅ Xem chi tiết bằng cách click row
- ✅ Cập nhật status (pending→confirmed/rejected)
- ✅ Hiển thị thống kê (tổng, chờ xử lý, đã xác nhận, bị từ chối)

### Truy Cập
```
Local dev: file:///path/to/web/vps_automation_vhck.html
GitHub Pages: https://doanhieu1986.github.io/vps-automation-vhck/
```

---

## ⚙️ Cài Đặt & Chạy

### 1️⃣ Prerequisites
```bash
# Python 3.8+
python3 --version

# Node.js (cho n8n)
node --version
npm --version
```

### 2️⃣ Install Dependencies
```bash
# Python
cd scripts
pip install -r requirements.txt

# Node (nếu chưa cài n8n)
npm install -g n8n
```

### 3️⃣ Deploy Workflow to n8n
```bash
# Deploy v8 workflow
node scripts/deploy-v8.js

# Output:
# ✅ Deploy thành công!
# Workflow: VPS Automation VHCK v8 - Complete Flow
# ID: <workflow-id>
```

### 4️⃣ Configure GitHub Token
Tạo file `.github-token.json` (không commit):
```json
{
  "github": {
    "token": "ghp_your_github_pat",
    "owner": "doanhieu1986",
    "repo": "vps-automation-vhck"
  }
}
```

### 5️⃣ Run Workflow
- Tự động: Setup schedule trong n8n (hàng ngày)
- Thủ công: Click "Execute" trong n8n UI

---

## 🔧 Configuration

### fetch_vsd.py
```python
KEEP_DAYS = 7  # Số ngày lấy dữ liệu (thay đổi tại dòng 34)
```

### n8n Workflow Nodes
| Node | Purpose |
|------|---------|
| Manual Trigger | Bắt đầu workflow |
| Fetch VSD (Tin Tuc) | Chạy fetch_vsd.py |
| Verify Excel File | Kiểm tra file Excel |
| Embed JSON into HTML | Nhúng dữ liệu vào HTML |
| Commit to GitHub | Push JSON |
| Push to GitHub | Push HTML |
| Workflow Complete | Trả về kết quả |

---

## 📊 Monitoring & Troubleshooting

### Check Execution Status
```bash
# Xem logs từ n8n
n8n logs

# Hoặc vào n8n UI → Workflow executions
http://localhost:5678
```

### Common Issues

**❌ "fetch_vsd.py not found"**
```
Giải pháp: Đảm bảo path đúng: /app/vps-automation-vhck/scripts/fetch_vsd.py
```

**❌ "GitHub API 400 Bad Request"**
```
Giải pháp: Token hết hạn hoặc invalid, check .github-token.json
```

**❌ "Data not displaying on GitHub Pages"**
```
Giải pháp: 
- Refresh page (Ctrl+Shift+R)
- Check browser cache
- Verify docs/index.html has embedded data
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Tổng quan hệ thống (file này) |
| `CLAUDE.md` | Project instructions |
| `workflow.md` | Chi tiết quy trình luồng |
| `FETCH_VSD_LOGIC.md` | Logic scraping VSD |
| `COLUMN_DETERMINATION_LOGIC.md` | Logic xác định columns |
| `DEPLOYMENT_GUIDE.md` | Hướng dẫn deploy v8 |
| `output_requirement.md` | Yêu cầu output format |

---

## 🎯 Next Steps

1. ✅ Configure GitHub token (`.github-token.json`)
2. ✅ Deploy workflow to n8n (`node scripts/deploy-v8.js`)
3. ✅ Test manual execution
4. ✅ Setup schedule (hàng ngày, 2 lần/ngày)
5. ✅ Monitor executions
6. ✅ Access dashboard: https://doanhieu1986.github.io/vps-automation-vhck/

---

## 📞 Support

Tất cả tài liệu liên quan:
- CLAUDE.md - Project instructions
- workflow.md - Quy trình chi tiết  
- FETCH_VSD_LOGIC.md - Scraping logic
- DEPLOYMENT_GUIDE.md - Deploy steps

---

**Last Updated:** 2026-04-21  
**Version:** v8 - Complete Flow  
**Status:** ✅ Active & Deployed
