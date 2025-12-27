########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\apps\flowork_architect\backend\parsers\py.py total lines 116 
########################################################################

import re
import ast
from .base import BaseParser

class PythonParser(BaseParser):
    """
    SPECIALIST PARSER FOR PYTHON FILES (.py)
    Capabilities:
    1. AST Analysis for Imports, Classes, and Functions.
    2. Genealogy Mapping (Class Inheritance).
    3. Security Scanning (Secret Hunter).
    """

    def __init__(self):
        super().__init__() # Ensure base attributes are loaded
        self.color = "#3572A5"  # Python Blue
        self.icon = "f3e2"      # Python Icon
        self.priority = 100     # High priority for specific matcher

    def supports(self, filename, ext):
        return ext == "py"

    def parse(self, content, path):
        """
        Main parsing logic using Abstract Syntax Tree (AST).
        """
        imports = set()
        structure = []

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        target = n.name.split('.')[-1]
                        imports.add(target)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        target = node.module.split('.')[-1]
                        imports.add(target)

                elif isinstance(node, ast.ClassDef):
                    bases = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            bases.append(base.id)
                        elif isinstance(base, ast.Attribute):
                            bases.append(base.attr)

                    structure.append({
                        "name": node.name,
                        "type": "class",
                        "line": node.lineno,
                        "icon": "fa-cube",
                        "bases": bases
                    })

                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("__"):
                        structure.append({
                            "name": node.name,
                            "type": "def",
                            "line": node.lineno,
                            "icon": "fa-code"
                        })
        except:
            pass

        security_risks = self.scan_for_secrets(content)

        return {
            "imports": list(imports),
            "assets": [],
            "structure": structure,
            "metrics": self.analyze_vital_signs(content, security_risks)
        }

    def scan_for_secrets(self, content):
        """
        THE SECRET HUNTER
        Scans for potential hardcoded secrets using regex patterns.
        """
        risks = []
        patterns = {
            "OpenAI Key": r"sk-[a-zA-Z0-9]{32,}",
            "GitHub Token": r"ghp_[a-zA-Z0-9]{30,}",
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "Generic Secret": r"(?i)(api_key|secret_key|password|token)\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]"
        }

        for name, pattern in patterns.items():
            if re.search(pattern, content):
                risks.append(f"Potential {name} detected")

        return risks

    def analyze_vital_signs(self, content, security_risks):
        metrics = super().analyze_vital_signs(content)

        metrics['security_risks'] = security_risks

        danger_count = len(re.findall(r'"""[\s\S]*?DANGER[\s\S]*?"""', content))

        if len(security_risks) > 0:
            metrics['complexity'] = "CRITICAL"
        elif danger_count > 0:
            metrics['complexity'] = "HIGH"

        return metrics
