# VPS Automation Scripts

Thư mục này chứa các scripts Python để fetch dữ liệu thông tin quyền chứng khoán từ các sàn giao dịch Việt Nam.

## Scripts

### 1. `fetch_vsd.py` - Vietnamese Securities Depository
- **URL:** https://www.vsd.vn
- **Purpose:** Fetch thông tin quyền từ VSD
- **Usage:** `python3 fetch_vsd.py BVBS14199 HCMB18240`

### 2. `fetch_hnx.py` - Hanoi Stock Exchange
- **URL:** https://www.hnx.vn
- **Purpose:** Fetch thông tin quyền từ HNX (Trái phiếu, Cổ phiếu)
- **Usage:** `python3 fetch_hnx.py BVBS14199 HCMB18240`

### 3. `fetch_hose.py` - Ho Chi Minh Stock Exchange
- **URL:** https://www.hsx.vn
- **Purpose:** Fetch thông tin quyền từ HOSE (Chứng chỉ, Trái phiếu)
- **Usage:** `python3 fetch_hose.py BVBS14199 HCMB18240`

### 4. `fetch_all.py` - Unified Fetcher
- **Purpose:** Gọi tất cả 3 fetchers và kết hợp kết quả
- **Usage:** `python3 fetch_all.py BVBS14199 HCMB18240 TD1429094`
- **Output:** JSON với data từ tất cả 3 sources

## Installation

Yêu cầu Python packages:
```bash
pip install requests beautifulsoup4
```

Hoặc:
```bash
pip install -r requirements.txt
```

## Usage

### Individual Fetchers
```bash
# Fetch từ VSD
python3 fetch_vsd.py BVBS14199

# Fetch từ HNX
python3 fetch_hnx.py HCMB18240

# Fetch từ HOSE
python3 fetch_hose.py TD1429094
```

### All Sources (Recommended)
```bash
# Fetch từ tất cả 3 sources
python3 fetch_all.py BVBS14199 HCMB18240 TD1429094 HCMB14181 HCMB15313
```

## Output Format

```json
{
  "status": "success",
  "timestamp": "2026-04-12T17:30:00.000000",
  "total_symbols": 5,
  "records": [
    {
      "symbol": "BVBS14199",
      "mã_chứng_khoán": "BVBS14199",
      "collected_at": "2026-04-12T17:30:00.000000",
      "sources": {
        "vsd": {
          "status": "success",
          "data": [...]
        },
        "hnx": {
          "status": "success",
          "data": [...]
        },
        "hose": {
          "status": "success",
          "data": [...]
        }
      },
      "collection_status": {
        "total_sources": 3,
        "successful_sources": 3,
        "overall": "success"
      }
    }
  ]
}
```

## N8n Integration

N8n workflow có thể gọi script này bằng cách sử dụng **Execute Command** node:

```javascript
// N8n Execute Command Configuration
Command: python3
Arguments: [
  "/Users/hieudt/vps-automation-vhck/scripts/fetch_all.py",
  $node.json.symbol1,
  $node.json.symbol2,
  ...
]
```

Hoặc bằng HTTP request tới một wrapper endpoint.

## Error Handling

- Nếu một source không accessible, script sẽ bỏ qua và tiếp tục với sources khác
- Timeout: 10 giây per request
- Rate limiting: 1 giây giữa các requests

## Notes

- Scripts sử dụng BeautifulSoup để parse HTML (web scraping)
- Không sử dụng API chính thức vì không công khai
- Có thể cần update selectors nếu website thay đổi layout
- Tôn trọng robots.txt và không abuse rate limits
