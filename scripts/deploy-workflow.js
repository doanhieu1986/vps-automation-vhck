#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const http = require('http');

// Configuration
const N8N_URL = 'http://localhost:5678';
const API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZGI0MzE2Ni0zMzM2LTQwZDYtYWRlMy0xZjkzYmViYTBmZDciLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZmRmMmI3MTEtMzJkMC00ODNmLThhNTEtYzhjNmUzNzRlMTRiIiwiaWF0IjoxNzc1ODAzNDY4fQ.QFkYu5UGAgOpa8H8ohO18U8597FkZuJC3EoKp-6Jqts';
const WORKFLOW_FILE = path.join(__dirname, '../n8n/VPS Automation VHCK v7 - Direct Excel Export.json');

async function deployWorkflow() {
  try {
    console.log('📝 Đang đọc workflow file...');
    const workflowData = JSON.parse(fs.readFileSync(WORKFLOW_FILE, 'utf-8'));
    const workflowId = workflowData.id;

    console.log(`📤 Đang deploy workflow: ${workflowData.name}`);
    console.log(`   Workflow ID: ${workflowId}`);

    // Remove fields that shouldn't be sent
    const payload = {
      name: workflowData.name,
      nodes: workflowData.nodes,
      connections: workflowData.connections
    };

    // Only include allowed settings
    if (workflowData.settings) {
      payload.settings = {
        ...(workflowData.settings.executionOrder && { executionOrder: workflowData.settings.executionOrder }),
        ...(workflowData.settings.timezone && { timezone: workflowData.settings.timezone }),
        ...(workflowData.settings.errorWorkflow && { errorWorkflow: workflowData.settings.errorWorkflow })
      };
    }

    const url = new URL(`${N8N_URL}/api/v1/workflows/${workflowId}`);
    const body = JSON.stringify(payload);

    const options = {
      hostname: url.hostname,
      port: url.port || 80,
      path: url.pathname + url.search,
      method: 'PUT',
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
              console.log(`✅ Deploy thành công!`);
              console.log(`   Workflow: ${result.name}`);
              console.log(`   Status: ${result.active ? '🟢 Active' : '🔴 Inactive'}`);
              console.log(`   Nodes: ${result.nodes.length}`);
              console.log(`   Updated: ${new Date(result.updatedAt).toLocaleString('vi-VN')}`);
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
deployWorkflow().catch(error => {
  console.error('❌ Lỗi:', error.message);
  process.exit(1);
});
