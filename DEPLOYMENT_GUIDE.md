# Hướng Dẫn Deploy VPS Automation VHCK v8

## 📋 Tổng Quan

Hướng dẫn chi tiết deploy workflow **"VPS Automation VHCK v8 - Complete Flow"** lên n8n instance.

---

## 🚀 Quick Start

### 1️⃣ Prerequisites

```bash
# Node.js
node --version  # v14+

# n8n installed
npm install -g n8n

# n8n running
n8n start
# or: n8n start --tunnel (for webhook access)
```

### 2️⃣ Python Dependencies

```bash
cd scripts
pip install -r requirements.txt

# Cần có:
- requests
- beautifulsoup4
- pandas
- openpyxl
```

### 3️⃣ GitHub Token

Tạo file `.github-token.json` tại root:
```json
{
  "github": {
    "token": "ghp_your_github_personal_access_token",
    "owner": "doanhieu1986",
    "repo": "vps-automation-vhck"
  }
}
```

**Cách tạo token:**
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token
3. Scopes: `repo` (full control of private repositories)
4. Copy token & lưu vào `.github-token.json`

---

## 🔧 Deploy Methods

### **Method 1: Auto Deploy via Script** (Recommended)

```bash
node scripts/deploy-v8.js
```

**Output:**
```
🚀 Deploying VPS Automation VHCK v8...

📝 Đang đọc workflow v8 file...
📤 Đang deploy workflow: VPS Automation VHCK v8 - Complete Flow
   Workflow ID: <id>
   Nodes: 7

✅ Deploy thành công!
   Workflow: VPS Automation VHCK v8 - Complete Flow
   ID: <workflow-id>
   Status: 🔴 Inactive (kích hoạt trong n8n UI)
   Nodes: 7
   URL n8n: http://localhost:5678/workflow/<workflow-id>
```

**Ưu điểm:**
- ✅ Tự động
- ✅ Tạo workflow mới nếu chưa có
- ✅ Cập nhật nếu đã tồn tại

---

### **Method 2: Manual Import in n8n UI**

```bash
1. Mở n8n: http://localhost:5678

2. Menu → Import → From File

3. Chọn file: n8n/VPS\ Automation\ VHCK\ v8\ -\ Complete\ Flow.json

4. Click Import

5. Kiểm tra & kích hoạt workflow
```

---

### **Method 3: Copy-Paste JSON**

```bash
1. Mở n8n: http://localhost:5678

2. New Workflow

3. Menu → Edit as JSON

4. Paste content từ: n8n/VPS\ Automation\ VHCK\ v8\ -\ Complete\ Flow.json

5. Ctrl+S để save

6. Exit JSON editor & kích hoạt
```

---

## ⚙️ Configuration After Deploy

### Step 1: Verify Nodes

Workflow có 7 nodes:
- ✅ Manual Trigger
- ✅ Fetch VSD (Tin Tuc) - Python script node
- ✅ Verify Excel File
- ✅ Embed JSON into HTML
- ✅ Commit to GitHub
- ✅ Push to GitHub
- ✅ Workflow Complete

Mỗi node phải có **green checkmark** (valid config)

### Step 2: Setup Schedule (Optional)

**Tự động chạy hàng ngày:**

```
1. Workflow Settings (cog icon)

2. Triggers

3. Add Trigger → Cron

4. Cron expression:
   0 12,17 * * *    # 12:00 & 17:00 hàng ngày
   
   Hoặc:
   0 9 * * *        # 9:00 sáng hàng ngày
   
   Hoặc:
   30 8 * * 1-5     # 8:30 sáng thứ 2-6
```

### Step 3: Test Manual Execution

```
1. Click "Execute Workflow" button

2. Monitor execution:
   - Blue running state
   - Green success node
   - Red error node

3. Check output → Click "Workflow Complete" node

4. Expected output:
{
  "status": "success",
  "message": "Workflow completed! Data committed to GitHub",
  "github_url": "https://github.com/doanhieu1986/vps-automation-vhck",
  "pages_url": "https://doanhieu1986.github.io/vps-automation-vhck/",
  "records_committed": 330+
}
```

### Step 4: Activate Workflow

```
1. Click toggle "Active" (top right)

2. Workflow is now active & will execute on schedule

3. Monitor → Executions → see run history
```

---

## 🔍 Verify Deployment

### Check n8n
```bash
# Via UI
http://localhost:5678
→ Workflows → VPS Automation VHCK v8
→ Status: ✅ Active

# Via API
curl -H "X-N8N-API-KEY: your-key" \
  http://localhost:5678/api/v1/workflows | jq '.data[] | select(.name | contains("v8"))'
```

### Check GitHub
```bash
# Latest commit
git log --oneline -1

# Should show:
# abc1234 ci: update VSD data (330 records)
# xyz5678 ci: update HTML with embedded data (330 records)
```

### Check GitHub Pages
```
Browser: https://doanhieu1986.github.io/vps-automation-vhck/

Expected:
- 🌐 Dashboard loads
- 📊 Data table shows 330+ records
- 📈 Stats: Tổng Bản Ghi, Giá Sắc Xoăn, etc.
```

---

## 🐛 Troubleshooting

### ❌ "fetch_vsd.py: No such file or directory"

**Error Message:**
```
Error: Command 'python3' failed with status code 1
```

