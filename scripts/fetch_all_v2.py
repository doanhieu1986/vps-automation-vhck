#!/usr/bin/env python3
"""
Enhanced fetch script with proper cascade logic:
VSD → HNX → HOSE (fallback)
Extracts detailed information as per workflow.md requirements
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import time
from datetime import datetime
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

class BondInfoFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.vsd_base = "https://www.vsd.vn"
        self.hnx_base = "https://www.hnx.vn"
        self.hose_base = "https://www.hsx.vn"

    def fetch_from_vsd(self, symbol):
        """
        Fetch from VSD - tin tức thị trường cơ sở
        https://www.vsd.vn/vi/tin-thi-truong-co-so
        """
        logger.info(f"🔍 VSD: Tìm kiếm {symbol}...")
        try:
            # VSD news page
            url = f"{self.vsd_base}/vi/tin-thi-truong-co-so"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                return {'status': 'error', 'code': response.status_code}

            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()

            # Check if symbol found in page
            if symbol.lower() not in text_content:
                logger.info(f"  ⚠ Không tìm thấy {symbol} trên VSD")
                return {'status': 'not_found'}

            # Extract news/announcement links mentioning the symbol
            announcements = []
            links = soup.find_all('a', href=True)

            for link in links:
                link_text = link.get_text(strip=True).lower()
                if symbol.lower() in link_text or symbol.lower() in link['href'].lower():
                    announcements.append({
                        'title': link.get_text(strip=True),
                        'url': link['href'] if link['href'].startswith('http') else f"{self.vsd_base}{link['href']}",
                        'source': 'VSD'
                    })

            if announcements:
                return {
                    'status': 'success',
                    'symbol': symbol,
                    'announcements': announcements[:5],  # Lấy tối đa 5
                    'url': url,
                    'data': {
                        'tên_tổ_chức_đăng_ký': 'Cần fetch từ chi tiết',
                        'tên_chứng_khoán': 'Cần fetch từ chi tiết',
                        'mã_isin': 'Cần fetch từ chi tiết',
                        'nơi_giao_dịch': 'VSD',
                        'quyền_nhận_lãi': 'Cần fetch từ chi tiết',
                        'quyền_trả_gốc': 'Cần fetch từ chi tiết',
                        'source_page': url
                    }
                }

            return {'status': 'partial', 'message': 'Tìm thấy nhưng không có announcement links'}

        except Exception as e:
            logger.error(f"  ✗ VSD Error: {str(e)[:50]}")
            return {'status': 'error', 'message': str(e)}

    def fetch_from_hnx(self, symbol):
        """
        Fetch from HNX
        - Trái phiếu → Niêm yết → Danh sách trái phiếu
        https://www.hnx.vn/vi-vn/trai-phieu
        """
        logger.info(f"🔍 HNX: Tìm kiếm {symbol}...")
        try:
            # HNX bonds listing page
            url = f"{self.hnx_base}/vi-vn/trai-phieu"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                logger.info(f"  ⚠ HNX không response (code: {response.status_code})")
                return {'status': 'error', 'code': response.status_code}

            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text()

            # Search for symbol in page
            if symbol.lower() not in text_content.lower():
                logger.info(f"  ⚠ Không tìm thấy {symbol} trên HNX")
                return {'status': 'not_found'}

            # Find bond details
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_text = ' '.join([cell.get_text(strip=True) for cell in cells])

                    if symbol.upper() in row_text.upper():
                        # Found the bond row
                        details = {
                            'symbol': symbol,
                            'found': True,
                            'nơi_giao_dịch': 'HNX',
                            'source': 'HNX',
                            'url': url
                        }

                        # Extract cells
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        if len(cell_texts) >= 2:
                            details['tên_chứng_khoán'] = cell_texts[1] if len(cell_texts) > 1 else 'N/A'

                        logger.info(f"  ✓ Tìm thấy {symbol} trên HNX")
                        return {
                            'status': 'success',
                            'symbol': symbol,
                            'data': details
                        }

            return {'status': 'partial', 'found_but_incomplete': True}

        except Exception as e:
            logger.error(f"  ✗ HNX Error: {str(e)[:50]}")
            return {'status': 'error', 'message': str(e)}

    def fetch_from_hose(self, symbol):
        """
        Fetch from HOSE
        - Niêm yết → CW → Tìm mã
        https://www.hsx.vn/vi/tra-cuu/chung-chi
        """
        logger.info(f"🔍 HOSE: Tìm kiếm {symbol}...")
        try:
            # HOSE CW listing page
            url = f"{self.hose_base}/vi/tra-cuu/chung-chi"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                logger.info(f"  ⚠ HOSE không response (code: {response.status_code})")
                return {'status': 'error', 'code': response.status_code}

            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text()

            # Search for symbol
            if symbol.lower() not in text_content.lower():
                logger.info(f"  ⚠ Không tìm thấy {symbol} trên HOSE")
                return {'status': 'not_found'}

            # Find details
            details = {
                'symbol': symbol,
                'found': True,
                'nơi_giao_dịch': 'HOSE',
                'source': 'HOSE',
                'url': url
            }

            logger.info(f"  ✓ Tìm thấy {symbol} trên HOSE")
            return {
                'status': 'success',
                'symbol': symbol,
                'data': details
            }

        except Exception as e:
            logger.error(f"  ✗ HOSE Error: {str(e)[:50]}")
            return {'status': 'error', 'message': str(e)}

    def fetch_with_cascade(self, symbol):
        """
        Cascade logic: VSD → HNX → HOSE
        """
        logger.info(f"\n📌 Xử lý: {symbol}")

        # Try VSD first
        vsd_result = self.fetch_from_vsd(symbol)
        if vsd_result.get('status') == 'success':
            return {
                'symbol': symbol,
                'primary_source': 'VSD',
                'vsd': vsd_result,
                'hnx': None,
                'hose': None,
                'status': 'found_vsd'
            }

        # If not in VSD, try HNX
        logger.info(f"  → Không tìm thấy trên VSD, chuyển sang HNX")
        hnx_result = self.fetch_from_hnx(symbol)
        if hnx_result.get('status') == 'success':
            return {
                'symbol': symbol,
                'primary_source': 'HNX',
                'vsd': vsd_result,
                'hnx': hnx_result,
                'hose': None,
                'status': 'found_hnx'
            }

        # If not in HNX, try HOSE
        logger.info(f"  → Không tìm thấy trên HNX, chuyển sang HOSE")
        hose_result = self.fetch_from_hose(symbol)
        if hose_result.get('status') == 'success':
            return {
                'symbol': symbol,
                'primary_source': 'HOSE',
                'vsd': vsd_result,
                'hnx': hnx_result,
                'hose': hose_result,
                'status': 'found_hose'
            }

        # Not found anywhere
        logger.info(f"  ✗ Không tìm thấy {symbol} trên bất kỳ nguồn nào")
        return {
            'symbol': symbol,
            'primary_source': None,
            'vsd': vsd_result,
            'hnx': hnx_result,
            'hose': hose_result,
            'status': 'not_found'
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_all_v2.py <symbol> [symbol2 ...]")
        sys.exit(1)

    fetcher = BondInfoFetcher()
    results = []

    symbols = sys.argv[1:]
    logger.info(f"🚀 Bắt đầu fetch {len(symbols)} mã chứng khoán")
    logger.info("=" * 60)

    for symbol in symbols:
        result = fetcher.fetch_with_cascade(symbol)
        results.append(result)
        time.sleep(1)  # Rate limiting

    logger.info("\n" + "=" * 60)
    logger.info(f"✅ Hoàn thành. Tìm thấy: {sum(1 for r in results if r['status'] != 'not_found')}/{len(results)}")
    logger.info("=" * 60 + "\n")

    # Output JSON to stdout
    output = {
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'total_symbols': len(symbols),
        'found_count': sum(1 for r in results if r['status'] != 'not_found'),
        'records': results
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
