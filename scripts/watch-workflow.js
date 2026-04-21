#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const WORKFLOW_FILE = path.join(__dirname, '../n8n/VPS Automation VHCK v7 - Direct Excel Export.json');

console.log('👀 Watching workflow file for changes...');
console.log(`📁 File: ${WORKFLOW_FILE}\n`);

let lastMtime = fs.statSync(WORKFLOW_FILE).mtime;
let isDeploying = false;

fs.watchFile(WORKFLOW_FILE, (curr, prev) => {
  // Skip if file is still being written
  if (isDeploying) return;

  // Skip if file hasn't actually changed (just mtime update)
  if (curr.mtime === lastMtime) return;

  lastMtime = curr.mtime;

  console.log(`\n⏰ ${new Date().toLocaleTimeString('vi-VN')} - Phát hiện thay đổi workflow`);
  console.log('📤 Đang deploy...\n');

  isDeploying = true;

  exec('node scripts/deploy-workflow.js', (error, stdout, stderr) => {
    isDeploying = false;

    if (error) {
      console.error('❌ Deploy thất bại:');
      console.error(stderr || stdout);
      return;
    }

    console.log(stdout);
    console.log(`✅ Workflow đã được update trên n8n!\n`);
    console.log('👀 Tiếp tục watching...\n');
  });
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n👋 Đã dừng watching workflow');
  process.exit(0);
});
