#!/usr/bin/env node

const http = require('http');

const API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZGI0MzE2Ni0zMzM2LTQwZDYtYWRlMy0xZjkzYmViYTBmZDciLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZmRmMmI3MTEtMzJkMC00ODNmLThhNTEtYzhjNmUzNzRlMTRiIiwiaWF0IjoxNzc1ODAzNDY4fQ.QFkYu5UGAgOpa8H8ohO18U8597FkZuJC3EoKp-6Jqts';
const WORKFLOW_ID = 'gSi7vlUxGOvRrGVF';

function request(path, method, body = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: 5678,
      path,
      method,
      headers: {
        'X-N8N-API-KEY': API_KEY,
        'Content-Type': 'application/json'
      }
    };

    if (body) {
      const bodyStr = JSON.stringify(body);
      options.headers['Content-Length'] = Buffer.byteLength(bodyStr);
    }

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(data));
          } catch {
            resolve({ statusCode: res.statusCode });
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    });

    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function run() {
  try {
    console.log('1️⃣ Đang kiểm tra workflow...');
    const workflow = await request(`/api/v1/workflows/${WORKFLOW_ID}`);
    console.log('✅ Workflow found:', workflow.name);
    console.log('   Status: ' + (workflow.active ? '🟢 Active' : '🔴 Inactive') + '\n');

    // Workflow có manual trigger, không thể trigger qua API
    console.log('2️⃣ Chuẩn bị trigger workflow...\n');

    console.log('\n⚠️  Workflow có Manual Trigger, cần trigger thông qua UI');
    console.log('📌 Hãy làm theo các bước sau:');
    console.log('1. Mở http://localhost:5678');
    console.log('2. Tìm workflow "VPS Automation VHCK v7 - Direct Excel Export"');
    console.log('3. Nhấn nút "Execute Workflow" hoặc "Test"');
    console.log('4. Chờ quá trình hoàn thành (1-3 phút)');
    console.log('5. Kiểm tra:');
    console.log('   - GitHub Pages: https://doanhieu1986.github.io/vps-automation-vhck/');
    console.log('   - Local HTML: ./web/vps_automation_vhck.html');

  } catch (error) {
    console.error('❌ Lỗi:', error.message);
    process.exit(1);
  }
}

run();
