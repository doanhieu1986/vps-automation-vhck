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
import os
from datetime import datetime, timedelta
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# CONFIGURATION - Thay đổi giá trị này để điều chỉnh số ngày cần lấy
# ============================================================================
KEEP_DAYS = 1  # Số ngày gần nhất cần lấy (1=ngày mới nhất, 2=2 ngày, 3=3 ngày, ...)
# ============================================================================

logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

class VSDFetcher:
    def __init__(self):
        """
        Khởi tạo VSDFetcher

        Số ngày cần lấy được điều chỉnh bằng hằng số KEEP_DAYS ở đầu file
        """
        self.base_url = "https://www.vsd.vn"
        self.news_url = "https://www.vsd.vn/vi/tin-thi-truong-co-so"
        self.session = requests.Session()
        self.vptoken = None  # Token để AJAX POST phân trang
        self.keep_days = KEEP_DAYS  # Số ngày gần nhất cần lấy (từ hằng số KEEP_DAYS)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9',
            'Connection': 'keep-alive',
        }

    def parse_date(self, date_string):
        """Parse ngày từ string 'dd/mm/yyyy' thành datetime.date"""
        try:
            return datetime.strptime(date_string, '%d/%m/%Y').date()
        except:
            return None

    def get_vptoken(self):
        """Extract VPToken từ <meta name='__VPToken'> trên trang list"""
        try:
            response = self.session.get(self.news_url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            meta = soup.find('meta', {'name': '__VPToken'})
            if meta and meta.get('content'):
                self.vptoken = meta.get('content')
                logger.info(f"✓ Got VPToken: {self.vptoken[:20]}...")
                return self.vptoken
            else:
                logger.error("✗ VPToken not found in meta tag")
                return None
        except Exception as e:
            logger.error(f"✗ Error getting VPToken: {str(e)}")
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

        Trả về tuple (info_dict, extracted_code, actual_update_date) nếu tìm được mã từ chi tiết
        actual_update_date là ngày "Cập nhật ngày" từ bài viết (chính xác hơn ngày listing)
        """
        try:
            # Retry logic để đảm bảo page load đầy đủ
            max_retries = 3
            response = None
            for attempt in range(max_retries):
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.encoding = 'utf-8'

                if response.status_code == 200:
                    break

                if attempt < max_retries - 1:
                    time.sleep(0.2)  # Wait before retry

            if response is None or response.status_code != 200:
                return None, None, None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text content
            main = soup.find('main') or soup.find('article')
            if not main:
                return None, None, None

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

            # Extract "Cập nhật ngày" từ bài viết (thay vì lấy từ listing page)
            actual_update_date = None
            # Pattern: "Cập nhật ngày DD/MM/YYYY" hoặc "Cập nhật ngày DD/MM/YYYY - HH:MM:SS"
            update_match = re.search(r'Cập nhật ngày\s+(\d{1,2}/\d{1,2}/\d{4})', text_content)
            if update_match:
                date_str = update_match.group(1)
                actual_update_date = self.parse_date(date_str)
                logger.debug(f"  ✓ Found actual update date: {date_str}")

            return info, extracted_code, actual_update_date

        except Exception as e:
            logger.debug(f"  ! Error extracting detail: {str(e)[:50]}")
            return None, None, None

    def fetch_latest_news(self):
        """
        Crawl tất cả trang tin tức VSD từ ngày gần nhất:
        1. Lặp qua các trang (page=1, 2, 3, ...)
        2. Extract danh sách tin từ mỗi trang
        3. Dừng khi ngày tin giảm xuống (đã hết tin từ ngày gần nhất)
        4. Mở từng tin để lấy chi tiết
        5. Return danh sách mã + chi tiết
        """
        try:
            logger.info(f"🔍 VSD: Crawling tin tức thị trường cơ sở (multiple pages)...")
            all_news = []
            page = 1
            latest_date_found = None
            max_pages = 25  # Tối đa 10 trang, sẽ dừng sớm khi gặp tin cũ hơn 2 ngày

            # Calculate cutoff date: today - 1 days
            today = datetime.now().date()
            cutoff_date = today - timedelta(days=2)
            logger.info(f"  📅 Cutoff date (> 2 days old): {cutoff_date}")

            while page <= max_pages:
                logger.info(f"  📄 Crawling page {page}...")

                try:
                    # Get VPToken từ trang đầu tiên nếu chưa có
                    if page == 1:
                        vptoken = self.get_vptoken()
                        if not vptoken:
                            logger.error("  ✗ Cannot get VPToken, stopping")
                            break

                    # Use AJAX POST with VPToken (correct method for VSD)
                    ajax_headers = {
                        'User-Agent': 'Mozilla/5.0',
                        'Content-Type': 'application/json;charset=utf-8',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Referer': self.news_url,
                        'Origin': self.base_url,
                        '__VPToken': vptoken
                    }
                    payload = {'SearchKey': 'TCPH', 'CurrentPage': page}

                    response = self.session.post(self.news_url, headers=ajax_headers, json=payload, timeout=10)
                    response.encoding = 'utf-8'

                    if response.status_code != 200:
                        logger.info(f"  ⚠ Page {page} failed (HTTP {response.status_code})")
                        break

                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Tìm tất cả <li> items trên trang này
                    news_items = soup.find_all('li')
                    page_news = []

                    # Extract danh sách tin từ trang hiện tại
                    logger.info(f"    📰 Total items on page: {len(news_items)}")
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

                        page_news.append({
                            'code': code,
                            'title': title,
                            'url': url,
                            'date': date_text,
                            'date_obj': date_obj,
                            'source': 'VSD'
                        })

                    if not page_news:
                        logger.info(f"  ⚠ Page {page} không có tin nào")
                        break

                    # Log codes của trang này để check xem khác nhau không
                    codes_on_page = [n['code'] for n in page_news]
                    logger.info(f"    Codes: {codes_on_page[:5]}... ({len(codes_on_page)} items)")

                    # Xác định ngày gần nhất và cũ nhất trên trang này
                    page_dates = [n['date_obj'] for n in page_news if n['date_obj']]
                    if not page_dates:
                        logger.warning(f"    ⚠ No valid dates found on page {page}, skipping")
                        page += 1
                        continue

                    page_latest_date = max(page_dates)
                    page_oldest_date = min(page_dates)

                    # DEBUG: Log all unique dates on this page, sorted descending
                    unique_dates = sorted(set(page_dates), reverse=True)
                    logger.info(f"    📅 Unique dates on page {page}: {unique_dates}")

                    # Lần đầu tiên tìm thấy trang, set latest_date_found
                    if latest_date_found is None:
                        latest_date_found = page_latest_date
                        logger.info(f"  ✓ Ngày gần nhất tìm thấy: {latest_date_found}")

                    # DEBUG: Log thông tin ngày trên trang này với comparison
                    logger.info(f"    📅 Page {page}: oldest={page_oldest_date}, latest={page_latest_date}, cutoff={cutoff_date}")
                    logger.info(f"    📊 Comparison: {page_oldest_date} <= {cutoff_date}? {page_oldest_date <= cutoff_date}")

                    # Thêm tin từ trang này vào danh sách trước
                    all_news.extend(page_news)
                    logger.info(f"    ✓ Thêm {len(page_news)} tin từ {page_oldest_date} đến {page_latest_date}")

                    # KIỂM TRA: Nếu trang này có tin cách đây >= 2 ngày (oldest_date <= cutoff_date), dừng crawl
                    if page_oldest_date <= cutoff_date:
                        logger.info(f"  ⏹ Trang {page} có tin từ {page_oldest_date} <= {cutoff_date} (cách đây >= 2 ngày), DỪNG crawl")
                        break

                    # Rate limiting: no delay between page requests (VSD allows fast crawl)
                    # time.sleep(0.1)
                    page += 1

                except requests.exceptions.Timeout:
                    logger.error(f"  ✗ Page {page}: Request timeout")
                    break
                except Exception as e:
                    logger.error(f"  ✗ Page {page}: {str(e)[:50]}")
                    break

            if not all_news:
                logger.info(f"  ⚠ Không tìm thấy tin nào trên VSD")
                return {
                    'status': 'not_found',
                    'message': 'Không tìm thấy tin trên VSD'
                }

            # Lọc tin để chỉ giữ N ngày gần nhất (self.keep_days)
            # Công thức: min_keep_date = latest_date_found - (keep_days - 1) ngày
            min_keep_date = latest_date_found - timedelta(days=self.keep_days - 1)
            filtered_news = [n for n in all_news if n['date_obj'] and n['date_obj'] >= min_keep_date]

            logger.info(f"  ✓ Tìm thấy {len(filtered_news)} tin từ {min_keep_date} đến {latest_date_found} (crawled {page-1} pages, keeping {self.keep_days} day(s))")
            logger.info(f"  🔗 Extracting details từ tất cả {len(filtered_news)} records (concurrent, with retry)...")

            # Extract chi tiết từ tin tức - concurrent với retry để ensure page load
            result_data = []

            def extract_with_retry(news):
                """Extract chi tiết với retry logic"""
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        detail, extracted_code, actual_update_date = self.extract_detail_from_article(news['url'])
                        final_code = extracted_code if extracted_code else news['code']

                        # Ưu tiên dùng "Cập nhật ngày" từ bài viết, nếu không có thì dùng ngày listing
                        final_date = actual_update_date if actual_update_date else news['date_obj']
                        final_date_str = final_date.strftime('%d/%m/%Y') if final_date else news['date']

                        result_item = {
                            'code': final_code,
                            'title': news['title'],
                            'url': news['url'],
                            'date': final_date_str,
                            'collected_date': final_date_str,
                            'source': 'VSD'
                        }

                        if detail:
                            result_item.update(detail)

                        return result_item
                    except Exception as e:
                        if attempt < max_retries - 1:
                            time.sleep(0.3)
                        else:
                            logger.error(f"Failed {news['code']}: {str(e)[:30]}")
                            # Return basic item on final failure (dùng ngày listing nếu không extract được)
                            return {
                                'code': news['code'],
                                'title': news['title'],
                                'url': news['url'],
                                'date': news['date'],
                                'collected_date': news['date'],
                                'source': 'VSD'
                            }

            # Extract từ tất cả records (concurrent)
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for idx, news in enumerate(filtered_news):
                    future = executor.submit(extract_with_retry, news)
                    futures.append((future, news['code']))
                    if idx % 10 == 0:  # Minimal delay every 10 items
                        time.sleep(0.05)

                for future, code in futures:
                    try:
                        result_item = future.result()
                        result_data.append(result_item)
                        if len(result_data) % 100 == 0:
                            logger.info(f"    Extracted {len(result_data)}/{len(filtered_news)}")
                    except Exception as e:
                        logger.error(f"Future error {code}: {str(e)[:30]}")

            logger.info(f"  ✓ Hoàn thành extract chi tiết từ {len(result_data)} tin")

            # Merge với records cũ để tránh duplicate
            merged_data = result_data  # Mặc định chỉ có data mới
            total_count = len(result_data)

            # Nếu file vsd_records.json tồn tại, load và merge
            json_file_path = '/app/vps-automation-vhck/data/vsd_records.json'
            if os.path.exists(json_file_path):
                try:
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)

                    existing_records = existing_data.get('records', [])
                    logger.info(f"  📚 Found {len(existing_records)} existing records, merging...")

                    # Create map of new codes để tránh duplicate
                    new_codes = {r['code']: r for r in result_data}

                    # Thêm existing records nếu không trùng với code mới
                    for existing_record in existing_records:
                        if existing_record.get('code') not in new_codes:
                            merged_data.append(existing_record)
                        else:
                            # Nếu code trùng, replace với version mới
                            logger.debug(f"  ! Updating {existing_record.get('code')} with new data")

                    logger.info(f"  ✓ Merged: {len(result_data)} new + {len(existing_records)} existing = {len(merged_data)} total")
                    total_count = len(merged_data)

                except Exception as e:
                    logger.error(f"  ✗ Error merging records: {str(e)[:50]}")
                    # Fallback: use only new data nếu merge failed
                    merged_data = result_data

            return {
                'status': 'success',
                'date': str(latest_date_found),
                'data': merged_data,
                'count': total_count,
                'url': self.news_url,
                'pages_crawled': page - 1,
                'fetched_at': datetime.now().isoformat(),
                'merge_info': f'{len(result_data)} new records merged with existing'
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
    logger.info(f"Starting VSD fetch with KEEP_DAYS={KEEP_DAYS}")
    result = fetcher.fetch_latest_news()

    # Output JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()