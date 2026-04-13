#!/usr/bin/env python3
"""
Fetch bond information from HNX (Hanoi Stock Exchange)
URL: https://www.hnx.vn/tin-trai-phieu-hnx.html

Quy trình (dùng Selenium):
1. Đọc danh sách symbol từ symbol.md
2. Mở trang tin tức HNX
3. Nhập symbol vào field "Đối tượng liên quan"
4. Click tìm kiếm
5. Mở tin mới nhất
6. Extract chi tiết thông tin
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import time
from datetime import datetime
import re
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

class HNXFetcher:
    def __init__(self):
        self.base_url = "https://www.hnx.vn"
        self.news_url = "https://www.hnx.vn/tin-trai-phieu-hnx.html"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.driver = None

    def init_driver(self):
        """Khởi tạo Selenium webdriver (Chrome headless)"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

            self.driver = webdriver.Chrome(options=options)
            logger.info("✓ Selenium driver initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize driver: {e}")
            raise

    def close_driver(self):
        """Đóng webdriver"""
        if self.driver:
            self.driver.quit()

    def extract_field_from_text(self, text, field_label, max_length=500):
        """
        Extract field value từ text content dựa trên label
        Hỗ trợ multi-line content và bullet points
        """
        pattern = f"{field_label}[:\\s]+([^\\n]+(?:\\n\\s*[+\\-•]\\s*[^\\n]+)*)"
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)

        if match:
            extracted = match.group(1).strip()
            if len(extracted) > max_length:
                extracted = extracted[:max_length] + "..."
            return extracted if extracted else None
        return None

    def extract_detail_from_article_html(self, html_content):
        """
        Extract chi tiết thông tin từ HTML content (popup modal)
        Trả về tuple (info_dict, extracted_code)
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()

            # Initialize info
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

            # Cách 1: Find all label-value pairs trong HTML structure
            label_divs = soup.find_all('div', class_=re.compile('col-md-4|label|info'))

            for label_div in label_divs:
                label = label_div.get_text(strip=True).lower()
                value_div = label_div.find_next('div', class_=re.compile('col-md-8|value|info-main'))

                if not value_div:
                    continue

                value = value_div.get_text(strip=True)

                # Map labels
                if 'tên tổ chức' in label:
                    info['tên_tổ_chức_đăng_ký'] = value
                elif 'tên chứng khoán' in label or 'tên trái phiếu' in label:
                    info['tên_chứng_khoán'] = value
                elif 'mã chứng khoán' in label or 'mã ck' in label:
                    extracted_code = value
                elif 'mã isin' in label:
                    info['mã_isin'] = value
                elif 'nơi giao dịch' in label or 'sở giao dịch' in label:
                    info['nơi_giao_dịch'] = value
                elif 'loại chứng khoán' in label or 'loại trái phiếu' in label:
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

            # Cách 2: Fallback - tìm text content từ paragraph hoặc table cells
            if not any([info.get(k) for k in list(info.keys())[:5]]):  # Nếu chưa tìm thấy thông tin nào
                # Thử parse từ table rows hoặc list items
                rows = soup.find_all(['tr', 'li', 'p'])
                for row in rows:
                    row_text = row.get_text(strip=True).lower()
                    row_value = row.get_text(strip=True)

                    if 'tên tổ chức' in row_text and not info['tên_tổ_chức_đăng_ký']:
                        info['tên_tổ_chức_đăng_ký'] = row_value
                    elif 'tên chứng khoán' in row_text and not info['tên_chứng_khoán']:
                        info['tên_chứng_khoán'] = row_value
                    elif 'mã chứng khoán' in row_text and not extracted_code:
                        match = re.search(r'\b[A-Z0-9]{6,10}\b', row_value)
                        if match:
                            extracted_code = match.group(0)

            # Cách 3: Fallback extraction từ text content
            if not info['tỷ_lệ_thực_hiện']:
                info['tỷ_lệ_thực_hiện'] = self.extract_field_from_text(
                    text_content, 'Tỷ lệ thực hiện', max_length=500
                )

            if not info['thời_gian_thực_hiện']:
                info['thời_gian_thực_hiện'] = self.extract_field_from_text(
                    text_content, 'Thời gian thực hiện', max_length=300
                )

            if not info['địa_điểm_thực_hiện']:
                info['địa_điểm_thực_hiện'] = self.extract_field_from_text(
                    text_content, 'Địa điểm thực hiện', max_length=500
                )

            if not info['lý_do_mục_đích']:
                info['lý_do_mục_đích'] = self.extract_field_from_text(
                    text_content, 'Lý do|Mục đích', max_length=300
                )

            # Find quyền
            text_lower = text_content.lower()
            if any(word in text_lower for word in ['nhận lãi', 'lãi định kỳ', 'thanh toán lãi']):
                info['quyền_nhận_lãi'] = 'Có'

            if any(word in text_lower for word in ['trả gốc', 'đáo hạn', 'thanh toán gốc']):
                info['quyền_trả_gốc'] = 'Có'

            if any(word in text_lower for word in ['chuyển đổi', 'hoán đổi']):
                info['quyền_chuyển_đổi'] = 'Có'

            return info, extracted_code

        except Exception as e:
            logger.debug(f"  ! Error extracting from HTML: {str(e)[:50]}")
            return None, None

    def extract_detail_from_article(self, url):
        """
        Extract chi tiết thông tin từ URL tin tức
        Trả về tuple (info_dict, extracted_code)
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                return None, None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text content
            main = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|body'))
            if not main:
                return None, None

            text_content = main.get_text()

            # Initialize info
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

            # Find all label-value pairs
            label_divs = soup.find_all('div', class_=re.compile('col-md-4|label|info'))

            for label_div in label_divs:
                label = label_div.get_text(strip=True).lower()
                value_div = label_div.find_next('div', class_=re.compile('col-md-8|value|info-main'))

                if not value_div:
                    continue

                value = value_div.get_text(strip=True)

                # Map labels to info keys
                if 'tên tổ chức đăng ký' in label or 'tên tổ chức' in label:
                    info['tên_tổ_chức_đăng_ký'] = value
                elif 'tên chứng khoán' in label or 'tên trái phiếu' in label:
                    info['tên_chứng_khoán'] = value
                elif 'mã chứng khoán' in label or 'mã ck' in label:
                    extracted_code = value
                elif 'mã isin' in label:
                    info['mã_isin'] = value
                elif 'nơi giao dịch' in label or 'sở giao dịch' in label:
                    info['nơi_giao_dịch'] = value
                elif 'loại chứng khoán' in label or 'loại trái phiếu' in label:
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

            # Fallback extraction cho multi-line fields
            if not info['tỷ_lệ_thực_hiện']:
                info['tỷ_lệ_thực_hiện'] = self.extract_field_from_text(
                    text_content, 'Tỷ lệ thực hiện', max_length=500
                )

            if not info['thời_gian_thực_hiện']:
                info['thời_gian_thực_hiện'] = self.extract_field_from_text(
                    text_content, 'Thời gian thực hiện', max_length=300
                )

            if not info['địa_điểm_thực_hiện']:
                info['địa_điểm_thực_hiện'] = self.extract_field_from_text(
                    text_content, 'Địa điểm thực hiện', max_length=500
                )

            if not info['lý_do_mục_đích']:
                info['lý_do_mục_đích'] = self.extract_field_from_text(
                    text_content, 'Lý do|Mục đích', max_length=300
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

    def search_and_extract_by_symbol(self, symbol):
        """
        Tìm kiếm symbol trên trang HNX dùng Selenium
        Nhập symbol vào field "Đối tượng liên quan", click search
        Mở tin mới nhất, extract chi tiết
        """
        try:
            logger.info(f"🔍 HNX: Tìm kiếm {symbol}...")

            # Mở trang tin tức
            self.driver.get(self.news_url)
            wait = WebDriverWait(self.driver, 10)
            time.sleep(3)  # Chờ page load hoàn toàn

            # Tìm input field "Đối tượng liên quan" (Trái phiếu)
            search_input = None
            selectors = [
                (By.ID, "txtConditionTCPH"),  # TCPH = Trái Chỉ Phiếu Huy động
                (By.ID, "txtConditionHNX"),   # HNX related
                (By.CSS_SELECTOR, "input[type='text']:not([style*='display:none'])"),
            ]

            for by, selector in selectors:
                try:
                    wait_short = WebDriverWait(self.driver, 2)
                    search_input = wait_short.until(
                        EC.presence_of_element_located((by, selector))
                    )
                    logger.info(f"  ✓ Tìm thấy input field")
                    break
                except TimeoutException:
                    continue

            if not search_input:
                logger.info(f"  ⚠ Không tìm thấy input field 'Đối tượng liên quan'")
                # Lưu screenshot để debug
                try:
                    import os
                    screenshot_path = os.path.expanduser("~/hnx_debug.png")
                    self.driver.save_screenshot(screenshot_path)
                    logger.info(f"  💾 Screenshot lưu tại: {screenshot_path}")
                except Exception as e:
                    logger.info(f"  ✗ Lỗi lưu screenshot: {e}")
                return {'status': 'not_found', 'symbol': symbol, 'message': 'Input field not found'}

            # Scroll element vào view
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", search_input)
                time.sleep(0.5)
            except:
                pass

            # Wait cho element be interactable
            try:
                wait_short = WebDriverWait(self.driver, 3)
                wait_short.until(EC.element_to_be_clickable((By.ID, search_input.get_attribute("id") or "dummy")))
            except:
                pass

            # Clear field COMPLETELY và nhập symbol
            try:
                search_input.clear()
                time.sleep(0.3)
                # Clear thêm bằng select all + delete
                search_input.send_keys(Keys.CONTROL + 'a')
                search_input.send_keys(Keys.DELETE)
            except:
                pass

            time.sleep(0.3)

            # Dùng JavaScript để set value đảm bảo clean
            self.driver.execute_script(f"""
                var input = arguments[0];
                input.value = '';
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            """, search_input)

            time.sleep(0.3)

            # Nhập symbol mới
            try:
                search_input.send_keys(symbol)
                time.sleep(0.3)
                self.driver.execute_script("""
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """, search_input)
            except Exception as e:
                # Fallback: chỉ dùng JavaScript
                logger.debug(f"  - send_keys error, using JS: {str(e)[:30]}")
                self.driver.execute_script(f"""
                    var input = arguments[0];
                    input.value = '{symbol}';
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                """, search_input)

            logger.info(f"  ✓ Đã nhập {symbol}")

            time.sleep(1)

            # Tìm và click button tìm kiếm
            search_button = None
            button_selectors = [
                (By.ID, "btn_search"),                            # Chính xác: id="btn_search"
                (By.CSS_SELECTOR, "input#btn_search"),
                (By.CSS_SELECTOR, "input[value='Tìm kiếm']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Tìm')]"),
                (By.CSS_SELECTOR, "button.btn-search"),
            ]

            for by, selector in button_selectors:
                try:
                    wait_short = WebDriverWait(self.driver, 2)
                    search_button = wait_short.until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    logger.info(f"  ✓ Tìm thấy nút tìm kiếm")
                    break
                except TimeoutException:
                    continue

            if search_button:
                try:
                    self.driver.execute_script("arguments[0].click();", search_button)
                    logger.info(f"  ✓ Đã click nút tìm kiếm")
                except Exception as e:
                    logger.error(f"  ✗ Click button error: {e}")
            else:
                logger.info(f"  ⚠ Không tìm thấy nút tìm kiếm, thử nhấn Enter")
                try:
                    search_input.send_keys(Keys.RETURN)
                except:
                    pass

            # Chờ kết quả load - rất quan trọng!
            logger.info(f"  ⏳ Chờ kết quả tìm kiếm...")
            time.sleep(2)

            # Wait cho bảng kết quả được cập nhật
            # Chiến lược: chờ cho số lượng rows thay đổi hoặc chờ specific element
            wait_short = WebDriverWait(self.driver, 15)

            # Cách 1: Chờ cho search được thực thi bằng cách chờ loading indicator
            try:
                # Tìm loading indicator và chờ nó biến mất
                loading_indicators = [
                    (By.CSS_SELECTOR, ".loading"),
                    (By.CSS_SELECTOR, "[class*='loading']"),
                    (By.CSS_SELECTOR, "[id*='loading']"),
                    (By.XPATH, "//*[contains(@style, 'display') and contains(@class, 'loading')]"),
                ]

                for by, selector in loading_indicators:
                    try:
                        wait_short.until(EC.invisibility_of_element_located((by, selector)))
                        logger.info(f"  ✓ Loading indicator biến mất")
                        break
                    except:
                        pass
            except:
                pass

            # Cách 2: Chờ table rows có dữ liệu
            try:
                # Chờ multiple rows (chứng tỏ search đã execute)
                wait_short.until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, "table tbody tr")) > 1
                )
                logger.info(f"  ✓ Kết quả tìm kiếm đã load (multiple rows)")
            except TimeoutException:
                logger.info(f"  ⚠ Chờ timeout, tiếp tục...")

            # Cách 3: CHỜ DỮ LIỆU CỘT SYMBOL ĐƯỢC LOAD (quan trọng!)
            # Cột "Đối tượng liên quan" được load via AJAX nên cần chờ riêng
            logger.info(f"  ⏳ Chờ AJAX load dữ liệu cột SYMBOL...")

            # Thử chờ jQuery AJAX hoàn thành
            try:
                wait_short.until(
                    lambda d: d.execute_script("return jQuery.active == 0")
                )
                logger.info(f"  ✓ jQuery AJAX hoàn thành")
            except:
                logger.info(f"  ⚠ Không thể detect jQuery AJAX, tiếp tục...")

            # Thử chờ SYMBOL cells có dữ liệu
            try:
                wait_short.until(
                    lambda d: any(
                        cell.text.strip()
                        for cell in d.find_elements(By.CSS_SELECTOR, "td.SYMBOL")
                    )
                )
                logger.info(f"  ✓ Dữ liệu cột 'Đối tượng liên quan' đã load")
            except TimeoutException:
                logger.info(f"  ⚠ Cột dữ liệu không load trong 10s, chờ thêm...")
                time.sleep(5)  # Chờ thêm 5s nữa

            time.sleep(2)  # Chờ thêm để JS fully render

            # Tìm link kết quả từ bảng tìm kiếm
            logger.info(f"  🔎 Tìm link ở STT=1...")

            # DEBUG: Save HTML để inspect
            try:
                import os
                html_debug_path = os.path.expanduser(f"~/hnx_search_results_{symbol}.html")
                with open(html_debug_path, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                logger.info(f"  💾 Debug HTML saved: {html_debug_path}")
            except Exception as e:
                logger.debug(f"  - Cannot save debug HTML: {e}")

            # Selector chính xác: Lấy link từ dòng đầu tiên (STT=1) của table kết quả
            # Rất quan trọng: tìm link CHỈ từ table kết quả, không phải từ toàn bộ page
            news_links = []

            selectors_for_links = [
                # Cách 1: Table cuối cùng (search results table thường ở cuối)
                (By.XPATH, "(//table)[last()]//tbody/tr[1]//a[contains(@onclick, 'funcViewDetailArticlesByID')]"),

                # Cách 2: Dòng đầu tiên trong tbody cuối cùng
                (By.XPATH, "//table[.//tbody//a[contains(@onclick, 'funcViewDetailArticlesByID')]][last()]//tbody//tr[1]//a"),

                # Cách 3: CSS - first tr in last table
                (By.CSS_SELECTOR, "table:last-of-type tbody tr:first-child a.hrefViewDetail"),

                # Cách 4: Tất cả links và lấy cái đầu tiên (sau khi đã wait)
                (By.CSS_SELECTOR, "a.hrefViewDetail"),
            ]

            for by, selector in selectors_for_links:
                try:
                    temp_links = self.driver.find_elements(by, selector)
                    if temp_links:
                        logger.info(f"  ✓ Tìm thấy {len(temp_links)} link (selector: {selector if isinstance(selector, str) else 'xpath'})")
                        # Debug: Log tất cả link titles để xem đoàn nào
                        for idx, link in enumerate(temp_links[:3]):  # Log first 3
                            try:
                                link_text = link.text[:60]
                                onclick = link.get_attribute('onclick') or ''
                                logger.info(f"     [{idx}] {link_text}... (onclick: {onclick[:50]})")
                            except:
                                pass
                        news_links = temp_links
                        break
                except Exception as e:
                    logger.debug(f"  - Selector không có kết quả: {str(e)[:30]}")
                    continue

            if not news_links:
                logger.info(f"  ⚠ Không tìm thấy link kết quả")
                # Lưu screenshot để debug
                try:
                    import os
                    screenshot_path = os.path.expanduser(f"~/hnx_search_{symbol}.png")
                    self.driver.save_screenshot(screenshot_path)
                    logger.info(f"  💾 Screenshot lưu tại: {screenshot_path}")
                except:
                    pass
                return {'status': 'not_found', 'symbol': symbol, 'message': 'No search results'}

            # Có kết quả - xử lý link đầu tiên
            try:
                logger.info(f"  ✓ Tìm thấy {len(news_links)} kết quả")

                # Lấy link đầu tiên (mới nhất)
                first_link = news_links[0]
                news_title = first_link.text[:100]

                # Debug: Log the onclick content để verify đúng link
                onclick_attr = first_link.get_attribute('onclick') or ''
                logger.info(f"  → Mở tin: {news_title}")
                logger.info(f"  → onclick attr: {onclick_attr[:80]}")

                # Scroll link vào view để chắc chắn nó visible trước khi click
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", first_link)
                    time.sleep(0.5)
                except:
                    logger.debug(f"  - Cannot scroll to link")

                # Click vào link để mở popup
                try:
                    self.driver.execute_script("arguments[0].click();", first_link)
                except:
                    # Fallback: regular click
                    first_link.click()

                time.sleep(3)

                # Wait cho popup/modal load - chờ lâu hơn vì có thể load động
                wait_short = WebDriverWait(self.driver, 10)

                # Thử các selector khác nhau cho modal
                modal_found = False
                modal_selectors = [
                    (By.CSS_SELECTOR, ".modal.show"),
                    (By.CSS_SELECTOR, "[id*='modal'][style*='display']"),
                    (By.CSS_SELECTOR, "[id*='popup'][style*='display']"),
                    (By.CSS_SELECTOR, "div[role='dialog']"),
                    (By.XPATH, "//*[contains(@class, 'modal') and contains(@style, 'display')]"),
                    (By.CSS_SELECTOR, "div.modal"),  # Fallback: any div with class modal
                ]

                for by, selector in modal_selectors:
                    try:
                        modal = wait_short.until(
                            EC.visibility_of_element_located((by, selector))
                        )
                        logger.info(f"  ✓ Popup opened (selector matched)")
                        modal_found = True
                        time.sleep(1)  # Chờ thêm cho animation/rendering
                        break
                    except TimeoutException:
                        continue

                if not modal_found:
                    logger.info(f"  ⚠ Popup không load với modal selector, chờ thêm...")
                    time.sleep(3)  # Chờ lâu hơn

                # Extract chi tiết từ popup content
                # Lấy body hoặc toàn bộ page_source (popup có thể overlay trên page)
                page_source = self.driver.page_source

                # Debug: Log size của page source để verify popup đã load
                logger.info(f"  📄 Page source size: {len(page_source)} chars")

                detail, extracted_code = self.extract_detail_from_article_html(page_source)

                # Nếu không extract được title, thử lấy từ popup text content
                if not detail or (detail and not detail.get('tên_chứng_khoán')):
                    logger.info(f"  → Thử extract từ text content của modal")
                    try:
                        # Tìm text content trong modal
                        modal_text = self.driver.execute_script("""
                            let modals = document.querySelectorAll('.modal, [role="dialog"], [id*="modal"]');
                            let content = '';
                            for (let m of modals) {
                                if (m.offsetParent !== null) {  // visible
                                    content += m.innerText || m.textContent;
                                }
                            }
                            return content;
                        """)

                        if modal_text:
                            logger.info(f"  ✓ Modal text found ({len(modal_text)} chars)")
                            # Parse modal text để lấy thông tin
                            if not extracted_code:
                                # Thử tìm mã chứng khoán trong text
                                match = re.search(r'\b[A-Z0-9]{6,10}\b', modal_text)
                                if match:
                                    extracted_code = match.group(0)
                    except Exception as e:
                        logger.debug(f"  - Error getting modal text: {str(e)[:30]}")

                # Ưu tiên mã từ detail
                final_code = extracted_code if extracted_code else symbol

                result = {
                    'symbol': symbol,
                    'code': final_code,
                    'title': news_title,
                    'source': 'HNX',
                    'status': 'success'
                }

                if detail:
                    result.update(detail)
                    # Debug: log extracted fields
                    extracted_count = sum(1 for v in detail.values() if v is not None)
                    logger.info(f"  📊 Extracted {extracted_count} fields from detail")
                    if detail.get('tên_chứng_khoán'):
                        logger.info(f"     → Tên CK: {detail['tên_chứng_khoán'][:50]}")
                    if detail.get('tên_tổ_chức_đăng_ký'):
                        logger.info(f"     → Tổ chức: {detail['tên_tổ_chức_đăng_ký'][:50]}")

                logger.info(f"  ✓ Extract xong {symbol}")

                # Close popup (tìm nút close)
                try:
                    close_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[id*='close'], [class*='close'], .btn-close, [data-dismiss]")
                    if close_buttons:
                        self.driver.execute_script("arguments[0].click();", close_buttons[0])
                        time.sleep(0.5)
                except:
                    pass

                return result

            except Exception as e:
                logger.error(f"  ✗ Error finding/opening news link: {str(e)[:50]}")
                return {'status': 'error', 'symbol': symbol, 'message': str(e)}

        except Exception as e:
            logger.error(f"  ✗ Search error: {str(e)[:50]}")
            return {'status': 'error', 'symbol': symbol, 'message': str(e)}

    def fetch_for_symbols(self, symbols):
        """
        Fetch thông tin cho danh sách symbols
        """
        try:
            logger.info(f"🚀 HNX: Bắt đầu fetch {len(symbols)} mã chứng khoán")
            logger.info("=" * 60)

            all_results = []

            for symbol in symbols:
                result = self.search_and_extract_by_symbol(symbol)
                all_results.append(result)
                time.sleep(1)

            logger.info("\n" + "=" * 60)
            found_count = sum(1 for r in all_results if r.get('status') == 'success')
            logger.info(f"✅ Hoàn thành. Tìm thấy: {found_count}/{len(all_results)}")
            logger.info("=" * 60 + "\n")

            return {
                'status': 'success',
                'data': all_results,
                'count': len(all_results),
                'found': found_count,
                'url': self.news_url,
                'fetched_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"✗ HNX Fetch Error: {str(e)[:100]}")
            return {
                'status': 'error',
                'message': str(e)
            }

def read_symbols_from_file(filepath):
    """Đọc danh sách symbols từ file"""
    try:
        with open(filepath, 'r') as f:
            symbols = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        # Remove duplicates while preserving order
        seen = set()
        unique_symbols = []
        for s in symbols:
            if s not in seen:
                seen.add(s)
                unique_symbols.append(s)
        return unique_symbols
    except Exception as e:
        logger.error(f"Error reading symbols file: {e}")
        return []

def main():
    # Đọc symbols từ symbol.md hoặc từ command line
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
    else:
        symbols = read_symbols_from_file('/Users/hieudt/vps-automation-vhck/symbol.md')
        if not symbols:
            logger.error("No symbols provided and symbol.md not found")
            sys.exit(1)

    fetcher = HNXFetcher()

    try:
        fetcher.init_driver()
        result = fetcher.fetch_for_symbols(symbols)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        fetcher.close_driver()

if __name__ == '__main__':
    main()
