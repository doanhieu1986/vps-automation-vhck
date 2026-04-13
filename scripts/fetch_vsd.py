#!/usr/bin/env python3
"""
Fetch bond information from VSD (Vietnamese Securities Depository)
URL: https://www.vsd.vn/vi/tin-thi-truong-co-so

Crawl trang tin tức thị trường cơ sở:
1. Lấy danh sách tin có mã CK từ ngày gần nhất
2. Mở từng tin tức để extract chi tiết thông tin
3. Return danh sách mã + chi tiết thông tin quyền
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import time
from datetime import datetime, timedelta
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

class VSDFetcher:
    def __init__(self):
        self.base_url = "https://www.vsd.vn"
        self.news_url = "https://www.vsd.vn/vi/tin-thi-truong-co-so"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def parse_date(self, date_string):
        """Parse ngày từ string 'dd/mm/yyyy' thành datetime.date"""
        try:
            return datetime.strptime(date_string, '%d/%m/%Y').date()
        except:
            return None

    def extract_field_from_text(self, text, field_label, max_length=500):
        """
        Extract field value từ text content dựa trên label
        Hỗ trợ multi-line content và bullet points

        Ví dụ:
        "Địa điểm thực hiện: ..." => lấy text sau "Địa điểm thực hiện:"
        "Địa điểm thực hiện:\n+ Đối với..." => lấy tất cả bullet points
        """
        pattern = f"{field_label}[:\\s]+([^\\n]+(?:\\n\\s*[+\\-•]\\s*[^\\n]+)*)"
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)

        if match:
            extracted = match.group(1).strip()
            # Nếu quá dài, chỉ lấy phần đầu
            if len(extracted) > max_length:
                extracted = extracted[:max_length] + "..."
            return extracted if extracted else None
        return None

    def extract_detail_from_article(self, url):
        """
        Mở URL tin tức và extract chi tiết thông tin từ HTML structure:
        <div class="col-md-4 item-info">Label:</div>
        <div class="col-md-8 item-info item-info-main">Value</div>

        Trả về tuple (info_dict, extracted_code) nếu tìm được mã từ chi tiết
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                return None, None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text content
            main = soup.find('main') or soup.find('article')
            if not main:
                return None, None

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

            extracted_code = None

            # Find all label-value pairs trong HTML structure chuẩn
            label_divs = soup.find_all('div', class_='col-md-4')

            for label_div in label_divs:
                # Get label text
                label = label_div.get_text(strip=True).lower()

                # Get value (next sibling with col-md-8)
                value_div = label_div.find_next('div', class_='col-md-8')
                if not value_div:
                    continue

                value = value_div.get_text(strip=True)

                # Map labels to info keys
                if 'tên tổ chức đăng ký' in label:
                    info['tên_tổ_chức_đăng_ký'] = value
                elif 'tên chứng khoán' in label:
                    info['tên_chứng_khoán'] = value
                elif 'mã chứng khoán' in label or 'mã ck' in label:
                    # Nếu có trường "Mã chứng khoán", lấy mã từ đây
                    extracted_code = value
                elif 'mã isin' in label:
                    info['mã_isin'] = value
                elif 'nơi giao dịch' in label:
                    info['nơi_giao_dịch'] = value
                elif 'loại chứng khoán' in label:
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

            # Nếu không tìm được từ HTML structure, thử lấy từ text content
            # Vì thông tin này có thể ở dạng bullet points hoặc multi-line
            if not info['tỷ_lệ_thực_hiện']:
                info['tỷ_lệ_thực_hiện'] = self.extract_field_from_text(
                    text_content,
                    'Tỷ lệ thực hiện',
                    max_length=500
                )

            if not info['thời_gian_thực_hiện']:
                info['thời_gian_thực_hiện'] = self.extract_field_from_text(
                    text_content,
                    'Thời gian thực hiện',
                    max_length=300
                )

            if not info['địa_điểm_thực_hiện']:
                info['địa_điểm_thực_hiện'] = self.extract_field_from_text(
                    text_content,
                    'Địa điểm thực hiện',
                    max_length=500
                )

            if not info['lý_do_mục_đích']:
                info['lý_do_mục_đích'] = self.extract_field_from_text(
                    text_content,
                    'Lý do|Mục đích',
                    max_length=300
                )

            # Find quyền from text content
            text_lower = text_content.lower()

            if any(word in text_lower for word in ['nhận lãi', 'lãi định kỳ', 'thanh toán lãi']):
                info['quyền_nhận_lãi'] = 'Có'

            if any(word in text_lower for word in ['trả gốc', 'đáo hạn', 'thanh toán gốc']):
                info['quyền_trả_gốc'] = 'Có'

            if any(word in text_lower for word in ['chuyển đổi', 'hoán đổi']):
                info['quyền_chuyển_đổi'] = 'Có'

            return info, extracted_code

        except Exception as e:
            logger.debug(f"  ! Error extracting detail: {str(e)[:50]}")
            return None, None

    def fetch_latest_news(self):
        """
        Crawl trang tin tức VSD:
        1. Extract danh sách tin từ ngày gần nhất
        2. Mở từng tin để lấy chi tiết
        3. Return danh sách mã + chi tiết
        """
        try:
            logger.info(f"🔍 VSD: Crawling tin tức thị trường cơ sở...")
            response = requests.get(self.news_url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                return {
                    'status': 'error',
                    'code': response.status_code,
                    'message': f'HTTP {response.status_code}'
                }

            soup = BeautifulSoup(response.content, 'html.parser')

            # Tìm tất cả <li> items
            news_items = soup.find_all('li')
            all_news = []

            # Extract danh sách tin từ trang chính
            for item in news_items:
                h3 = item.find('h3')
                if not h3:
                    continue

                link = h3.find('a')
                if not link:
                    continue

                title = link.get_text(strip=True)
                url = link.get('href', '')

                if not title or not url:
                    continue

                # Chỉ lấy tin có mã CK - pattern: CODE: (where CODE is 2-10 chars)
                if not re.search(r'[A-Z0-9]{2,10}:', title):
                    continue

                # Extract mã CK from title (allow 2-10 character codes)
                match = re.search(r'([A-Z0-9]{2,10}):', title)
                if not match:
                    continue

                code = match.group(1)

                # Normalize URL
                if not url.startswith('http'):
                    url = self.base_url + url

                # Extract ngày
                time_div = item.find('div', class_='time-news')
                date_text = None
                date_obj = None

                if time_div:
                    time_text = time_div.get_text(strip=True)
                    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', time_text)
                    if date_match:
                        date_text = date_match.group(1)
                        date_obj = self.parse_date(date_text)

                all_news.append({
                    'code': code,
                    'title': title,
                    'url': url,
                    'date': date_text,
                    'date_obj': date_obj,
                    'source': 'VSD'
                })

            if not all_news:
                logger.info(f"  ⚠ Không tìm thấy tin nào trên VSD")
                return {
                    'status': 'not_found',
                    'message': 'Không tìm thấy tin trên VSD'
                }

            # Filter chỉ tin từ ngày gần nhất
            latest_date = max([n['date_obj'] for n in all_news if n['date_obj']])
            filtered_news = [n for n in all_news if n['date_obj'] == latest_date]

            logger.info(f"  ✓ Tìm thấy {len(filtered_news)} tin từ ngày {latest_date}")
            logger.info(f"  🔗 Đang mở từng tin tức để extract chi tiết...")

            # Mở từng tin tức để lấy chi tiết
            result_data = []
            for idx, news in enumerate(filtered_news, 1):
                logger.info(f"    [{idx}/{len(filtered_news)}] {news['code']}: {news['title'][:50]}")

                # Extract chi tiết từ tin tức
                detail, extracted_code = self.extract_detail_from_article(news['url'])

                # Ưu tiên mã được lấy từ chi tiết nếu có
                final_code = extracted_code if extracted_code else news['code']

                result_item = {
                    'code': final_code,
                    'title': news['title'],
                    'url': news['url'],
                    'date': news['date'],
                    'source': 'VSD'
                }

                if detail:
                    result_item.update(detail)

                result_data.append(result_item)

                # Rate limiting: sleep 2 seconds between requests để tránh lỗi
                time.sleep(2)

            logger.info(f"  ✓ Hoàn thành extract chi tiết từ {len(result_data)} tin")

            return {
                'status': 'success',
                'date': str(latest_date),
                'data': result_data,
                'count': len(result_data),
                'url': self.news_url,
                'fetched_at': datetime.now().isoformat()
            }

        except requests.exceptions.Timeout:
            logger.error("  ✗ Request timeout")
            return {
                'status': 'error',
                'message': 'Request timeout'
            }
        except Exception as e:
            logger.error(f"  ✗ VSD Error: {str(e)[:100]}")
            return {
                'status': 'error',
                'message': str(e)
            }

def main():
    fetcher = VSDFetcher()
    result = fetcher.fetch_latest_news()

    # Output JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()