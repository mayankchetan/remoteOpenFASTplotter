"""
Module for exporting plots and data to HTML.
"""

def export_to_html(data, output_path):
    """Export data to an HTML file."""
    with open(output_path, "w") as f:
        f.write(f"<html><head><title>{data['title']}</title></head><body>")
        for plot in data["plots"]:
            f.write(plot)
        f.write("</body></html>")
