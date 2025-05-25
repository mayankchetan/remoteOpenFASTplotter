import pytest
import plotly.graph_objects as go
import datetime

# Import from html_exporter.py in the root directory
from html_exporter import export_figures_from_plotly_objects

# Default metadata for testing
DEFAULT_METADATA = {
    "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "system": "TestSystem",
    "user": "TestUser",
    "version": "1.0.0"
}


def create_simple_figure(title="Sample Plot"):
    """Helper function to create a simple Plotly figure."""
    return go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[2, 1, 3])], layout=go.Layout(
        title=go.layout.Title(text=title)))


def test_html_export_single_plot(tmp_path):
    """Test exporting a single Plotly figure to HTML."""
    output_path = tmp_path / "single_plot_export.html"
    figs = [create_simple_figure(title="My Single Plot")]
    page_title = "Single Plot Test"

    html_content = export_figures_from_plotly_objects(
        figs, DEFAULT_METADATA, title=page_title, plot_type="Test Plot")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Verify the file exists
    assert output_path.exists()

    # Read content and perform checks
    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()

        # Check for page title
        assert f"<title>{page_title}</title>" in content

        # Check for metadata
        assert DEFAULT_METADATA["datetime"] in content
        assert DEFAULT_METADATA["system"] in content
        assert DEFAULT_METADATA["user"] in content
        assert DEFAULT_METADATA["version"] in content
        assert "Test Plot" in content  # plot_type

        # Check for plot container (assuming one plot)
        assert 'id="plot-0"' in content
        # Check for the plot's actual title within the JSON data
        expected_title_text = "MySinglePlot"

        # Find the script block for plot-0
        script_tag_start = content.find(
            f"<script type=\"text/javascript\">",
            content.find(f"id=\"plot-0\""))
        script_tag_end = content.find("</script>", script_tag_start)
        script_content = ""
        if script_tag_start != -1 and script_tag_end != -1:
            script_content = content[script_tag_start:script_tag_end]

        # Find 'var figure = {...};' within this script block
        var_figure_start = script_content.find("var figure = {")
        var_figure_end = -1
        if var_figure_start != -1:
            # Find the matching closing brace for the figure JSON
            open_braces = 0
            for k in range(
                    var_figure_start +
                    len("var figure = "),
                    len(script_content)):
                if script_content[k] == '{':
                    open_braces += 1
                elif script_content[k] == '}':
                    open_braces -= 1
                    if open_braces == - \
                            1:  # Started with '{', so first one makes it 0, second one makes it -1
                        var_figure_end = k + 1
                        break

        figure_json_str = ""
        if var_figure_start != -1 and var_figure_end != -1:
            figure_json_str = script_content[var_figure_start +
                                             len("var figure = "):var_figure_end]

        assert f'"text":"{expected_title_text}"' in figure_json_str.replace(
            " ",
            "").replace(
            "\\n",
            "")
        assert "Plotly.newPlot('plot-0'" in content


def test_html_export_zero_plots(tmp_path):
    """Test exporting HTML when there are no figures."""
    output_path = tmp_path / "zero_plots_export.html"
    figs = []
    page_title = "Zero Plots Test"

    html_content = export_figures_from_plotly_objects(
        figs, DEFAULT_METADATA, title=page_title, plot_type="No Plots Test")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    assert output_path.exists()

    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert f"<title>{page_title}</title>" in content
        # Metadata should still be there
        assert DEFAULT_METADATA["user"] in content
        assert "No Plots Test" in content  # plot_type

        # Check that no plot divs are created
        assert 'id="plot-0"' not in content
        assert "Plotly.newPlot" not in content  # No plotting script calls beyond setup


