# Logic Xác định Giá trị Cột "Nơi giao dịch" và "Loại chứng khoán"

## 📋 Tổng quan

Hai cột "Nơi giao dịch" (Place of Trading) và "Loại chứng khoán" (Securities Type) được xác định thông qua hai giai đoạn:
1. **Giai đoạn 1 (Script):** `fetch_vsd.py` cố gắng trích xuất từ HTML cấu trúc tiêu chuẩn
2. **Giai đoạn 2 (Workflow):** Node "Process & Structure Data" trong n8n xử lý fallback nếu script không tìm được

---

## 🔧 Giai đoạn 1: Trích xuất từ Script (`fetch_vsd.py`)

### 1.1 Logic "Nơi giao dịch" (Nơi giao dịch)

**Vị trí code:** `fetch_vsd.py` lines 174-175

```python
elif 'nơi giao dịch' in label:
    info['nơi_giao_dịch'] = value
```

**Cơ chế:**
- Script tìm kiếm tất cả các `<div class="col-md-4">` (label divs)
- Kiểm tra xem text của label có chứa chuỗi `"nơi giao dịch"` (không phân biệt hoa/thường)
- Nếu tìm thấy, lấy giá trị từ `<div class="col-md-8">` tiếp theo (value div)
- Giá trị được lưu vào `info['nơi_giao_dịch']`

**HTML structure mục tiêu:**
```html
<div class="col-md-4">Nơi giao dịch:</div>
<div class="col-md-8">HOSE</div>
```

