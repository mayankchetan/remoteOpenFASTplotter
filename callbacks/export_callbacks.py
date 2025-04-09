"""
Export callbacks for OpenFAST Plotter
Contains callbacks for exporting plots as HTML
"""

import os
import datetime
import pandas as pd
import plotly.graph_objects as go

from dash import Input, Output, State
from dash.exceptions import PreventUpdate

# Import local modules
from data_manager import DATAFRAMES
from utils import draw_graph


def register_export_callbacks(app):
    """Register export callbacks with the Dash app"""
    
    # Export plot to HTML
    @app.callback(
        Output("download-html", "data"),
        Input("export-plot-btn", "n_clicks"),
        State("current-figure", "data"),
        State("current-plot-data", "data"),
        prevent_initial_call=True
    )
    def download_plot_html(export_clicks, current_fig, plot_data):
        """
        Generate and download an HTML file of the current plot.
        
        This function:
        1. Uses the current figure if available
        2. Regenerates the figure from plot data if needed
        3. Creates a standalone HTML file with the plot
        4. Returns the file for download
        """
        if not export_clicks:
            raise PreventUpdate

        # Use the current figure if available, otherwise generate it
        if current_fig:
            # Use the existing figure, no need to regenerate
            fig = go.Figure(current_fig)
        else:
            # Fall back to regenerating the figure if needed
            if not plot_data:
                raise PreventUpdate
            
            # Extract plot configuration
            file_paths = plot_data.get("file_paths", [])
            signalx = plot_data.get("signalx")
            signaly = plot_data.get("signaly", [])
            plot_option = plot_data.get("plot_option", "overlay")
            start_time = plot_data.get("start_time")
            end_time = plot_data.get("end_time")
            
            if not file_paths or not signalx or not signaly:
                raise PreventUpdate
            
            # Apply time range filtering to DataFrames
            filtered_dfs = []
            valid_paths = []
            for file_path in file_paths:
                if file_path in DATAFRAMES:
                    df = DATAFRAMES[file_path].copy()
                    
                    # Apply time filtering if specified
                    if start_time is not None or end_time is not None:
                        mask = pd.Series(True, index=df.index)
                        if start_time is not None:
                            mask = mask & (df[signalx] >= start_time)
                        if end_time is not None:
                            mask = mask & (df[signalx] <= end_time)
                        df = df[mask]
                    
                    if not df.empty:
                        filtered_dfs.append(df)
                        valid_paths.append(file_path)
            
            if not filtered_dfs:
                raise PreventUpdate
            
            if plot_option == "overlay" or len(valid_paths) == 1:
                fig = draw_graph(valid_paths, filtered_dfs, signalx, signaly, "overlay")
            else:
                # For separate plots, use first file for the export
                fig = draw_graph([valid_paths[0]], [filtered_dfs[0]], signalx, signaly, "separate")
        
        # Generate the HTML content
        html_str = fig.to_html(include_plotlyjs='cdn')
        
        # Create timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"openfast_plot_{timestamp}.html"
        
        # Return the content as a download
        return dict(
            content=html_str,
            filename=filename
        )
    
    # Export FFT plot as HTML with enhanced details
    @app.callback(
        Output("download-fft-html", "data"),
        Input("export-fft-btn", "n_clicks"),
        State("current-fft-figure", "data"),
        State("signalx", "value"),
        State("signaly", "value"),
        State("time-start", "value"),
        State("time-end", "value"),
        State("fft-averaging", "value"),
        State("fft-windowing", "value"),
        State("fft-n-exp", "value"),
        State("fft-detrend", "value"),
        State("fft-x-limit", "value"),
        State("fft-xscale", "value"),
        State("fft-annotations", "data"),
        prevent_initial_call=True
    )
    def download_fft_html(export_clicks, current_fig, signalx, signaly, time_start, time_end, 
                         averaging, windowing, n_exp, detrend, x_limit, xscale, annotations):
        """
        Generate and download an HTML file of the current FFT plot
        with detailed settings and annotations.
        """
        if not export_clicks or current_fig is None:
            raise PreventUpdate
        
        # Use the stored figure
        fig = go.Figure(current_fig)
            
        # Create timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"openfast_fft_{timestamp}.html"
        
        # Create detailed settings table
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
        
        # Add annotations if available
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
        
        # Generate the HTML with the figure and settings
        fig_html = fig.to_html(include_plotlyjs='cdn')
        
        # Insert settings after the plot
        split_point = fig_html.find('</body>')
        if split_point > 0:
            html_str = fig_html[:split_point] + settings_html + fig_html[split_point:]
        else:
            html_str = fig_html + settings_html
        
        return dict(
            content=html_str,
            filename=filename
        )
