# Hướng dẫn Deploy Workflow lên n8n

## 📋 Tổng quan

Có 3 cách để deploy workflow lên n8n UI khi thay đổi file JSON:

### 1. **Auto Deploy via Git Commit** (Tự động)
```bash
# Chỉ cần commit thay đổi workflow
git add n8n/VPS\ Automation\ VHCK\ v7\ -\ Direct\ Excel\ Export.json
git commit -m "Update workflow"
# Hook sẽ tự động deploy lên n8n
```

**Ưu điểm:** Tự động, không cần làm gì thêm  
**Nhược điểm:** Chỉ hoạt động khi commit

---

### 2. **Watch & Auto Deploy** (Realtime)
```bash
# Chạy script watch trong terminal
node scripts/watch-workflow.js
```

**Ưu điểm:**  
- Monitor file realtime, tự động deploy khi save  
- Không cần commit
- Hiệu quả khi phát triển  

**Nhược điểm:** Cần giữ terminal chạy

**Cách sử dụng:**
1. Mở terminal và chạy: `node scripts/watch-workflow.js`
2. Thay đổi file workflow JSON trong editor
3. Script sẽ tự động deploy lên n8n
4. Nhấn `Ctrl+C` để dừng watching

---

### 3. **Manual Deploy** (Thủ công)
```bash
# Chạy script deploy thủ công
node scripts/deploy-workflow.js
```

**Output:**
```
📝 Đang đọc workflow file...
📤 Đang deploy workflow: VPS Automation VHCK v7 - Direct Excel Export
   Workflow ID: gSi7vlUxGOvRrGVF
✅ Deploy thành công!
   Workflow: VPS Automation VHCK v7 - Direct Excel Export
   Status: 🟢 Active
   Nodes: 6
   Updated: 13:23:16 21/4/2026
```

---

## 🔧 Configuration

Scripts sử dụng các giá trị từ `scripts/deploy-workflow.js`:
- **n8n URL:** `http://localhost:5678`
- **API Key:** Đã được set sẵn
- **Workflow ID:** `gSi7vlUxGOvRrGVF`

Để thay đổi, edit file `scripts/deploy-workflow.js`:
```javascript
const N8N_URL = 'http://localhost:5678';
const API_KEY = 'your-api-key-here';
```

---

## 🚀 Workflow Cập nhật

Các cập nhật được deploy:
- ✅ Node definitions
- ✅ Connections
- ✅ Node parameters (bao gồm JavaScript code)
- ✅ Workflow name
- ✅ Settings cơ bản

---

## ⚠️ Lưu ý

1. **n8n phải chạy** trên `http://localhost:5678`
2. **API Key phải hợp lệ**
3. **Workflow ID phải khớp** với workflow trong n8n
4. Sau khi deploy, **refresh n8n UI** để thấy thay đổi (F5)

---

## 🐛 Troubleshooting

### "Connection refused"
```
Error: connect ECONNREFUSED 127.0.0.1:5678
```
**Giải pháp:** Chắc chắn n8n đang chạy: `http://localhost:5678`

### "API Key invalid"
```
HTTP 401: 'X-N8N-API-KEY' header required
```
**Giải pháp:** Check API Key trong `scripts/deploy-workflow.js`

### "Workflow not found"
```
HTTP 404: Not found
```
**Giải pháp:** Check Workflow ID khớp với workflow trong n8n

---

## 📝 Ví dụ workflow quy trình

```
1. Edit file JSON workflow
   ↓
2. Chọn một trong 3 cách deploy:
   - Commit (auto via hook) ← Recommended
   - Watch script (realtime)
   - Manual deploy
   ↓
3. Script deploy-workflow.js chạy
   ↓
4. Gửi PUT request tới n8n API
   ↓
5. n8n update workflow
   ↓
6. Refresh n8n UI (F5)
   ↓
7. ✅ Workflow updated!
```

---

## 📚 File liên quan

- `scripts/deploy-workflow.js` - Script deploy chính
- `scripts/watch-workflow.js` - Script watch file
- `.git/hooks/post-commit` - Git hook tự động deploy
- `n8n/VPS Automation VHCK v7 - Direct Excel Export.json` - Workflow file

