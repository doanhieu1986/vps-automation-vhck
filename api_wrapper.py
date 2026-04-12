#!/usr/bin/env python3
"""
API Wrapper for N8n Workflow
Exposes Python fetch scripts as HTTP endpoints
This allows N8n to call fetch_vsd, fetch_hnx, fetch_hose separately
"""

from flask import Flask, request, jsonify
import subprocess
import json
import sys
import threading
from datetime import datetime

app = Flask(__name__)

def run_python_script(script_name, symbol):
    """Run a Python script and return JSON result"""
    try:
        script_path = f'/Users/hieudt/vps-automation-vhck/scripts/{script_name}'
        result = subprocess.run(
            ['python3', script_path, symbol],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {
                    'status': 'error',
                    'message': 'Invalid JSON output',
                    'raw': result.stdout[:200]
                }
        else:
            return {
                'status': 'error',
                'message': result.stderr or 'Unknown error',
                'returncode': result.returncode
            }

    except subprocess.TimeoutExpired:
        return {'status': 'error', 'message': 'Timeout'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# ============================================================================
# ENDPOINTS FOR N8N WORKFLOW
# ============================================================================

@app.route('/api/fetch-vsd', methods=['POST', 'GET'])
def fetch_vsd():
    """
    POST/GET /api/fetch-vsd
    Fetch all bonds from VSD latest date (no parameters needed)
    Returns all security codes updated on latest date with detailed information
    """
    try:
        script_path = '/Users/hieudt/vps-automation-vhck/scripts/fetch_vsd.py'
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            try:
                return jsonify(json.loads(result.stdout)), 200
            except json.JSONDecodeError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid JSON output',
                    'raw': result.stdout[:200]
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': result.stderr or 'Unknown error',
                'returncode': result.returncode
            }), 500

    except subprocess.TimeoutExpired:
        return jsonify({'status': 'error', 'message': 'Timeout'}), 504
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/fetch-hnx', methods=['POST', 'GET'])
def fetch_hnx():
    """
    POST/GET /api/fetch-hnx
    Fetch all bonds from HNX (no parameters needed)
    Returns all bonds with detailed information
    """
    try:
        script_path = '/Users/hieudt/vps-automation-vhck/scripts/fetch_hnx.py'
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            try:
                return jsonify(json.loads(result.stdout)), 200
            except json.JSONDecodeError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid JSON output',
                    'raw': result.stdout[:200]
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': result.stderr or 'Unknown error',
                'returncode': result.returncode
            }), 500

    except subprocess.TimeoutExpired:
        return jsonify({'status': 'error', 'message': 'Timeout'}), 504
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/fetch-hose', methods=['POST', 'GET'])
def fetch_hose():
    """
    POST/GET /api/fetch-hose
    Fetch all certificates/bonds from HOSE (no parameters needed)
    Returns all securities with detailed information
    """
    try:
        script_path = '/Users/hieudt/vps-automation-vhck/scripts/fetch_hose.py'
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            try:
                return jsonify(json.loads(result.stdout)), 200
            except json.JSONDecodeError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid JSON output',
                    'raw': result.stdout[:200]
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': result.stderr or 'Unknown error',
                'returncode': result.returncode
            }), 500

    except subprocess.TimeoutExpired:
        return jsonify({'status': 'error', 'message': 'Timeout'}), 504
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/fetch-all-sources', methods=['POST', 'GET'])
def fetch_all_sources():
    """
    POST/GET /api/fetch-all-sources
    Fetch from all three sources (VSD, HNX, HOSE) and combine results
    Returns merged data from all sources with latest updates
    """
    try:
        all_results = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }

        # Fetch from VSD
        try:
            vsd_script = '/Users/hieudt/vps-automation-vhck/scripts/fetch_vsd.py'
            vsd_result = subprocess.run(
                ['python3', vsd_script],
                capture_output=True,
                text=True,
                timeout=60
            )
            if vsd_result.returncode == 0:
                all_results['sources']['vsd'] = json.loads(vsd_result.stdout)
            else:
                all_results['sources']['vsd'] = {'status': 'error', 'message': vsd_result.stderr}
        except Exception as e:
            all_results['sources']['vsd'] = {'status': 'error', 'message': str(e)}

        # Fetch from HNX
        try:
            hnx_script = '/Users/hieudt/vps-automation-vhck/scripts/fetch_hnx.py'
            hnx_result = subprocess.run(
                ['python3', hnx_script],
                capture_output=True,
                text=True,
                timeout=60
            )
            if hnx_result.returncode == 0:
                all_results['sources']['hnx'] = json.loads(hnx_result.stdout)
            else:
                all_results['sources']['hnx'] = {'status': 'error', 'message': hnx_result.stderr}
        except Exception as e:
            all_results['sources']['hnx'] = {'status': 'error', 'message': str(e)}

        # Fetch from HOSE
        try:
            hose_script = '/Users/hieudt/vps-automation-vhck/scripts/fetch_hose.py'
            hose_result = subprocess.run(
                ['python3', hose_script],
                capture_output=True,
                text=True,
                timeout=60
            )
            if hose_result.returncode == 0:
                all_results['sources']['hose'] = json.loads(hose_result.stdout)
            else:
                all_results['sources']['hose'] = {'status': 'error', 'message': hose_result.stderr}
        except Exception as e:
            all_results['sources']['hose'] = {'status': 'error', 'message': str(e)}

        return jsonify(all_results), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'VPS Automation API Wrapper',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/endpoints', methods=['GET'])
def endpoints():
    """List available endpoints"""
    return jsonify({
        'endpoints': [
            {
                'method': 'GET/POST',
                'path': '/api/fetch-vsd',
                'description': 'Fetch all bonds from VSD latest date with detailed info',
                'notes': 'No parameters needed - returns all security codes updated on latest date'
            },
            {
                'method': 'GET/POST',
                'path': '/api/fetch-hnx',
                'description': 'Fetch all bonds from HNX with detailed info',
                'notes': 'No parameters needed - returns all bonds with details'
            },
            {
                'method': 'GET/POST',
                'path': '/api/fetch-hose',
                'description': 'Fetch all certificates/bonds from HOSE with detailed info',
                'notes': 'No parameters needed - returns all securities with details'
            },
            {
                'method': 'GET/POST',
                'path': '/api/fetch-all-sources',
                'description': 'Fetch from all three sources (VSD, HNX, HOSE) and combine',
                'notes': 'Runs all three fetchers and merges results'
            },
            {
                'method': 'GET',
                'path': '/health',
                'description': 'Health check'
            }
        ]
    }), 200

if __name__ == '__main__':
    print("🚀 Starting VPS Automation API Wrapper...")
    print("📍 Server running at: http://localhost:4000")
    print("\n📋 Available Endpoints:")
    print("  GET  /api/fetch-vsd - Fetch all bonds from VSD (latest date)")
    print("  GET  /api/fetch-hnx - Fetch all bonds from HNX")
    print("  GET  /api/fetch-hose - Fetch all certificates from HOSE")
    print("  GET  /api/fetch-all-sources - Fetch from all three sources")
    print("  GET  /health - Health check")
    print("  GET  /api/endpoints - List endpoints")
    print("\n⚠️  Keep this server running for N8n workflow to work\n")

    app.run(host='0.0.0.0', port=4000, debug=False)