**Solution:**
```bash
# Check fetch_vsd.py exists
ls -la scripts/fetch_vsd.py

# Check shebang
head -1 scripts/fetch_vsd.py

# Should be: #!/usr/bin/env python3

# Verify executable
chmod +x scripts/fetch_vsd.py

# Test run manually
/usr/bin/python3 scripts/fetch_vsd.py
```

---

### ❌ "GitHub API 400: Bad Request"

**Error Message:**
```
HTTP 400: Bad Request
GitHub API {...}: Invalid base64 content
```

**Solution:**
```bash
# Check token validity
cat .github-token.json  # Token should be valid

# Check file paths in .github-token.json
{
  "github": {
    "token": "ghp_...",    ← Valid format
    "owner": "doanhieu1986",
    "repo": "vps-automation-vhck"
  }
}

# Token may have expired → regenerate new one
```

---

### ❌ "Data not showing on GitHub Pages"

**Debugging:**
```bash
# 1. Check if file was committed
git log --oneline | grep -i "update"

# 2. Check if data is embedded
curl -s https://doanhieu1986.github.io/vps-automation-vhck/ | grep -o "window.EMBEDDED_DATA"

# 3. Hard refresh browser
Ctrl+Shift+R  (Chrome/Firefox)
Cmd+Shift+R   (Mac)

# 4. Check GitHub Pages settings
GitHub Repo → Settings → Pages → Source: Branch main /docs
```

---

### ❌ "Workflow fails at 'Fetch VSD' node"

**Check:**
```bash
# 1. VSD website is accessible
curl -I https://www.vsd.vn/vi/tin-thi-truong-co-so

# 2. Python dependencies installed
pip list | grep -E "requests|beautifulsoup"

# 3. Check fetch_vsd.py syntax
python3 -m py_compile scripts/fetch_vsd.py  # Should return no error

# 4. Test manually
python3 scripts/fetch_vsd.py
```

---

### ❌ "Workflow hangs at 'Embed JSON' node"

**Solution:**
```bash
# File size too large?
ls -lh data/vsd_records.json

# If > 5MB, may timeout
# Reduce KEEP_DAYS in fetch_vsd.py:
# KEEP_DAYS = 3  (instead of 7)

# Then re-run workflow
```

---

## 📊 Monitoring & Logs

### n8n Execution History
```
http://localhost:5678/workflow/<workflow-id>/executions

Status indicators:
🟢 Success - All nodes executed
🔴 Error - One or more nodes failed
🟡 Running - Currently executing
⚪ Unknown - Pending
```

### View Node Output
```
1. Click on node → Output tab

2. See what was returned from previous node

3. Use this to debug issues
```

### Check GitHub Commits
```bash
git log --oneline -10

# Filter by n8n commits
git log --oneline --grep="ci:" -10
```

---

## 🚀 Scheduled Execution

### Setup Daily Schedule

```bash
n8n UI → Workflow Settings (v8) → Cron trigger

# Example: Run at 9 AM & 5 PM every day
0 9,17 * * *

# Example: Run weekdays only
0 9 * * 1-5

# Example: Run every hour
0 * * * *
```

### View Scheduled Runs
```
n8n UI → Workflow Executions → Filter by date range

Or:

git log --since="2 hours ago" --until="now" --oneline
```

---

## ✅ Success Checklist

After deployment:

- [ ] n8n is running: `http://localhost:5678`
- [ ] Workflow exists & is Active
- [ ] Python dependencies installed: `pip list`
- [ ] `.github-token.json` created & valid
- [ ] Manual test execution successful
- [ ] Schedule configured (if needed)
- [ ] GitHub commits visible: `git log`
- [ ] Dashboard accessible: `https://doanhieu1986.github.io/vps-automation-vhck/`
- [ ] Data displays correctly with 330+ records
- [ ] Test click on a record → detail modal opens

---

## 📞 Support

### Verify Installation
```bash
# Node.js
node -v
npm -v

# Python
python3 -v
pip list

# n8n
n8n --version
```

### Common Commands
```bash
# Start n8n
n8n start

# Start with tunnel (for webhooks)
n8n start --tunnel

# Stop n8n
Ctrl+C

# Check logs
n8n logs

# Reset n8n (CAUTION: deletes all workflows)
rm -rf ~/.n8n
```

---

## 📚 Files Involved

| File | Purpose |
|------|---------|
| `n8n/VPS Automation VHCK v8 - Complete Flow.json` | Workflow definition |
| `scripts/deploy-v8.js` | Deployment script |
| `scripts/fetch_vsd.py` | Main scraper |
| `.github-token.json` | GitHub API token (local, not in git) |
| `data/vsd_records.json` | Data output |
| `web/vps_automation_vhck.html` | Dashboard source |
| `docs/index.html` | GitHub Pages |

---

## 🎯 Next Steps

1. ✅ Run `node scripts/deploy-v8.js`
2. ✅ Verify workflow in n8n UI
3. ✅ Configure `.github-token.json`
4. ✅ Test manual execution
5. ✅ Setup schedule (optional)
6. ✅ Monitor first automatic run
7. ✅ Verify GitHub Pages update

---

**Last Updated:** 2026-04-21  
**Version:** v8 - Complete Flow  
**Status:** ✅ Production Ready
