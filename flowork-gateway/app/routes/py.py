########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-gateway\app\routes\py.py total lines 37 
########################################################################

import os
import sys
import logging
import requests
from flask import Blueprint, jsonify

spy_bp = Blueprint('spy', __name__)
logger = logging.getLogger(__name__)

CORE_INTERNAL_URL = os.getenv("FLOWORK_CORE_INTERNAL_URL", "http://flowork_core:8989")

@spy_bp.route('/check', methods=['GET'])
def run_diagnostics():
    report = {
        "status": "scanning",
        "tests": {}
    }

    try:
        import requests
        report['tests']['library_requests'] = f"OK ({requests.__version__})"
    except ImportError:
        report['tests']['library_requests'] = "MISSING"

    try:
        resp = requests.get(f"{CORE_INTERNAL_URL}/health", timeout=3)
        report['tests']['core_connection'] = f"OK ({resp.status_code})"
    except Exception as e:
        report['tests']['core_connection'] = f"FAIL: {str(e)}"

    return jsonify(report)