**Các giá trị có thể:**
- `HOSE` (Sở giao dịch chứng khoán TP.HCM)
- `HNX` (Sở giao dịch chứng khoán Hà Nội)
- `UPCOM` (Sàn giao dịch
- Các giá trị khác tùy theo tin tức VSD

**Fallback (nếu không tìm được):**
- Script trả về `None` nếu không tìm thấy label chứa "nơi giao dịch"

---

### 1.2 Logic "Loại chứng khoán" (Loại chứng khoán)

**Vị trí code:** `fetch_vsd.py` lines 176-177

```python
elif 'loại chứng khoán' in label:
    info['loại_chứng_khoán'] = value
```

**Cơ chế:**
- Script tìm kiếm tất cả các `<div class="col-md-4">` (label divs)
- Kiểm tra xem text của label có chứa chuỗi `"loại chứng khoán"` (không phân biệt hoa/thường)
- Nếu tìm thấy, lấy giá trị từ `<div class="col-md-8">` tiếp theo (value div)
- Giá trị được lưu vào `info['loại_chứng_khoán']`

**HTML structure mục tiêu:**
```html
<div class="col-md-4">Loại chứng khoán:</div>
<div class="col-md-8">Trái phiếu</div>
```

**Các giá trị có thể:**
- `Trái phiếu` (Bond/Debenture)
- `Cổ phiếu` (Stock/Equity)
- `Chứng chỉ lợi suất` (Yield Certificate)
- Các loại chứng khoán khác tùy theo tin tức VSD

**Fallback (nếu không tìm được):**
- Script trả về `None` nếu không tìm thấy label chứa "loại chứng khoán"

---

## 📊 Giai đoạn 2: Xử lý trong Workflow n8n

### Node "Process & Structure Data"

Node này xử lý các records từ node "Combine Results" và áp dụng logic fallback cho các trường có giá trị `null`.

**Vị trí:** n8n workflow "VPS Automation VHCK v6 - Simplified (All Sources) - EDIT" > Node "Process & Structure Data"

### 2.1 Logic xử lý "Nơi giao dịch"

```javascript
nơi_giao_dịch: record.nơi_giao_dịch || "Logic chưa xác định được"
```

**Luồng xử lý:**

```
1. Kiểm tra record.nơi_giao_dịch có giá trị?
   ├─ CÓ (ví dụ: "HOSE") → Sử dụng giá trị này
   └─ KHÔNG (null/undefined)
      │
      └─ Sử dụng "Logic chưa xác định được" (indicator)
```

**Giải thích:**
- `record.nơi_giao_dịch`: Giá trị trích xuất từ HTML VSD (HOSE, HNX, UPCOM, v.v.)
- `"Logic chưa xác định được"`: **Indicator** chỉ ra rằng script **không thể trích xuất** giá trị này từ HTML
  - Đây KHÔNG phải dữ liệu thực tế
  - Đây là **tín hiệu cho VHCK** biết rằng có thể cần xem xét thủ công hoặc script cần cải thiện

**Các tình huống:**
| record.nơi_giao_dịch | Kết quả |
|---|---|
| "HOSE" | **"HOSE"** |
| "HNX" | **"HNX"** |
| "UPCOM" | **"UPCOM"** |
| null | **"Logic chưa xác định được"** |

---

### 2.2 Logic xử lý "Loại chứng khoán"

```javascript
loại_chứng_khoán: record.loại_chứng_khoán || "Logic chưa xác định được"
```

**Luồng xử lý:**

```
1. Kiểm tra record.loại_chứng_khoán có giá trị?
   ├─ CÓ (ví dụ: "Trái phiếu") → Sử dụng giá trị này
   └─ KHÔNG (null/undefined)
      │
      └─ Sử dụng "Logic chưa xác định được" (indicator)
```

**Giải thích:**
- `record.loại_chứng_khoán`: Giá trị trích xuất từ HTML VSD (Trái phiếu, Cổ phiếu, v.v.)
- `"Logic chưa xác định được"`: **Indicator** chỉ ra rằng script **không thể trích xuất** giá trị này từ HTML
  - Đây KHÔNG phải dữ liệu thực tế
  - Đây là **tín hiệu cho VHCK** biết rằng có thể cần xem xét thủ công hoặc script cần cải thiện

**Các tình huống:**
| record.loại_chứng_khoán | Kết quả |
|---|---|
| "Trái phiếu" | **"Trái phiếu"** |
| "Cổ phiếu" | **"Cổ phiếu"** |
| null | **"Logic chưa xác định được"** |

---

## 🔄 Luồng xử lý Toàn cầu

```
┌─────────────────────────────────────────────┐
│  fetch_vsd.py (Giai đoạn 1)                │
├─────────────────────────────────────────────┤
│                                             │
│  1. Tìm label chứa "nơi giao dịch"         │
│     ├─ Tìm thấy? → Lấy giá trị             │
│     └─ Không? → nơi_giao_dịch = null      │
│                                             │
│  2. Tìm label chứa "loại chứng khoán"      │
│     ├─ Tìm thấy? → Lấy giá trị             │
│     └─ Không? → loại_chứng_khoán = null   │
│                                             │
│  Output: {                                 │
│    nơi_giao_dịch: "HOSE" | null          │
│    loại_chứng_khoán: "Trái phiếu" | null │
│    source: "VSD"                          │
│    ...                                     │
│  }                                         │
└─────────────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────┐
│  n8n Workflow (Giai đoạn 2)                │
│  "Process & Structure Data" Node           │
├─────────────────────────────────────────────┤
│                                             │
│  nơi_giao_dịch:                            │
│    = record.nơi_giao_dịch ||              │
│      record.source ||                      │
│      "N/A"                                 │
│                                             │
│  loại_chứng_khoán:                        │
│    = record.loại_chứng_khoán ||           │
│      "Logic chưa xác định được"           │
│                                             │
│  Output: {                                 │
│    nơi_giao_dịch: "HOSE" | "VSD" | "N/A" │
│    loại_chứng_khoán: "Trái phiếu" |       │
│                     "Logic chưa..."       │
│    ...                                     │
│  }                                         │
└─────────────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────┐
│  Excel Output / Final Data                 │
└─────────────────────────────────────────────┘
```

---

## 🎯 Nguyên tắc thiết kế

### Tính Transparency (Tính minh bạch)

**Mục đích:** Cho phép VHCK dễ dàng phát hiện khi script không thể trích xuất được thông tin

**Cơ chế:**

| Trường | Khi tìm được | Khi không tìm được |
|---|---|---|
| **nơi_giao_dịch** | Giá trị từ VSD (HOSE, HNX, ...) | Fallback: `source` ("VSD") hoặc "N/A" |
| **loại_chứng_khoán** | Giá trị từ VSD (Trái phiếu, Cổ phiếu, ...) | **Indicator:** "Logic chưa xác định được" |

**Tại sao khác biệt?**
- `nơi_giao_dịch`: Có fallback logic hợp lý (sử dụng nguồn dữ liệu), nên không cần indicator rõ ràng
- `loại_chứng_khoán`: **Không có fallback logic hợp lý** vì loại chứng khoán phải xác định rõ ràng, nên dùng "Logic chưa xác định được" để báo hiệu trích xuất thất bại

### Bảo vệ Dữ liệu Gốc

**Nguyên tắc:** Dữ liệu từ script không được thêm logic hay suy luận nếu chưa được yêu cầu

**Áp dụng:**
- Giai đoạn 1 (script): Chỉ trích xuất, không suy luận hay biến đổi giá trị
- Giai đoạn 2 (workflow): Xử lý fallback rõ ràng, sử dụng "indicator" thay vì giá trị giả tạo

---

## 📝 Tóm tắt

| Khía cạnh | Nơi giao dịch | Loại chứng khoán |
|---|---|---|
| **Trích xuất (Script)** | Label chứa "nơi giao dịch" | Label chứa "loại chứng khoán" |
| **Fallback (Workflow)** | "Logic chưa xác định được" | "Logic chưa xác định được" |
| **Indicator** | **Rõ ràng** ("Logic chưa...") | **Rõ ràng** ("Logic chưa...") |
| **VHCK Action** | Nếu "Logic chưa..." → xem lại HTML VSD | Nếu "Logic chưa..." → xem lại HTML VSD |

