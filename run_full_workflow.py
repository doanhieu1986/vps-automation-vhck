#!/usr/bin/env python3
"""
Complete workflow: Fetch → Process → Save → Display
This script simulates the full N8n workflow locally
"""

import subprocess
import json
import sys
import requests
from datetime import datetime

def run_fetch_script():
    """Run fetch_all_v2.py"""
    print("=" * 70)
    print("📋 FULL WORKFLOW EXECUTION")
    print("=" * 70)

    print("\n📌 STEP 1: Reading symbols from symbol.md...")
    symbols = []
    try:
        with open('/Users/hieudt/vps-automation-vhck/symbol.md', 'r') as f:
            symbols = [s.strip() for s in f.readlines() if s.strip() and not s.startswith('#')]
    except:
        print("❌ Error reading symbol.md")
        return None

    print(f"✓ Found {len(symbols)} symbols: {', '.join(symbols)}")

    print("\n📌 STEP 2: Executing fetch_all_v2.py with cascade logic...")
    try:
        result = subprocess.run(
            ['python3', '/Users/hieudt/vps-automation-vhck/scripts/fetch_all_v2.py'] + symbols,
            capture_output=True,
            text=True,
            timeout=60
        )

        fetch_output = result.stdout
        fetch_result = json.loads(fetch_output)

        print(f"✓ Fetch completed")
        print(f"  - Total symbols: {fetch_result.get('total_symbols')}")
        print(f"  - Found: {fetch_result.get('found_count')}")

        return fetch_result

    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Fetch Error: {e}")
        return None

def process_results(fetch_result):
    """Process fetch results"""
    print("\n📌 STEP 3: Processing and structuring data...")

    if not fetch_result or 'records' not in fetch_result:
        print("❌ Invalid fetch result")
        return None

    records = []
    for record in fetch_result['records']:
        processed = {
            'symbol': record['symbol'],
            'mã_chứng_khoán': record['symbol'],
            'tên_tổ_chức_đăng_ký': 'Cần cập nhật',
            'tên_chứng_khoán': 'Cần cập nhật',
            'mã_isin': 'Cần cập nhật',
            'nơi_giao_dịch': record.get('primary_source', 'N/A'),
            'loại_chứng_khoán': 'Trái Phiếu',
            'ngày_đăng_ký_cuối': 'Cần cập nhật',
            'lý_do_mục_đích': 'Cần cập nhật',
            'tỷ_lệ_thực_hiện': 'Cần cập nhật',
            'thời_gian_thực_hiện': 'Cần cập nhật',
            'địa_điểm_thực_hiện': 'Cần cập nhật',
            'quyền_nhận_lãi': 'Cần cập nhật',
            'quyền_trả_gốc': 'Cần cập nhật',
            'quyền_chuyển_đổi': 'Cần cập nhật',
            'quyền_khác': 'Cần cập nhật',
            'status': 'pending',
            'confirmation_status': 'awaiting_review',
            'collected_at': datetime.now().isoformat(),
            'fetch_status': record.get('status', 'not_found'),
            'vsd_status': record.get('vsd', {}).get('status'),
            'hnx_status': record.get('hnx', {}).get('status'),
            'hose_status': record.get('hose', {}).get('status'),
            'source_links': {
                'vsd': 'https://www.vsd.vn/vi/tin-thi-truong-co-so',
                'hnx': 'https://www.hnx.vn/vi-vn/trai-phieu',
                'hose': 'https://www.hsx.vn/vi/tra-cuu/chung-chi'
            }
        }
        records.append(processed)

    print(f"✓ Processed {len(records)} records")
    return records

