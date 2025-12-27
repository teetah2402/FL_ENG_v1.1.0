########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\utils\flowchain_verifier.py total lines 46 
########################################################################

import json
import hashlib
import os
import logging


def calculate_hash(file_path):
    """
    Simple SHA256 hash for internal integrity checks.
    Does NOT require web3.
    """
    sha256 = hashlib.sha256()
    try:
        if isinstance(file_path, str) and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            return sha256.hexdigest()

        if isinstance(file_path, dict):
            encoded = json.dumps(file_path, sort_keys=True).encode()
        else:
            encoded = str(file_path).encode()
        return hashlib.sha256(encoded).hexdigest()

    except Exception as e:
        logging.error(f"[Verifier] Error calculating hash: {e}")
        return None

def verify_workflow_chain(workflow_directory):
    """
    [LITE MODE STUB]
    Always returns True to bypass blockchain verification on Edge devices.
    In the full Enterprise version, this would verify the chain integrity via Web3.
    """
    if not os.path.isdir(workflow_directory):
        print(f"[Verifier] Lite Mode Warning: Directory not found: {workflow_directory}")
        return True, "Lite Mode: Directory check bypassed."

    return True, "Lite Mode: Chain verification bypassed successfully."
