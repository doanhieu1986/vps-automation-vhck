# Dashboard UI - VPS Automation VHCK v8.1

## 📊 Tổng Quan Dashboard

Dashboard là giao diện web tương tác để xem, tìm kiếm và quản lý dữ liệu chứng khoán từ VSD.

**URL:** 
- Local: `/index.html` hoặc `/web/vps_automation_vhck.html`
- GitHub Pages: `https://doanhieu1986.github.io/vps-automation-vhck/`

**Cập nhật:** Tự động sau mỗi lần chạy workflow

---

## 🎨 Bố Cục Giao Diện

### Header (Phần đầu)
```
┌─────────────────────────────────────────────────────────┐
│ VPS Automation VHCK                                     │
│ Hệ thống Quản Lý Quyền Chứng Khoán                      │
├─────────────────────────────────────────────────────────┤
│ Tổng Bản Ghi: 409  │  Đã Xác Nhận: 0  │  Chờ Xử Lý: 409│
└─────────────────────────────────────────────────────────┘
```

**Thông tin thống kê:**
- **TỔNG BẢN GHI**: Tổng số bản ghi (records) trong hệ thống
- **ĐÃ XÁC NHẬN**: Số bản ghi đã xác nhận (status = confirmed)
- **BỊ TỪ CHỐI**: Số bản ghi bị từ chối (status = rejected)
- **CHỜ XỬ LÝ**: Số bản ghi chưa xác nhận (status = pending)

---

## 🔍 Toolbar (Thanh Công Cụ)

### 1. Ô Tìm Kiếm (Search Box)
```
┌──────────────────────────────────────────────────────┐
│ Tìm kiếm theo mã, tên tổ chức hoặc tên chứng khoán.. │
└──────────────────────────────────────────────────────┘
```

**Tìm kiếm theo:**
- **Mã CK** (code): VNG, FPT, GEX, etc.
- **Tên Tổ Chức Đăng Ký**: Công ty, ngân hàng, etc.
- **Tên Chứng Khoán**: Tên chứng khoán liên quan

Tìm kiếm **thực hiện tức thời** (real-time) khi gõ.

### 2. Lọc Theo Khoảng Thời Gian
```
Từ ngày: [dd/mm/yyyy]  Đến ngày: [dd/mm/yyyy]  [Áp Dụng Lọc] [Xóa lọc ngày]
```

**Cách dùng:**
1. Chọn ngày bắt đầu (Từ ngày)
2. Chọn ngày kết thúc (Đến ngày)
3. Nhấn "Áp Dụng Lọc"
4. Nhấn "Xóa lọc ngày" để hủy

### 3. Lọc Theo Trạng Thái
```
[Tất Cả] [Chờ Xử Lý] [Đã Xác Nhận] [Bị Từ Chối]
```

**Trạng thái:**
- **Tất Cả**: Hiển thị tất cả bản ghi
- **Chờ Xử Lý** (pending): Bản ghi mới, chưa xác nhận
- **Đã Xác Nhận** (confirmed): Đã review và xác nhận
- **Bị Từ Chối** (rejected): Không hợp lệ, bị loại

---

## 📋 Bảng Dữ Liệu (Data Table)

### Cột Hiển Thị
```
┌──────┬────────────────────┬──────────────────┬───────────────┬──────────┬──────────┐
│ MÃ   │ TÊN CHỨNG KHOÁN    │ TỔ CHỨC ĐĂNG KÝ  │ NỚI GIAO DỊCH │ LOẠI CK  │ TRẠNG    │
│ CK   │                    │                  │               │          │ THÁI     │
├──────┼────────────────────┼──────────────────┼───────────────┼──────────┼──────────┤
│ VSH  │ Cổ Phiếu CTCP...   │ CTCP Thuỷ Điện...│ HOSE          │ Cổ phiếu │ PENDING  │
│ GEX  │ Cổ Phiếu GELEX     │ Công ty GELEX    │ HOSE          │ Cổ phiếu │ PENDING  │
└──────┴────────────────────┴──────────────────┴───────────────┴──────────┴──────────┘
```

