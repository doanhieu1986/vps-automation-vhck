#!/usr/bin/env python3
"""
Simple Flask server để N8n workflow gọi và save result.md
Chạy: python3 save_result.py
Server sẽ chạy tại http://localhost:5000
"""

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_FILE = os.path.join(PROJECT_DIR, 'result.md')

@app.route('/api/save-result', methods=['POST'])
def save_result():
    """
    Endpoint để save markdown content vào result.md

    POST body:
    {
        "markdown": "content...",
        "records": [...],
        "summary": {...}
    }
    """
    try:
        data = request.get_json()
        markdown_content = data.get('markdown', '')
        records = data.get('records', [])

        if not markdown_content:
            return jsonify({
                'status': 'error',
                'message': 'Markdown content is empty'
            }), 400

        # Save to result.md
        with open(RESULT_FILE, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return jsonify({
            'status': 'success',
            'message': f'Saved {len(records)} records to result.md',
            'file': RESULT_FILE,
            'timestamp': datetime.now().isoformat(),
            'records_count': len(records)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/get-result', methods=['GET'])
def get_result():
    """
    Endpoint để lấy nội dung result.md
    """
    try:
        if not os.path.exists(RESULT_FILE):
            return jsonify({
                'status': 'error',
                'message': 'result.md not found'
            }), 404

        with open(RESULT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({
            'status': 'success',
            'content': content,
            'file': RESULT_FILE,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'VPS Automation Helper',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    print("🚀 Starting VPS Automation Helper Server...")
    print("📍 Server running at: http://localhost:3000")
    print("💾 Result file location:", RESULT_FILE)
    print("\nAvailable endpoints:")
    print("  POST /api/save-result - Save markdown to result.md")
    print("  GET  /api/get-result  - Get result.md content")
    print("  GET  /health         - Health check")
    print("\n💡 For N8n workflow, use HTTP nodes to call these endpoints")
    print("⚠️  Keep this server running while executing N8n workflow\n")

    app.run(host='0.0.0.0', port=3000, debug=False)