def test_html_export_multiple_plots(tmp_path):
    """Test exporting multiple Plotly figures to HTML."""
    output_path = tmp_path / "multiple_plots_export.html"
    num_plots = 3
    figs = [
        create_simple_figure(
            title=f"Plot Number {i+1}") for i in range(num_plots)]
    page_title = "Multiple Plots Test"

    html_content = export_figures_from_plotly_objects(
        figs, DEFAULT_METADATA, title=page_title, plot_type="Multi-Plot Test")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    assert output_path.exists()

    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert f"<title>{page_title}</title>" in content
        assert DEFAULT_METADATA["version"] in content
        assert "Multi-Plot Test" in content  # plot_type

        for i in range(num_plots):
            assert f'id="plot-{i}"' in content, f"Div for plot {i} not found."
            assert f"Plotly.newPlot('plot-{i}'" in content, f"Plotly call for plot {i} not found."

            expected_title_text = f"PlotNumber{i+1}"

            # Find the script block for plot-i
            # Search for the script tag that appears *after* the div for plot-i
            plot_div_pos = content.find(f'id="plot-{i}"')
            script_tag_start = content.find(
                f"<script type=\"text/javascript\">", plot_div_pos)
            script_tag_end = content.find("</script>", script_tag_start)
            script_content = ""
            if script_tag_start != -1 and script_tag_end != -1:
                script_content = content[script_tag_start:script_tag_end]

            var_figure_start = script_content.find("var figure = {")
            var_figure_end = -1
            if var_figure_start != -1:
                open_braces = 0
                for k in range(
                        var_figure_start +
                        len("var figure = "),
                        len(script_content)):
                    if script_content[k] == '{':
                        open_braces += 1
                    elif script_content[k] == '}':
                        open_braces -= 1
                        if open_braces == -1:
                            var_figure_end = k + 1
                            break

            figure_json_str = ""
            if var_figure_start != -1 and var_figure_end != -1:
                figure_json_str = script_content[var_figure_start +
                                                 len("var figure = "):var_figure_end]

            assert f'"text":"{expected_title_text}"' in figure_json_str.replace(
                " ", "").replace("\\n", "")


def test_html_export_different_metadata_and_title(tmp_path):
    """Test exporting with different metadata and title."""
    output_path = tmp_path / "custom_meta_export.html"
    figs = [create_simple_figure()]

    custom_metadata = {
        "datetime": "2023-01-01 10:00:00",
        "system": "Production Server",
        "user": "Admin User",
        "version": "2.5.1"
    }
    custom_page_title = "Custom Report Title"
    custom_plot_type = "Custom Analysis"

    html_content = export_figures_from_plotly_objects(
        figs, custom_metadata, title=custom_page_title, plot_type=custom_plot_type)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    assert output_path.exists()

    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert f"<title>{custom_page_title}</title>" in content
        assert custom_metadata["datetime"] in content
        assert custom_metadata["system"] in content
        assert custom_metadata["user"] in content
        assert custom_metadata["version"] in content
        assert custom_plot_type in content
        assert 'id="plot-0"' in content  # Ensure the plot is still there

# The original test_html_export from the prompt used a different function signature.
# This version adapts to the identified html_exporter.py (root)
# The old `tools.html_export.export_to_html` took `data` as a dict with 'title' and 'plots' (list of html strings)
# The new `html_exporter.export_figures_from_plotly_objects` takes a list of actual Plotly figures.
# If `tools.html_export.py` is still meant to be used and tested, its tests should be separate.
# For now, focusing on the more complex html_exporter.py from root.
#
# def test_original_style_export_if_needed(tmp_path):
#     """ If tools.html_export.export_to_html is also to be tested. """
#     from tools.html_export import export_to_html as export_simple_html
#     output_path = tmp_path / "simple_export.html"
#     mock_data = {"title": "Simple Test Export", "plots": ["<div>Plot 1 HTML</div>", "<div>Plot 2 HTML</div>"]}
#     export_simple_html(mock_data, output_path)
#     assert output_path.exists()
#     with open(output_path, "r") as f:
#         content = f.read()
#         assert "Simple Test Export" in content
#         assert "<div>Plot 1 HTML</div>" in content
#         assert "<div>Plot 2 HTML</div>" in content
