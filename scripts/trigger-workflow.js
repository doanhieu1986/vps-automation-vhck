#!/usr/bin/env node

const http = require('http');

const N8N_URL = 'http://localhost:5678';
const API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZGI0MzE2Ni0zMzM2LTQwZDYtYWRlMy0xZjkzYmViYTBmZDciLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZmRmMmI3MTEtMzJkMC00ODNmLThhNTEtYzhjNmUzNzRlMTRiIiwiaWF0IjoxNzc1ODAzNDY4fQ.QFkYu5UGAgOpa8H8ohO18U8597FkZuJC3EoKp-6Jqts';
const WORKFLOW_ID = 'gSi7vlUxGOvRrGVF';

async function triggerWorkflow() {
  console.log('🚀 Đang trigger workflow...');

  const options = {
    hostname: 'localhost',
    port: 5678,
    path: `/api/v1/workflows/${WORKFLOW_ID}/execute`,
    method: 'POST',
    headers: {
      'X-N8N-API-KEY': API_KEY,
      'Content-Type': 'application/json',
      'Content-Length': 2
    }
  };

  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            const result = JSON.parse(data);
            console.log(`✅ Workflow triggered thành công!`);
            console.log(`   Execution ID: ${result.execution?.id || result.id || 'N/A'}`);
            console.log(`   Status: ${result.execution?.status || result.status || 'running'}`);
            resolve(result);
          } catch (e) {
            reject(new Error(`Parse response failed: ${e.message}`));
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    });

    req.on('error', reject);
    req.write('{}');
    req.end();
  });
}

triggerWorkflow().catch(error => {
  console.error('❌ Lỗi:', error.message);
  process.exit(1);
});
