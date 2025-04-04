"""
Tests that use actual OpenFAST files downloaded by the utility.
These tests ensure that the app can properly load and display real data.
"""

import pytest
import os
import glob
from pathlib import Path

# Check if dash testing components are available
try:
    from dash.testing.application_runners import import_app
    from dash.testing.composite import DashComposite
    DASH_TESTING_AVAILABLE = True
except ImportError:
    DASH_TESTING_AVAILABLE = False

# Skip all tests in this module if dash testing is not available
pytestmark = pytest.mark.skipif(not DASH_TESTING_AVAILABLE, 
                              reason="Dash testing components not available. Install psutil to enable.")

# Initialize tests using pytest-dash
@pytest.fixture
def dash_duo():
    with DashComposite() as dc:
        yield dc

# Fixture to find test files
@pytest.fixture
def test_files():
    """Find test files in the test_files directory"""
    test_file_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_files")
    outb_files = glob.glob(os.path.join(test_file_dir, "*.outb"))
    
    if not outb_files:
        pytest.skip("No test files found. Run 'python utils/download_test_files.py' first.")
    
    return outb_files

# Test loading real files
def test_load_real_files(dash_duo, test_files):
    """Test if the application can load real OpenFAST files"""
    app = import_app("app")
    dash_duo.start_server(app)
    
    # Enter file paths into the textarea
    file_input = dash_duo.find_element("#file-paths-input")
    file_input.send_keys("\n".join(test_files))
    
    # Click load button
    load_button = dash_duo.find_element("#load-files-btn")
    load_button.click()
    
    # Wait for files to load
    dash_duo.wait_for_element("#loaded-files-count")
    
    # Check that the file count matches
    file_count_badge = dash_duo.find_element("#loaded-files-count")
    assert file_count_badge.text == str(len(test_files))
    
    # Check that the file pills container has content
    file_pills = dash_duo.find_element("#loaded-files-pills")
    assert file_pills.text != ""

# Test plotting with real files
def test_plot_real_files(dash_duo, test_files):
    """Test if the application can create plots from real OpenFAST files"""
    app = import_app("app")
    dash_duo.start_server(app)
    
    # Enter file paths into the textarea
    file_input = dash_duo.find_element("#file-paths-input")
    file_input.send_keys("\n".join(test_files))
    
    # Click load button
    load_button = dash_duo.find_element("#load-files-btn")
    load_button.click()
    
    # Wait for signals to be populated
    dash_duo.wait_for_element("#signalx")
    dash_duo.wait_for_element("#signaly")
    
    # Wait for plot button to be clickable
    plot_button = dash_duo.wait_for_element("#plot-btn")
    
    # Click plot button
    plot_button.click()
    
    # Wait for plot to appear
    dash_duo.wait_for_element(".js-plotly-plot")
    
    # Verify the plot exists
    plot = dash_duo.find_element(".js-plotly-plot")
    assert plot is not None

def test_invalid_file_inputs(dash_duo):
    """Test handling of invalid file paths and unsupported formats."""
    app = import_app("app")
    dash_duo.start_server(app)

    # Enter invalid file paths
    file_input = dash_duo.find_element("#file-paths-input")
    file_input.send_keys("/invalid/path/to/file.outb\nunsupported_file.txt")

    # Click load button
    load_button = dash_duo.find_element("#load-files-btn")
    load_button.click()

    # Check for error message
    error_message = dash_duo.wait_for_element("#error-message")
    assert "Invalid file path" in error_message.text or "Unsupported file format" in error_message.text