def generate_markdown(records):
    """Generate markdown report"""
    print("\n📌 STEP 4: Generating markdown report...")

    summary = {
        'total': len(records),
        'found': sum(1 for r in records if r['fetch_status'] != 'not_found'),
        'not_found': sum(1 for r in records if r['fetch_status'] == 'not_found'),
        'pending_confirmation': sum(1 for r in records if r['confirmation_status'] == 'awaiting_review'),
        'confirmed': sum(1 for r in records if r['confirmation_status'] == 'confirmed'),
        'rejected': sum(1 for r in records if r['confirmation_status'] == 'rejected')
    }

    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    markdown = f"""# Kết Quả Thu Thập Thông Tin Quyền Chứng Khoán

## 📊 Thống Kê

- **Cập nhật lúc:** {timestamp}
- **Tổng bản ghi:** {summary['total']}
- **Tìm thấy:** {summary['found']}
- **Không tìm thấy:** {summary['not_found']}
- **Chờ xác nhận:** {summary['pending_confirmation']}
- **Đã xác nhận:** {summary['confirmed']}
- **Bị từ chối:** {summary['rejected']}

---

## 📋 Chi Tiết Từng Mã

"""

    for idx, record in enumerate(records, 1):
        markdown += f"""
### {idx}. {record['symbol']}

**Trạng thái tìm kiếm:**
- Trạng thái: {record['fetch_status']}
- Nguồn (nếu tìm thấy): {record['nơi_giao_dịch']}
- VSD: {record['vsd_status']}
- HNX: {record['hnx_status']}
- HOSE: {record['hose_status']}

**Thông tin chứng khoán:**

| Trường | Giá trị |
|-------|--------|
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

**Quyền:**

- **Quyền nhận lãi:** {record['quyền_nhận_lãi']}
- **Quyền trả gốc:** {record['quyền_trả_gốc']}
- **Quyền chuyển đổi:** {record['quyền_chuyển_đổi']}
- **Quyền khác:** {record['quyền_khác']}

**Thông tin xác nhận:**

- **Trạng thái xác nhận:** {record['confirmation_status']}
- **Trạng thái:** {record['status']}
- **Thu thập lúc:** {record['collected_at']}

**Liên kết nguồn:**

- [VSD - Tin tức thị trường](https://www.vsd.vn/vi/tin-thi-truong-co-so)
- [HNX - Trái phiếu](https://www.hnx.vn/vi-vn/trai-phieu)
- [HOSE - Chứng chỉ](https://www.hsx.vn/vi/tra-cuu/chung-chi)

---
"""

    print(f"✓ Generated markdown ({len(markdown)} characters)")
    return markdown

def save_result(markdown, records):
    """Save to Flask API"""
    print("\n📌 STEP 5: Saving to Flask API...")

    try:
        response = requests.post(
            'http://localhost:3000/api/save-result',
            json={
                'markdown': markdown,
                'records': records,
                'summary': {
                    'total': len(records),
                    'timestamp': datetime.now().isoformat()
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Saved successfully")
            print(f"  - File: {result.get('file')}")
            print(f"  - Records: {result.get('records_count')}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Save Error: {e}")
        return False

def main():
    """Main workflow"""
    print()

    # Step 1: Fetch
    fetch_result = run_fetch_script()
    if not fetch_result:
        print("\n❌ Workflow failed at fetch stage")
        sys.exit(1)

    # Step 2: Process
    records = process_results(fetch_result)
    if not records:
        print("\n❌ Workflow failed at process stage")
        sys.exit(1)

    # Step 3: Generate
    markdown = generate_markdown(records)
    if not markdown:
        print("\n❌ Workflow failed at generate stage")
        sys.exit(1)

    # Step 4: Save
    if not save_result(markdown, records):
        print("\n❌ Workflow failed at save stage")
        sys.exit(1)

    # Success
    print("\n" + "=" * 70)
    print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print("\n📂 Next Steps:")
    print("  1. Open Web Interface: web/vps_automation_vhck.html")
    print("  2. Review collected data")
    print("  3. Confirm or edit information")
    print("  4. System updates result.md status")
    print("\n")

if __name__ == '__main__':
    main()
