#!/usr/bin/env python3
"""
Fetch bond/warrant information from HOSE (Ho Chi Minh Stock Exchange)
URL: https://www.hsx.vn/vi/tra-cuu/chung-chi

Crawl danh sách chứng chỉ/trái phiếu:
1. Lấy danh sách chứng chỉ từ ngày gần nhất
2. Mở từng chứng chỉ để extract chi tiết thông tin
3. Return danh sách mã + chi tiết thông tin quyền
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import time
from datetime import datetime
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

class HOSEFetcher:
    def __init__(self):
        self.base_url = "https://www.hsx.vn"
        self.cw_url = "https://www.hsx.vn/vi/tra-cuu/chung-chi"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def parse_date(self, date_string):
        """Parse ngày từ string 'dd/mm/yyyy' thành datetime.date"""
        try:
            return datetime.strptime(date_string, '%d/%m/%Y').date()
        except:
            return None

    def extract_detail_from_article(self, url):
        """
        Mở URL chứng chỉ và extract chi tiết thông tin từ HTML structure
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text content
            main = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|body'))
            if not main:
                return None

            text_content = main.get_text()

            # Initialize info với tất cả fields cần thiết
            info = {
                'tên_tổ_chức_đăng_ký': None,
                'tên_chứng_khoán': None,
                'mã_isin': None,
                'nơi_giao_dịch': None,
                'loại_chứng_khoán': None,
                'ngày_đăng_ký_cuối': None,
                'lý_do_mục_đích': None,
                'tỷ_lệ_thực_hiện': None,
                'thời_gian_thực_hiện': None,
                'địa_điểm_thực_hiện': None,
                'quyền_nhận_lãi': None,
                'quyền_trả_gốc': None,
                'quyền_chuyển_đổi': None
            }

            # Find all label-value pairs
            label_divs = soup.find_all('div', class_=re.compile('col-md-4|label|info'))

            for label_div in label_divs:
                # Get label text
                label = label_div.get_text(strip=True).lower()

                # Get value (next sibling with col-md-8 or similar)
                value_div = label_div.find_next('div', class_=re.compile('col-md-8|value|info-main'))
                if not value_div:
                    continue

                value = value_div.get_text(strip=True)

                # Map labels to info keys
                if 'tên tổ chức đăng ký' in label or 'tên tổ chức' in label:
                    info['tên_tổ_chức_đăng_ký'] = value
                elif 'tên chứng khoán' in label or 'tên chứng chỉ' in label:
                    info['tên_chứng_khoán'] = value
                elif 'mã isin' in label:
                    info['mã_isin'] = value
                elif 'nơi giao dịch' in label or 'sở giao dịch' in label:
                    info['nơi_giao_dịch'] = value
                elif 'loại chứng khoán' in label or 'loại chứng chỉ' in label:
                    info['loại_chứng_khoán'] = value
                elif 'ngày đăng ký' in label and 'cuối' in label:
                    info['ngày_đăng_ký_cuối'] = value
                elif 'lý do' in label or 'mục đích' in label:
                    info['lý_do_mục_đích'] = value
                elif 'tỷ lệ' in label and 'thực hiện' in label:
                    info['tỷ_lệ_thực_hiện'] = value
                elif 'thời gian' in label and 'thực hiện' in label:
                    info['thời_gian_thực_hiện'] = value
                elif 'địa điểm' in label and 'thực hiện' in label:
                    info['địa_điểm_thực_hiện'] = value

            # Find quyền from text content
            text_lower = text_content.lower()

            if any(word in text_lower for word in ['nhận lãi', 'lãi định kỳ', 'thanh toán lãi']):
                info['quyền_nhận_lãi'] = 'Có'

            if any(word in text_lower for word in ['trả gốc', 'đáo hạn', 'thanh toán gốc']):
                info['quyền_trả_gốc'] = 'Có'

            if any(word in text_lower for word in ['chuyển đổi', 'hoán đổi']):
                info['quyền_chuyển_đổi'] = 'Có'

            return info

        except Exception as e:
            logger.debug(f"  ! Error extracting detail: {str(e)[:50]}")
            return None

    def fetch_latest_cw(self):
        """
        Crawl trang danh sách chứng chỉ HOSE:
        1. Extract danh sách chứng chỉ từ bảng
        2. Mở từng chứng chỉ để lấy chi tiết
        3. Return danh sách mã + chi tiết
        """
        try:
            logger.info(f"🔍 HOSE: Crawling danh sách chứng chỉ...")
            response = requests.get(self.cw_url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                return {
                    'status': 'error',
                    'code': response.status_code,
                    'message': f'HTTP {response.status_code}'
                }

            soup = BeautifulSoup(response.content, 'html.parser')

            # Tìm tất cả <tr> trong tables
            all_cw = []
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Bỏ header
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        symbol_text = cols[0].get_text(strip=True)

                        # Chỉ lấy những mã hợp lệ (không để trống)
                        if not symbol_text or len(symbol_text) < 2:
                            continue

                        link = cols[0].find('a')
                        url = None
                        if link and link.get('href'):
                            url = link.get('href')
                            if not url.startswith('http'):
                                url = self.base_url + url

                        all_cw.append({
                            'code': symbol_text,
                            'title': cols[1].get_text(strip=True) if len(cols) > 1 else symbol_text,
                            'url': url,
                            'source': 'HOSE'
                        })

            if not all_cw:
                logger.info(f"  ⚠ Không tìm thấy chứng chỉ nào trên HOSE")
                return {
                    'status': 'not_found',
                    'message': 'Không tìm thấy chứng chỉ trên HOSE'
                }

            logger.info(f"  ✓ Tìm thấy {len(all_cw)} chứng chỉ")
            logger.info(f"  🔗 Đang mở từng chứng chỉ để extract chi tiết...")

            # Mở từng chứng chỉ để lấy chi tiết
            result_data = []
            for idx, cw in enumerate(all_cw[:20], 1):  # Lấy tối đa 20
                logger.info(f"    [{idx}/{min(20, len(all_cw))}] {cw['code']}: {cw['title'][:50]}")

                # Extract chi tiết từ chứng chỉ
                detail = None
                if cw['url']:
                    detail = self.extract_detail_from_article(cw['url'])

                result_item = {
                    'code': cw['code'],
                    'title': cw['title'],
                    'url': cw['url'],
                    'source': 'HOSE'
                }

                if detail:
                    result_item.update(detail)

                result_data.append(result_item)

                # Rate limiting: sleep 2 seconds between requests để tránh lỗi
                time.sleep(2)

            logger.info(f"  ✓ Hoàn thành extract chi tiết từ {len(result_data)} chứng chỉ")

            return {
                'status': 'success',
                'data': result_data,
                'count': len(result_data),
                'url': self.cw_url,
                'fetched_at': datetime.now().isoformat()
            }

        except requests.exceptions.Timeout:
            logger.error("  ✗ Request timeout")
            return {
                'status': 'error',
                'message': 'Request timeout'
            }
        except Exception as e:
            logger.error(f"  ✗ HOSE Error: {str(e)[:100]}")
            return {
                'status': 'error',
                'message': str(e)
            }

def main():
    fetcher = HOSEFetcher()
    result = fetcher.fetch_latest_cw()

    # Output JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
