#!/usr/bin/env python3
"""
Fix broken Prometheus metrics definitions in metrics.py
"""

import re


def fix_metrics_file():
    """Fix all broken metric definitions"""

    with open("app/monitoring/metrics.py", "r") as f:
        content = f.read()

    # Fix pattern: MetricType() \n "name", \n "description" \n ["labels"], -> MetricType("name", "description", ["labels"],

    # Pattern 1: Counter() with args on next lines
    pattern1 = r'(\w+) = Counter\(\)\s*\n\s*"([^"]+)",\s*\n\s*"([^"]+)"\s*\n\s*(\[[^\]]+\]),\s*\n\s*registry=self\.registry,\s*\n\s*\)'
    replacement1 = r'\1 = Counter(\n            "\2",\n            "\3",\n            \4,\n            registry=self.registry,\n        )'
    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)

    # Pattern 2: Histogram() with args on next lines
    pattern2 = r'(\w+) = Histogram\(\)\s*\n\s*"([^"]+)",\s*\n\s*"([^"]+)"\s*\n\s*(\[[^\]]+\]),\s*\n\s*registry=self\.registry,\s*\n\s*\)'
    replacement2 = r'\1 = Histogram(\n            "\2",\n            "\3",\n            \4,\n            registry=self.registry,\n        )'
    content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)

    # Pattern 3: Gauge() with args on next lines
    pattern3 = r'(\w+) = Gauge\(\)\s*\n\s*"([^"]+)",\s*\n\s*"([^"]+)"\s*\n\s*(\[[^\]]+\]),\s*\n\s*registry=self\.registry,\s*\n\s*\)'
    replacement3 = r'\1 = Gauge(\n            "\2",\n            "\3",\n            \4,\n            registry=self.registry,\n        )'
    content = re.sub(pattern3, replacement3, content, flags=re.MULTILINE)

    # Pattern 4: Summary() with args on next lines
    pattern4 = r'(\w+) = Summary\(\)\s*\n\s*"([^"]+)",\s*\n\s*"([^"]+)"\s*\n\s*(\[[^\]]+\]),\s*\n\s*registry=self\.registry,\s*\n\s*\)'
    replacement4 = r'\1 = Summary(\n            "\2",\n            "\3",\n            \4,\n            registry=self.registry,\n        )'
    content = re.sub(pattern4, replacement4, content, flags=re.MULTILINE)

    # Fix broken docstrings: ""text"" -> """text"""
    content = re.sub(r'""([^"]*?)""', r'"""\1"""', content)

    # Fix missing commas in descriptions: "description" \n ["labels"] -> "description", \n ["labels"]
    content = re.sub(
        r'"([^"]+)"\s*\n\s*(\[[^\]]+\])', r'"\1",\n            \2', content
    )

    with open("app/monitoring/metrics.py", "w") as f:
        f.write(content)

    print("Fixed metrics.py file")


if __name__ == "__main__":
    fix_metrics_file()
