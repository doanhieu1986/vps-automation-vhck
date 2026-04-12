#!/usr/bin/env python3
"""
Unified script to fetch bond information from all sources (VSD, HNX, HOSE)
This script calls individual fetchers and merges the results
"""

import subprocess
import json
import sys
import os
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

def run_fetcher(script_name, symbol):
    """Chạy script fetcher con và trả về kết quả JSON"""
    try:
        script_path = os.path.join(SCRIPTS_DIR, script_name)
        result = subprocess.run(
            ['python3', script_path, symbol],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0:
            try:
                # Parse JSON output từ stderr (to avoid mixing with stdout)
                data = json.loads(result.stdout)
                return data
            except json.JSONDecodeError:
                return {
                    'status': 'error',
                    'message': 'Invalid JSON output',
                    'raw_output': result.stdout
                }
        else:
            return {
                'status': 'error',
                'message': result.stderr or 'Unknown error',
                'returncode': result.returncode
            }

    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'message': 'Timeout'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def merge_results(symbol, vsd_data, hnx_data, hose_data):
    """Kết hợp kết quả từ các nguồn"""

    # Normalize data - vsd_data might be a list or dict
    if isinstance(vsd_data, list):
        vsd_result = vsd_data[0] if vsd_data else {'status': 'error'}
    else:
        vsd_result = vsd_data or {'status': 'error'}

    if isinstance(hnx_data, list):
        hnx_result = hnx_data[0] if hnx_data else {'status': 'error'}
    else:
        hnx_result = hnx_data or {'status': 'error'}

    if isinstance(hose_data, list):
        hose_result = hose_data[0] if hose_data else {'status': 'error'}
    else:
        hose_result = hose_data or {'status': 'error'}

    record = {
        'symbol': symbol,
        'mã_chứng_khoán': symbol,
        'collected_at': datetime.now().isoformat(),
        'sources': {
            'vsd': {
                'status': vsd_result.get('status', 'unknown'),
                'data': vsd_result.get('data', []) if isinstance(vsd_result, dict) else []
            },
            'hnx': {
                'status': hnx_result.get('status', 'unknown') if isinstance(hnx_result, dict) else 'error',
                'data': hnx_result.get('data', []) if isinstance(hnx_result, dict) else []
            },
            'hose': {
                'status': hose_result.get('status', 'unknown') if isinstance(hose_result, dict) else 'error',
                'data': hose_result.get('data', []) if isinstance(hose_result, dict) else []
            }
        }
    }

    # Trích xuất thông tin từ kết quả
    vsd_results = vsd_result.get('data', []) if isinstance(vsd_result, dict) else []
    hnx_results = hnx_result.get('data', []) if isinstance(hnx_result, dict) else []
    hose_results = hose_result.get('data', []) if isinstance(hose_result, dict) else []

    # Gộp dữ liệu từ các nguồn
    record['all_sources_data'] = {
        'vsd': vsd_results,
        'hnx': hnx_results,
        'hose': hose_results
    }

    # Đánh dấu trạng thái
    success_count = sum([
        1 for s in [vsd_data, hnx_data, hose_data]
        if isinstance(s, dict) and s.get('status') in ['success', 'partial']
    ])

    record['collection_status'] = {
        'total_sources': 3,
        'successful_sources': success_count,
        'overall': 'success' if success_count >= 1 else 'error'
    }

    return record

def fetch_symbol(symbol):
    """Fetch dữ liệu cho một mã chứng khoán từ tất cả nguồn"""
    print(f"📌 Fetching {symbol} từ tất cả sources...", file=sys.stderr)

    # Chạy các fetcher song song (mô phỏng)
    vsd_data = run_fetcher('fetch_vsd.py', symbol)
    hnx_data = run_fetcher('fetch_hnx.py', symbol)
    hose_data = run_fetcher('fetch_hose.py', symbol)

    # Kết hợp kết quả
    record = merge_results(symbol, vsd_data, hnx_data, hose_data)

    return record

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_all.py <symbol> [symbol2 ...]")
        sys.exit(1)

    symbols = sys.argv[1:]
    all_records = []

    for symbol in symbols:
        record = fetch_symbol(symbol)
        all_records.append(record)

    # Output JSON
    output = {
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'total_symbols': len(symbols),
        'records': all_records
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
