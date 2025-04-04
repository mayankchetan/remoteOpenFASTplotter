import os
import pytest
from tools.html_export import export_to_html

def test_html_export(tmp_path):
    """Test the HTML export feature."""
    output_path = tmp_path / "test_export.html"

    # Mock data for export
    mock_data = {"title": "Test Export", "plots": ["<div>Plot 1</div>", "<div>Plot 2</div>"]}

    # Export to HTML
    export_to_html(mock_data, output_path)

    # Verify the file exists and contains expected content
    assert output_path.exists()
    with open(output_path, "r") as f:
        content = f.read()
        assert "Test Export" in content
        assert "<div>Plot 1</div>" in content
        assert "<div>Plot 2</div>" in content
