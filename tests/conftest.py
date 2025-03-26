"""
Pytest configuration file.
This file contains shared fixtures and configuration for tests.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow importing from app.py
# This is crucial for tests to be able to import the main module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Define common fixtures here if needed
