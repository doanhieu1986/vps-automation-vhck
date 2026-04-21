#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const http = require('http');

// Configuration
const N8N_URL = 'http://localhost:5678';
const API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZGI0MzE2Ni0zMzM2LTQwZDYtYWRlMy0xZjkzYmViYTBmZDciLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZmRmMmI3MTEtMzJkMC00ODNmLThhNTEtYzhjNmUzNzRlMTRiIiwiaWF0IjoxNzc1ODAzNDY4fQ.QFkYu5UGAgOpa8H8ohO18U8597FkZuJC3EoKp-6Jqts';
const WORKFLOW_FILE = path.join(__dirname, '../n8n/VPS Automation VHCK v8 - Complete Flow.json');

async function deployWorkflow() {
  try {
    console.log('📝 Đang đọc workflow v8 file...');
    const workflowData = JSON.parse(fs.readFileSync(WORKFLOW_FILE, 'utf-8'));

    // Generate new ID or use existing
    const workflowId = workflowData.id || require('crypto').randomBytes(8).toString('hex');
    console.log(`📤 Đang deploy workflow: ${workflowData.name}`);
    console.log(`   Workflow ID: ${workflowId}`);
    console.log(`   Nodes: ${workflowData.nodes.length}`);

    const payload = {
      name: workflowData.name,
      nodes: workflowData.nodes,
      connections: workflowData.connections
    };

    if (workflowData.settings) {
      payload.settings = workflowData.settings;
    }

    const url = new URL(`${N8N_URL}/api/v1/workflows`);
    const body = JSON.stringify(payload);

    const options = {
      hostname: url.hostname,
      port: url.port || 80,
      path: url.pathname,
      method: 'POST',
      headers: {
        'X-N8N-API-KEY': API_KEY,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body)
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
              console.log(`\n✅ Deploy thành công!`);
              console.log(`   Workflow: ${result.name}`);
              console.log(`   ID: ${result.id}`);
              console.log(`   Status: 🔴 Inactive (kích hoạt trong n8n UI)`);
              console.log(`   Nodes: ${result.nodes.length}`);
              console.log(`   URL n8n: http://localhost:5678/workflow/${result.id}`);
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
      req.write(body);
      req.end();
    });
  } catch (error) {
    console.error('❌ Deploy thất bại:', error.message);
    process.exit(1);
  }
}

// Run deployment
console.log('🚀 Deploying VPS Automation VHCK v8...\n');
deployWorkflow().catch(error => {
  console.error('❌ Lỗi:', error.message);
  process.exit(1);
});
