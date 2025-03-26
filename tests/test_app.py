import pytest
from dash.testing.application_runners import import_app
from dash.testing.composite import DashComposite

# Initialize tests using pytest-dash
@pytest.fixture
def dash_duo():
    with DashComposite() as dc:
        yield dc

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