**6 Cột Chính:**
1. **MÃ CK**: Mã chứng khoán (VSH, GEX, etc.)
2. **TÊN CHỨNG KHOÁN**: Tên đầy đủ của chứng khoán
3. **TỔ CHỨC ĐĂNG KÝ**: Công ty/tổ chức phát hành
4. **NỚI GIAO DỊCH**: Sàn giao dịch (HOSE, HNX, etc.)
5. **LOẠI CK**: Loại chứng khoán (Cổ phiếu, Trái phiếu, etc.)
6. **TRẠNG THÁI**: Status badge (PENDING, CONFIRMED, REJECTED)

### Tương Tác Với Bảng
- **Click vào dòng**: Mở chi tiết modal (không cần nút riêng)
- Dòng có `cursor: pointer` để chỉ dẫn click được

---

## 🔎 Modal Chi Tiết (Detail View)

### Kích Thước & Vị Trí
- **Chiều rộng**: 1400px (95% màn hình nếu nhỏ hơn)
- **Chiều cao**: 85vh (85% chiều cao viewport)
- **Vị trí**: Căn giữa cả chiều ngang và chiều dọc
- **Background**: Dark overlay (80% opacity) che lại bảng

### Bố Cục Modal (2 Cột)

```
┌─────────────────────────────────────────────────────────────┐
│ Chi tiết mã CK                                       [X]     │
├──────────────────────────┬──────────────────────────────────┤
│ [Cột Trái - Thông Tin]   │ [Cột Phải - Nội Dung Tin Tức]   │
│                          │                                  │
│ Thông Tin Cơ Bản         │ Nội Dung Chính Của Tin Tức      │
│ • Mã Chứng Khoán         │ (Full text from VSD news)       │
│ • Tên Chứng Khoán        │ (Scrollable)                    │
│ • Tổ Chức Đăng Ký        │                                 │
│ • Mã ISIN                │                                 │
│ • Nơi Giao Dịch          │                                 │
│ • Loại Chứng Khoán       │                                 │
│                          │                                 │
│ Thông Tin Thực Hiện      │                                 │
│ • Ngày Đăng Ký Cuối      │                                 │
│ • Thời Gian Thực Hiện    │                                 │
│ • Địa Điểm Thực Hiện     │                                 │
│                          │                                 │
│ Quyền và Lợi Ích         │                                 │
│ • Quyền Họp Đại Hội      │                                 │
│ • Quyền Cổ Tức Tiền      │                                 │
│ • Quyền Cổ Tức Cổ Phiếu  │                                 │
│ • Quyền Mua              │                                 │
│ • Quyền Hoán Đổi/Chuyển  │                                 │
│ • Chứng Quyền            │                                 │
│ • Chấp Thuận Đăng Ký     │                                 │
│ • Tin Hủy                │                                 │
│ • Thay Đổi               │                                 │
│                          │                                 │
│ Lý Do / Mục Đích         │                                 │
│ Tỷ Lệ Thực Hiện          │                                 │
│                          │                                 │
│ Nguồn Dữ Liệu            │                                 │
│ [Xem trên nguồn gốc] →   │                                 │
├──────────────────────────┴──────────────────────────────────┤
│ [Xác Nhận]  [Từ Chối]  [Đóng]                              │
└─────────────────────────────────────────────────────────────┘
```

### Cột Trái: Thông Tin Chi Tiết
**Phần 1: Thông Tin Cơ Bản**
- Mã Chứng Khoán
- Tên Chứng Khoán
- Tổ Chức Đăng Ký
- Mã ISIN
- Nơi Giao Dịch
- Loại Chứng Khoán

**Phần 2: Thông Tin Thực Hiện**
- Ngày Đăng Ký Cuối
- Thời Gian Thực Hiện
- Địa Điểm Thực Hiện

**Phần 3: Quyền và Lợi Ích** (9 trường)
- Quyền Họp Đại Hội Cổ Đông
- Quyền Cổ Tức Tiền
- Quyền Cổ Tức Cổ Phiếu
- Quyền Mua
- Quyền Hoán Đổi / Chuyển Đổi
- Chứng Quyền
- Chấp Thuận Đăng Ký
- Tin Hủy
- Thay Đổi
- Lý Do / Mục Đích
- Tỷ Lệ Thực Hiện

