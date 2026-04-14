#!/bin/bash
# Script to fetch VSD data, merge with existing records, and update result.md
# Usage: bash scripts/update_result_md.sh
# Schedule: 0 12,17 * * * (12h và 17h mỗi ngày)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "🔄 $(date '+%H:%M:%S %d/%m/%Y') - Starting VSD data update..."

# Run Node.js script to fetch, merge, and update
node << 'EOJS'
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

try {
  console.log('⏳ Fetching VSD data...');
  const output = execSync('python3 scripts/fetch_vsd.py 2>/dev/null', { encoding: 'utf-8' });
  const vsdResult = JSON.parse(output);

  console.log(`✓ Fetched ${vsdResult.count} NEW records from VSD`);

  // Merge với records cũ từ vsd_records.json
  let allRecords = (vsdResult.data || []);
  let existingCount = 0;
  const fetchedNewCount = allRecords.length;  // Số records fetch từ VSD
  let insertedCount = 0;  // Số records thực sự mới (không duplicate)

  if (fs.existsSync('data/vsd_records.json')) {
    try {
      const existing = JSON.parse(fs.readFileSync('data/vsd_records.json', 'utf-8'));
      const existingRecords = existing.records || [];
      existingCount = existingRecords.length;

      // Create map of existing codes để check duplicate
      const existingCodes = new Set(existingRecords.map(r => r.code));
      const allSeenCodes = new Set(existingCodes);  // Track all codes to prevent ANY duplicate

      // Đếm bao nhiêu records mới thực sự là unique (không có trong existing)
      const newRecords = [];
      for (const rec of allRecords) {
        if (!allSeenCodes.has(rec.code)) {
          newRecords.push(rec);
          allSeenCodes.add(rec.code);
          insertedCount++;
        }
      }

      // Add existing records (after dedup, ensure no duplicates)
      const dedupedExisting = existingRecords.filter(r => !newRecords.some(nr => nr.code === r.code));
      allRecords = [...newRecords, ...dedupedExisting];

      console.log(`✓ Merged: ${fetchedNewCount} FETCHED, ${insertedCount} NEW INSERT, ${existingCount} EXISTING = ${allRecords.length} TOTAL`);
    } catch (e) {
      console.log(`⚠ Warning: Could not merge existing records: ${e.message}`);
      insertedCount = fetchedNewCount;  // Fallback: assume all are new
    }
  } else {
    insertedCount = fetchedNewCount;  // No existing data, all are new
  }

  // Store counts for later use
  const recordStats = {
    fetchedNewCount: fetchedNewCount,  // Từ VSD
    insertedCount: insertedCount,      // Thực sự mới (after merge check)
    existingCount: existingCount,      // Từ lần chạy trước
    totalCount: allRecords.length
  };

  // Process all records
  const records = allRecords.map(record => ({
    code: record.code,
    symbol: record.code,
    mã_chứng_khoán: record.code,
    tên_tổ_chức_đăng_ký: record.tên_tổ_chức_đăng_ký || "Cần cập nhật",
    tên_chứng_khoán: record.tên_chứng_khoán || "Cần cập nhật",
    mã_isin: record.mã_isin || "Cần cập nhật",
    nơi_giao_dịch: record.nơi_giao_dịch || record.source || "N/A",
    loại_chứng_khoán: record.loại_chứng_khoán || "Trái Phiếu",
    ngày_đăng_ký_cuối: record.ngày_đăng_ký_cuối || "Cần cập nhật",
    lý_do_mục_đích: record.lý_do_mục_đích || "Cần cập nhật",
    tỷ_lệ_thực_hiện: record.tỷ_lệ_thực_hiện || "Cần cập nhật",
    thời_gian_thực_hiện: record.thời_gian_thực_hiện || "Cần cập nhật",
    địa_điểm_thực_hiện: record.địa_điểm_thực_hiện || "Cần cập nhật",
    quyền_nhận_lãi: record.quyền_nhận_lãi || "Chưa xác định",
    quyền_trả_gốc: record.quyền_trả_gốc || "Chưa xác định",
    quyền_chuyển_đổi: record.quyền_chuyển_đổi || "Chưa xác định",
    source: record.source,
    title: record.title,
    url: record.url,
    status: "pending",
    confirmation_status: "awaiting_review",
    collected_at: new Date().toISOString(),
    source_links: { vsd: "https://www.vsd.vn/vi/tin-thi-truong-co-so" }
  }));

  const summary = {
    total: records.length,
    vsd: records.length,
    total_unique: records.length,
    pending_confirmation: records.filter(r => r.confirmation_status === "awaiting_review").length
  };

  // Save to vsd_records.json
  const timestamp = new Date().toLocaleString('vi-VN');
  const jsonData = {
    source: "VSD",
    collected_at: new Date().toISOString(),
    timestamp: timestamp,
    total_records: records.length,
    summary: summary,
    records: records
  };

  fs.writeFileSync('data/vsd_records.json', JSON.stringify(jsonData, null, 2), 'utf-8');
  console.log(`✓ Saved ${records.length} records to vsd_records.json`);

  // Update result.md with prepend + preserve history
  const resultPath = 'data/result.md';
  const headerLine = '# Kết Quả Thu Thập Thông Tin Quyền Chứng Khoán';
  let historyContent = '';

  if (fs.existsSync(resultPath)) {
    const existingContent = fs.readFileSync(resultPath, 'utf-8');
    if (existingContent) {
      const headerIndex = existingContent.indexOf(headerLine);
      if (headerIndex !== -1) {
        const headerEnd = headerIndex + headerLine.length;
        const doubleNewlineIndex = existingContent.indexOf('\n\n', headerEnd);
        if (doubleNewlineIndex !== -1) {
          historyContent = existingContent.substring(doubleNewlineIndex + 2);
        }
      }
    }
  }

  // Generate update section with detailed record counts
  const updateSection = `## 📊 Thống Kê

- **Cập nhật lúc:** ${timestamp}
- **Records fetch từ VSD:** ${recordStats.fetchedNewCount} (ngày gần nhất)
- **Records insert mới:** ${recordStats.insertedCount} (không duplicate)
- **Records cũ:** ${recordStats.existingCount} (từ những ngày trước)
- **Tổng bản ghi (duy nhất):** ${summary.total}
  - VSD: ${summary.vsd}
- **Chờ xác nhận:** ${summary.pending_confirmation}
`;

  // Build new content
  let newContent = headerLine + '\n\n' + updateSection + '\n---';
  if (historyContent && historyContent.trim()) {
    newContent += '\n\n' + historyContent;
  }

  fs.writeFileSync(resultPath, newContent, 'utf-8');
  console.log(`✓ Updated result.md (total: ${summary.total})`);
  console.log(`✅ Done at ${new Date().toLocaleString('vi-VN')}`);

} catch (error) {
  console.error(`❌ Error: ${error.message}`);
  process.exit(1);
}
EOJS
