import pytest
import sys
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

# Ensure the application path is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test if the app initializes correctly
def test_app_initialization(dash_duo):
    """Test if the application loads properly"""
    app = import_app("app")
    dash_duo.start_server(app)
    
    # Check if the title is present
    assert dash_duo.wait_for_element("h2").text == "Remote OpenFAST Plotter"
    
    # Check if main components are loaded
    dash_duo.wait_for_element("#file-paths-input")
    dash_duo.wait_for_element("#load-files-btn")

# Test UI components
def test_ui_components(dash_duo):
    """Test if UI components are properly rendered"""
    app = import_app("app")
    dash_duo.start_server(app)
    
    # Check file input area
    file_input = dash_duo.wait_for_element("#file-paths-input")
    assert file_input is not None
    
    # Check load button
    load_button = dash_duo.wait_for_element("#load-files-btn")
    assert load_button is not None
    assert load_button.text == "Load Files"
    
    # Check clear button
    clear_button = dash_duo.wait_for_element("#clear-files-btn")
    assert clear_button is not None
    assert clear_button.text == "Clear All"

# Test if FFT annotation features are available
def test_fft_annotation_ui(dash_duo):
    """Test if FFT annotation UI components are properly rendered"""
    app = import_app("app")
    dash_duo.start_server(app)
    
    # Switch to FFT tab
    tabs = dash_duo.find_element("#tabs")
    fft_tab = dash_duo.find_element("[data-value='tab-fft']")  # Tab button
    fft_tab.click()
    
    # Check if annotation input is present
    dash_duo.wait_for_element("#fft-annotation-freq")
    freq_input = dash_duo.find_element("#fft-annotation-freq")
    assert freq_input is not None
    
    # Check if label input is present
    label_input = dash_duo.find_element("#fft-annotation-text")
    assert label_input is not None
    
    # Check if add button is present
    add_button = dash_duo.find_element("#fft-add-annotation-btn")
    assert add_button is not None
    assert add_button.text == "Add"
    
    # Check if annotation display area exists
    display_area = dash_duo.find_element("#fft-annotations-display")
    assert display_area is not None

# Enhanced test for FFT annotation features
def test_fft_annotation_interaction(dash_duo):
    """Test interactive features of the FFT annotation system"""
    app = import_app("app")
    dash_duo.start_server(app)
    
    # Switch to FFT tab
    tabs = dash_duo.find_element("#tabs")
    fft_tab = dash_duo.find_element("[data-value='tab-fft']")
    fft_tab.click()
    
    # Get input elements
    freq_input = dash_duo.find_element("#fft-annotation-freq")
    label_input = dash_duo.find_element("#fft-annotation-text")
    add_button = dash_duo.find_element("#fft-add-annotation-btn")
    display_area = dash_duo.find_element("#fft-annotations-display")
    
    # Enter values
    freq_input.send_keys("1.5, 3.0")
    label_input.send_keys("Tower, 3P")
    
    # Add annotations
    add_button.click()
    
    # Wait for badges to appear
    dash_duo.wait_for_text_to_equal("#fft-annotations-display", lambda x: "Tower" in x and "3P" in x)
    
    # Verify badges were created
    badges = dash_duo.find_elements(".badge")
    badge_texts = [badge.text for badge in badges if badge.is_displayed()]
    
    # Check that our annotations are in the displayed badges
    annotations_found = any("Tower: 1.5" in text for text in badge_texts)
    assert annotations_found, f"Expected 'Tower: 1.5' in badge texts, but got {badge_texts}"
    
    # Try adding more annotations
    freq_input.clear()
    freq_input.send_keys("0.33")
    label_input.clear()
    label_input.send_keys("1P")
    add_button.click()
    
    # Wait for updated badges
    dash_duo.wait_for_text_to_equal("#fft-annotations-display", lambda x: "1P" in x)
    
    # Check badges again - should now include the new one
    badges = dash_duo.find_elements(".badge")
    badge_texts = [badge.text for badge in badges if badge.is_displayed()]
    
    # Verify the new annotation is included and they are sorted
    assert len(badge_texts) >= 3, "Should have at least 3 annotation badges"
    
    # Optional: Test removing annotations
    # This is more complex as it requires clicking on dynamic elements
    # and would need special handling for the pattern-matching selectors