**Phần 4: Nguồn Dữ Liệu**
- URL Gốc: Link đến bài tin trên VSD

### Cột Phải: Nội Dung Tin Tức
- Hiển thị **toàn bộ nội dung ban đầu** từ bài tin VSD
- Dùng để **so sánh và kiểm tra** giữa dữ liệu trích xuất và nội dung gốc
- Cuộn độc lập (không ảnh hưởng đến cột trái)
- Chỉ hiển thị nếu có dữ liệu text_content

### Nút Hành Động
- **Xác Nhận**: Đánh dấu bản ghi là confirmed (tính năng sắp tới)
- **Từ Chối**: Đánh dấu bản ghi là rejected (tính năng sắp tới)
- **Đóng**: Đóng modal quay lại bảng

---

## 🔄 Luồng Tương Tác

### Tìm Kiếm Bản Ghi
```
1. Nhập text trong ô tìm kiếm
   ↓
2. Bảng tự động lọc (real-time)
   ↓
3. Hiển thị chỉ những bản ghi khớp
   ↓
4. Click vào bản ghi để xem chi tiết
```

### Xem Chi Tiết
```
1. Click vào dòng bảng
   ↓
2. Modal chi tiết mở ra (overlay với dark background)
   ↓
3. Xem thông tin chi tiết trên cột trái
   ↓
4. So sánh với nội dung tin tức trên cột phải
   ↓
5. Nhấn "Đóng" để quay lại bảng
```

### Lọc Kết Hợp
```
1. Nhập từ khóa tìm kiếm
   ↓
2. Chọn khoảng thời gian (nếu cần)
   ↓
3. Chọn trạng thái (pending/confirmed/rejected)
   ↓
4. Bảng hiển thị kết quả hợp nhất từ 3 bộ lọc
```

---

## 📱 Responsive Design

- **Desktop (> 1400px)**: 2 cột modal, full width
- **Tablet (768px - 1400px)**: Modal 95% width, columns adjust
- **Mobile (< 768px)**: Modal full width (nếu modal support mobile)

---

## 🎯 Tính Năng Chính

✅ **Tìm kiếm real-time** theo mã, tên, tổ chức
✅ **Lọc theo thời gian** (khoảng ngày)
✅ **Lọc theo trạng thái** (pending/confirmed/rejected)
✅ **Click để xem chi tiết** (không cần nút riêng)
✅ **Modal 2 cột** (thông tin + nội dung gốc)
✅ **Modal căn giữa** và khô lớn (1400x85vh)
✅ **Dark overlay** (80% opacity) khi mở modal
✅ **Thống kê trực tiếp** (tổng, xác nhận, từ chối, chờ xử lý)
✅ **Auto-update** khi workflow chạy

---

## 🔧 Tùy Chỉnh

### Thay đổi kích thước modal
File: `docs/index.html`, CSS `.modal-content`
```css
max-width: 1400px;  /* Chiều rộng tối đa */
height: 85vh;       /* Chiều cao */
```

### Thay đổi độ tối overlay
File: `docs/index.html`, CSS `.modal`
```css
background: rgba(0,0,0,0.8);  /* 0-1: 0=trong suốt, 1=đen đặc */
```

### Thêm/Xóa cột trong bảng
File: `docs/index.html`, function `initializeTable()`
```javascript
row.innerHTML = `
  <td>${record.code || 'N/A'}</td>
  <td>${record.tên_chứng_khoán || 'N/A'}</td>
  <!-- Thêm <td> mới tại đây -->
`;
```

---

## 📝 Lịch Sử Phiên Bản

### v8.1 (2026-04-23)
- ✨ Thêm 2-cột modal (thông tin + nội dung gốc)
- ✨ Modal căn giữa và kích thước lớn hơn
- ✨ Dark overlay 80% opacity
- 🔧 Fix tìm kiếm và lọc kết hợp
- 🔧 Populate tất cả trường quyền và lợi ích

### v8.0 (2026-04-21)
- 🎉 Phiên bản ổn định đầu tiên
- ✨ Dashboard interactive
- ✨ Table search & filter
- ✨ Click-to-view-details modal

---

**Last Updated:** 2026-04-23
**Version:** v8.1 - Dashboard Interactive
**Status:** ✅ Production Ready
