#!/usr/bin/env python3
"""
Test script để simulate N8n workflow
Đọc symbols, fetch data, process, và save result.md
"""

import requests
import json
from datetime import datetime
import sys

# Configuration
SYMBOL_FILE = '/Users/hieudt/vps-automation-vhck/symbol.md'
SAVE_API = 'http://localhost:3000/api/save-result'

# URLs
VSD_URL = 'https://www.vsd.vn/vi/tin-thi-truong-co-so'
HNX_URL = 'https://www.hnx.vn/vi-vn/'
HOSE_URL = 'https://www.hsx.vn/vi/'

def read_symbols():
    """Đọc danh sách mã chứng khoán từ symbol.md"""
    print("📖 Đọc danh sách ký hiệu từ symbol.md...")
    try:
        with open(SYMBOL_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        symbols = [s.strip() for s in content.split('\n') if s.strip() and not s.startswith('#')]
        print(f"✓ Tìm thấy {len(symbols)} mã chứng khoán: {', '.join(symbols)}")
        return symbols
    except Exception as e:
        print(f"✗ Lỗi đọc file: {e}")
        return []

def fetch_url(url, name):
    """Fetch dữ liệu từ URL"""
    try:
        print(f"  ↳ Đang fetch từ {name}...", end=' ')
        response = requests.get(url, timeout=5)
        print(f"✓ (Status: {response.status_code})")
        return {
            'status_code': response.status_code,
            'size': len(response.content),
            'success': response.status_code == 200
        }
    except requests.exceptions.Timeout:
        print(f"✗ Timeout")
        return {'status_code': None, 'size': 0, 'success': False, 'error': 'Timeout'}
    except Exception as e:
        print(f"✗ Error: {str(e)[:30]}")
        return {'status_code': None, 'size': 0, 'success': False, 'error': str(e)}

def process_symbol(symbol):
    """Xử lý dữ liệu cho mỗi mã chứng khoán"""
    print(f"\n📌 Xử lý mã: {symbol}")

    # Fetch từ các nguồn
    vsd_data = fetch_url(VSD_URL, "VSD")
    hnx_data = fetch_url(HNX_URL, "HNX")
    hose_data = fetch_url(HOSE_URL, "HOSE")

    # Tạo record
    record = {
        'symbol': symbol,
        'mã_chứng_khoán': symbol,
        'tên_tổ_chức_đăng_ký': 'Đang cập nhật...',
        'tên_chứng_khoán': 'Đang cập nhật...',
        'mã_isin': 'Đang cập nhật...',
        'nơi_giao_dịch': 'Đang cập nhật...',
        'loại_chứng_khoán': 'Trái Phiếu',
        'ngày_đăng_ký_cuối': 'Đang cập nhật...',
        'lý_do_mục_đích': 'Phát hành vốn',
        'tỷ_lệ_thực_hiện': '100%',
        'thời_gian_thực_hiện': 'Đang cập nhật...',
        'địa_điểm_thực_hiện': 'Việt Nam',
        'quyền_nhận_lãi': 'Nhận lãi định kỳ',
        'quyền_trả_gốc': 'Trả gốc khi đáo hạn',
        'quyền_chuyển_đổi': 'N/A',
        'quyền_khác': 'N/A',
        'sources': {
            'vsd': VSD_URL,
            'hnx': HNX_URL,
            'hose': HOSE_URL
        },
        'vsd_status': vsd_data.get('status_code', 'N/A'),
        'hnx_status': hnx_data.get('status_code', 'N/A'),
        'hose_status': hose_data.get('status_code', 'N/A'),
        'status': 'pending',
        'collected_at': datetime.now().isoformat(),
        'note': 'Thông tin tạm thời - Cần manual review từ VSD/HNX/HOSE'
    }

    return record

def generate_markdown(records):
    """Tạo nội dung markdown từ danh sách records"""
    print("\n📝 Tạo markdown content...")

    header = f"""# Kết Quả Thu Thập Thông Tin Quyền Chứng Khoán

**Cập nhật lúc:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Trạng thái:** pending
**Tổng bản ghi:** {len(records)}

---

"""

    content = ""
    for idx, record in enumerate(records, 1):
        content += f"""## {idx}. {record['symbol']}

| Thông Tin | Chi Tiết |
|-----------|----------|
| Mã chứng khoán | {record['mã_chứng_khoán']} |
| Tên tổ chức đăng ký | {record['tên_tổ_chức_đăng_ký']} |
| Tên chứng khoán | {record['tên_chứng_khoán']} |
| Mã ISIN | {record['mã_isin']} |
| Nơi giao dịch | {record['nơi_giao_dịch']} |
| Loại chứng khoán | {record['loại_chứng_khoán']} |
| Ngày đăng ký cuối | {record['ngày_đăng_ký_cuối']} |
| Lý do/Mục đích | {record['lý_do_mục_đích']} |
| Tỷ lệ thực hiện | {record['tỷ_lệ_thực_hiện']} |
| Thời gian thực hiện | {record['thời_gian_thực_hiện']} |
| Địa điểm thực hiện | {record['địa_điểm_thực_hiện']} |

### Quyền

- **Quyền nhận lãi:** {record['quyền_nhận_lãi']}
- **Quyền trả gốc:** {record['quyền_trả_gốc']}
- **Quyền chuyển đổi:** {record['quyền_chuyển_đổi']}
- **Quyền khác:** {record['quyền_khác']}

**Trạng thái:** {record['status']}
**Ghi chú:** {record['note']}

**Fetch Status:**
- VSD: {record.get('vsd_status', 'N/A')}
- HNX: {record.get('hnx_status', 'N/A')}
- HOSE: {record.get('hose_status', 'N/A')}

**Nguồn:**
- [VSD]({record['sources']['vsd']})
- [HNX]({record['sources']['hnx']})
- [HOSE]({record['sources']['hose']})

---

"""

    return header + content

def save_result(markdown, records):
    """Gửi dữ liệu tới Flask API để save result.md"""
    print(f"\n💾 Gửi dữ liệu tới API ({SAVE_API})...")

    try:
        response = requests.post(SAVE_API, json={
            'markdown': markdown,
            'records': records,
            'summary': {
                'total': len(records),
                'status': 'collected',
                'timestamp': datetime.now().isoformat()
            }
        }, timeout=5)

        result = response.json()

        if response.status_code == 200:
            print(f"✓ Đã save thành công!")
            print(f"  ↳ {result.get('message', 'OK')}")
            return True
        else:
            print(f"✗ Lỗi: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Lỗi kết nối: {e}")
        return False

def main():
    """Main workflow"""
    print("=" * 60)
    print("🚀 VPS Automation VHCK - Test Workflow")
    print("=" * 60)

    # Bước 1: Đọc symbols
    symbols = read_symbols()
    if not symbols:
        print("✗ Không thể đọc danh sách ký hiệu!")
        return False

    # Bước 2: Xử lý từng symbol
    records = []
    for symbol in symbols:
        record = process_symbol(symbol)
        records.append(record)

    print(f"\n✓ Đã xử lý {len(records)} bản ghi")

    # Bước 3: Tạo markdown
    markdown = generate_markdown(records)
    print(f"✓ Markdown content: {len(markdown)} characters")

    # Bước 4: Save kết quả
    success = save_result(markdown, records)

    if success:
        print("\n" + "=" * 60)
        print("✅ WORKFLOW HOÀN THÀNH THÀNH CÔNG!")
        print("=" * 60)
        print(f"📍 File được lưu tại: /Users/hieudt/vps-automation-vhck/result.md")
        print(f"🌐 Mở web interface: web/vps_automation_vhck.html")
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ LỖI KHI SAVE RESULT")
        print("=" * 60)
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow bị dừng bởi người dùng")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Lỗi nghiêm trọng: {e}")
        sys.exit(1)
