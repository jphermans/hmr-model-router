#!/usr/bin/env python3
"""OpenRouter Daily Monitor - Cron Job Script"""

import subprocess
import os

# Run the pricing check and report generation
os.chdir("/home/jphermans/hmr-model-router")

# Fetch latest pricing and generate report
result = subprocess.run(
    ["python3", "generate_daily_report.py"],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.returncode != 0:
    print(f"ERROR: {result.stderr}")
