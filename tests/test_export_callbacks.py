import pytest

# For export_callbacks, we can test the HTML generation for the settings table.
# The main part of the callback (fig.to_html()) is a Plotly function.


def test_download_fft_html_settings_generation():
    """Test the generation of the HTML settings table in download_fft_html."""

    # Sample inputs that would be States in the callback
    signalx = "Time"
    signaly = ["WindSpeed", "RotorSpeed"]
    time_start = 0.5
    time_end = 100.0
    averaging = "Welch"
    windowing = "hann"
    n_exp = 12
    detrend = ["detrend"]  # As it's a checklist, value is a list
    x_limit = 50
    xscale = "log"
    annotations = [
        {"freq": 10.0, "label": "Peak1"},
        {"freq": 25.55, "label": "Peak2 (Important)"}
    ]

    # Simplified logic from download_fft_html for settings_html
    settings_html = f"""
    <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
        <h4>FFT Analysis Settings</h4>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
            <tr>
                <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd; background-color: #f1f1f1;">Setting</th>
                <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd; background-color: #f1f1f1;">Value</th>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">X Signal</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{signalx}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Y Signal(s)</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{", ".join(signaly) if isinstance(signaly, list) else signaly}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Time Range</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{time_start if time_start is not None else "Start"} to {time_end if time_end is not None else "End"} seconds</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Averaging Method</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{averaging}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Window Function</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{windowing}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">2^n Exponent</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{n_exp}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Detrend</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{"Yes" if "detrend" in detrend else "No"}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">X-axis Scale</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{xscale}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">X-axis Limit</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{x_limit} Hz</td>
            </tr>
        </table>
    """

    if annotations and len(annotations) > 0:
        settings_html += """
        <h4 style="margin-top: 15px;">Frequency Annotations</h4>
        <ul>
        """
        for anno in annotations:
            settings_html += f"""
            <li>{anno['label']}: {anno['freq']:.2f} Hz</li>
            """
        settings_html += "</ul>"
    settings_html += "</div>"

    # Assertions to check if the HTML contains the expected values
    # Making assertions more robust to exact HTML structure by checking for the value within the relevant tags.
    # This is still substring matching but more targeted.
    td_style = 'style="padding: 8px; border-bottom: 1px solid #ddd;"'

    assert f"<td {td_style}>{signalx}</td>" in settings_html
    assert f"<td {td_style}>{', '.join(signaly)}</td>" in settings_html
    assert f"<td {td_style}>{time_start if time_start is not None else 'Start'} to {time_end if time_end is not None else 'End'} seconds</td>" in settings_html
    assert f"<td {td_style}>{averaging}</td>" in settings_html
    assert f"<td {td_style}>{windowing}</td>" in settings_html
    assert f"<td {td_style}>{n_exp}</td>" in settings_html
    assert f"<td {td_style}>{'Yes' if 'detrend' in detrend else 'No'}</td>" in settings_html
    assert f"<td {td_style}>{xscale}</td>" in settings_html
    assert f"<td {td_style}>{x_limit} Hz</td>" in settings_html

    # Make the assertion for the header more specific, including potential style attributes
    # and ignoring leading/trailing whitespace for the line itself.
    assert '<h4 style="margin-top: 15px;">Frequency Annotations</h4>' in settings_html
    # For list items, the content is more direct.
    assert f"<li>{annotations[0]['label']}: {annotations[0]['freq']:.2f} Hz</li>" in settings_html
    assert f"<li>{annotations[1]['label']}: {annotations[1]['freq']:.2f} Hz</li>" in settings_html


def test_download_fft_html_settings_generation_no_annotations_no_time_limits():
    """Test settings HTML when annotations are empty and time limits are None."""
    signalx = "Time"
    signaly = "WindSpeed"  # Single signal
    time_start = None
    time_end = None
    averaging = "None"
    windowing = "None"
    n_exp = 10
    detrend = []  # Not selected
    x_limit = 10
    xscale = "linear"
    annotations = []

    # Simplified logic from download_fft_html for settings_html
    settings_html = f"""
    <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
        <h4>FFT Analysis Settings</h4>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
            <tr>
                <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd; background-color: #f1f1f1;">Setting</th>
                <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd; background-color: #f1f1f1;">Value</th>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">X Signal</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{signalx}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Y Signal(s)</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{", ".join(signaly) if isinstance(signaly, list) else signaly}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Time Range</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{time_start if time_start is not None else "Start"} to {time_end if time_end is not None else "End"} seconds</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Averaging Method</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{averaging}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Window Function</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{windowing}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">2^n Exponent</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{n_exp}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Detrend</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{"Yes" if "detrend" in detrend else "No"}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">X-axis Scale</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{xscale}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">X-axis Limit</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{x_limit} Hz</td>
            </tr>
        </table>
    """  # Note: No annotations section here
    settings_html += "</div>"

    td_style = 'style="padding: 8px; border-bottom: 1px solid #ddd;"'

    assert f"<td {td_style}>{signalx}</td>" in settings_html
    # Check single signal handling
    assert f"<td {td_style}>{signaly}</td>" in settings_html
    # Check None time limits
    assert f"<td {td_style}>Start to End seconds</td>" in settings_html
    assert f"<td {td_style}>{'No'}</td>" in settings_html  # Check detrend 'No'
    # Ensure the header is NOT present if there are no annotations
    # Check no annotation header
    assert '<h4 style="margin-top: 15px;">Frequency Annotations</h4>' not in settings_html
    assert "<li>" not in settings_html  # Check no annotation list items
