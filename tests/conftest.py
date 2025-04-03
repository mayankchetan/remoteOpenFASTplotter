"""
Pytest configuration file.
This file contains shared fixtures and configuration for tests.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow importing from app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Define common fixtures here
import pytest
import glob

@pytest.fixture
def test_files():
    """Find test files in the test_files directory"""
    test_file_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_files")
    outb_files = glob.glob(os.path.join(test_file_dir, "*.outb"))
    
    if not outb_files:
        pytest.skip("No test files found. Run 'python utils/download_test_files.py' first.")
    
    return outb_files
