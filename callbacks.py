"""
Callbacks for OpenFAST Plotter
Contains all application callbacks for interactivity
"""

import os
import sys
import datetime
import traceback
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.colors
import uuid

from dash import Input, Output, State, html, dcc, ctx, ALL, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc  # Add this import for dbc

# Import local modules
from data_manager import DATAFRAMES, store_dataframes, get_file_info, remove_file
from utils import draw_graph, create_file_pills, create_annotation_badges, get_unique_identifiers
# Import new user preferences module
from user_preferences import (load_preferences, update_recent_files, update_favorite_signals, 
                            save_fft_settings, save_custom_annotations, save_plot_settings)

# Import FFT analysis module
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))
from tools.fft_analysis import compute_fft

def register_callbacks(app):
    """
    Register all callbacks with the Dash app
    
    Parameters:
    -----------
    app : dash.Dash
        The Dash application instance
    """
    
    # Initialize and load user preferences when app starts
    @app.callback(
        Output("fft-annotations", "data", allow_duplicate=True),
        Output("fft-annotations-display", "children", allow_duplicate=True),
        Output("fft-averaging", "value", allow_duplicate=True),
        Output("fft-windowing", "value", allow_duplicate=True),
        Output("fft-n-exp", "value", allow_duplicate=True),
        Output("fft-plot-style", "value", allow_duplicate=True),
        Output("fft-detrend", "value", allow_duplicate=True),
        Output("fft-xscale", "value", allow_duplicate=True),
        Output("fft-x-limit", "value", allow_duplicate=True),
        Output("plot-option", "value", allow_duplicate=True),
        Input("plot-metadata", "data"),  # Use the metadata store as a trigger on app start
        prevent_initial_call=True
    )
    def initialize_from_preferences(metadata):
        """Initialize app settings from saved user preferences"""
        prefs = load_preferences()
        
        # Initialize FFT annotations
        annotations = prefs.get("custom_annotations", [])
        badges = create_annotation_badges(annotations)
        
        # Initialize FFT settings
        fft_settings = prefs.get("fft_settings", {})
        averaging = fft_settings.get("averaging", "Welch")
        windowing = fft_settings.get("windowing", "hamming")
        n_exp = fft_settings.get("n_exp", 15)
        plot_style = fft_settings.get("plot_style", "overlay")
        detrend = ["detrend"] if fft_settings.get("detrend", True) else []
        xscale = fft_settings.get("xscale", "linear")
        x_limit = fft_settings.get("x_limit", 5)
        
        # Initialize plot settings
        plot_settings = prefs.get("plot_settings", {})
        plot_option = plot_settings.get("plot_option", "overlay")
        
        return (annotations, badges, averaging, windowing, n_exp, plot_style, 
                detrend, xscale, x_limit, plot_option)
    
    #######################
    # UI AND LOADING CALLBACKS
    #######################
    
    # Show/Hide loading spinner
    @app.callback(
        Output("loading-container", "style"),
        Input("is-loading", "data")
    )
    def toggle_loading_spinner(is_loading):
        """Toggle the visibility of the loading spinner based on loading state."""
        if is_loading:
            return {"display": "block"}
        else:
            return {"display": "none"}

    # Background processing for file loading
    @app.callback(
        Output("is-loading", "data", allow_duplicate=True),
        Input("load-files-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def start_loading(n_clicks):
        """Set the loading state when the load button is clicked."""
        if n_clicks:
            return True
        return False
        
    # Toggle error details collapse
    @app.callback(
        Output("error-details-collapse", "is_open"),
        Input("error-details-button", "n_clicks"),
        State("error-details-collapse", "is_open"),
        prevent_initial_call=True
    )
    def toggle_error_details(n_clicks, is_open):
        """Toggle the visibility of the error details section."""
        return not is_open
            
    #######################
    # FILE LOADING CALLBACKS
    #######################
    
    # Main callback for loading files
    @app.callback(
        Output("loaded-files", "data"),
        Output("file-path-list", "data"),
        Output("file-loading-status", "children"),
        Output("file-paths-input", "value"),
        Output("loaded-files-pills", "children"),
        Output("loaded-files-count", "children"),
        Output("error-details-container", "style"),
        Output("error-details-button", "style"),
        Output("error-details-collapse", "children"),
        Output("is-loading", "data"),
        Output("time-range-info", "data"),
        Input("load-files-btn", "n_clicks"),
        Input("clear-files-btn", "n_clicks"),
        State("loaded-files", "data"),
        State("file-path-list", "data"),
        State("file-paths-input", "value"),
        prevent_initial_call=True
    )
    def load_files_from_input(load_clicks, clear_clicks, current_loaded_files, current_file_paths, file_paths_input):
        """
        Load files from input text area, avoiding reload of already loaded files.
        
        This callback handles:
        1. Loading new files when the "Load Files" button is clicked
        2. Clearing all loaded files when the "Clear All" button is clicked
        3. Displaying status messages and error details
        4. Creating file pills for visual representation of loaded files
        """
        
        trigger_id = ctx.triggered_id
        
        if trigger_id == "clear-files-btn":
            DATAFRAMES.clear()  # Clear the global dictionary
            return {}, [], html.Div("All files cleared"), "", html.Div(), "0", {"display": "none"}, {"display": "none"}, [], False, {}
        
        if not file_paths_input:
            current_files = current_loaded_files.get("files", [])
            return current_loaded_files, current_file_paths, html.Div("No file paths entered", style={"color": "red"}), "", create_file_pills(current_files), str(len(current_files)), {"display": "none"}, {"display": "none"}, [], False, {}
        
        # Get currently loaded files
        current_files = set(current_loaded_files.get("files", []))
        
        # Split input by newlines and filter out empty lines
        new_file_paths = [path.strip() for path in file_paths_input.split('\n') if path.strip()]
        
        if not new_file_paths:
            return current_loaded_files, current_file_paths, html.Div("No file paths entered", style={"color": "red"}), "", create_file_pills(current_files), str(len(current_files)), {"display": "none"}, {"display": "none"}, [], False, {}
        
        # Detect which files are new and need to be processed
        new_files_to_process = [f for f in new_file_paths if f not in current_files]
        
        if not new_files_to_process:
            return current_loaded_files, current_file_paths, html.Div("All files already loaded", style={"color": "blue"}), "", create_file_pills(current_files), str(len(current_files)), {"display": "none"}, {"display": "none"}, [], False, {}
        
        # Validate file paths
        valid_paths = []
        invalid_paths = []
        for path in new_files_to_process:
            if os.path.exists(path) and os.path.isfile(path):
                valid_paths.append(path)
            else:
                invalid_paths.append(path)
        
        # Load valid files in parallel
        if valid_paths:
            new_dfs, failed_files, load_times = store_dataframes(valid_paths)
            
            # Log loading times
            for file_path, elapsed in load_times.items():
                print(f"Loaded {os.path.basename(file_path)} in {elapsed:.2f} seconds")
            
            # Merge with existing data
            all_files = list(current_files) + list(new_dfs.keys())
            
            # Update the global DATAFRAMES dictionary with new DataFrames
            for path, df in new_dfs.items():
                DATAFRAMES[path] = df
            
            # Get list of files that failed to load
            failed_paths = [f[0] for f in failed_files]
            
            # Create status message
            status_elements = []
            
            if new_dfs:
                status_elements.append(
                    html.Span(f"✓ Loaded {len(new_dfs)} new files", style={"color": "green"})
                )
            
            if failed_paths:
                status_elements.append(
                    html.Span(f" | ⚠️ {len(failed_paths)} files failed to parse", style={"color": "red", "marginLeft": "10px"})
                )
            
            if invalid_paths:
                status_elements.append(
                    html.Span(f" | ⚠️ {len(invalid_paths)} files not found", style={"color": "red", "marginLeft": "10px"})
                )
            
            # Create error details content
            error_details = []
            has_errors = False
            if failed_files:
                has_errors = True
                for path, error in failed_files:
                    error_details.append(html.Div([
                        html.Small(f"• {os.path.basename(path)}: {error}", className="text-danger")
                    ]))
                
            if invalid_paths:
                has_errors = True
                for path in invalid_paths:
                    error_details.append(html.Div([
                        html.Small(f"• {path}: File not found", className="text-danger")
                    ]))
            
            # Create file pills for all loaded files
            pills = create_file_pills(all_files)
            
            # Set visibility based on whether we have errors
            error_container_style = {"display": "block"} if has_errors else {"display": "none"}
            error_button_style = {"display": "block"} if has_errors else {"display": "none"}
            
            # Determine time range from loaded files
            time_range_info = {}
            if all_files:
                for file_path in all_files:
                    if file_path in DATAFRAMES:
                        df = DATAFRAMES[file_path]
                        if 'Time' in df.columns or 'Time_[s]' in df.columns:
                            time_col = 'Time_[s]' if 'Time_[s]' in df.columns else 'Time'
                            min_time = df[time_col].min()
                            max_time = df[time_col].max()
                            if 'min_time' not in time_range_info or min_time < time_range_info['min_time']:
                                time_range_info['min_time'] = min_time
                            
                            if 'max_time' not in time_range_info or max_time > time_range_info['max_time']:
                                time_range_info['max_time'] = max_time
                
            # Update user preferences with successful files
            if new_dfs:
                update_recent_files(list(new_dfs.keys()))
                
            return (
                {"files": all_files},
                all_files,
                html.Div(status_elements),
                "",
                pills,
                str(len(all_files)),
                error_container_style,
                error_button_style,
                error_details,
                False,  # Loading done
                time_range_info
            )
        else:
            # No valid files to add
            return (
                current_loaded_files,
                current_file_paths,
                html.Div("No valid new files found", style={"color": "red"}),
                file_paths_input,
                create_file_pills(current_files),
                str(len(current_files)),
                {"display": "none"},
                {"display": "none"},
                [],
                False,
                {}
            )

    # Update file information tooltip
    @app.callback(
        Output("file-info-content", "children"),
        Input("loaded-files", "data")
    )
    def update_file_info(loaded_files):
        """
        Update file information display with details about loaded files.
        Shows file size, creation time, and modification time for each loaded file.
        """
        if not loaded_files or "files" not in loaded_files:
            return "No files loaded"
        
        info_content = []
        for file_path in loaded_files["files"]:
            file_info = get_file_info(file_path)
            info_content.append(html.Div([
                html.H6(os.path.basename(file_path), className="mb-1"),
                html.P([
                    html.Small(f"{file_info['file_size']} MB | Modified: {datetime.datetime.fromtimestamp(file_info['modification_time']).strftime('%Y-%m-%d %H:%M:%S')}"),
                    html.Br(),
                    html.Small(file_path, className="text-muted")
                ], className="mb-2")
            ]))
        
        return info_content
    
    #######################
    # SIGNAL SELECTION CALLBACKS
    #######################
    
    # Update signal dropdowns based on loaded files
    @app.callback(
        Output("signalx", "options"),
        Output("signalx", "value"),
        Output("signaly", "options"),
        Output("signaly", "value"),
        Output("time-start", "min"),
        Output("time-start", "max"),
        Output("time-end", "min"),
        Output("time-end", "max"),
        Input("file-path-list", "data"),
        State("signalx", "value"),
        State("signaly", "value"),
        State("time-range-info", "data"),
        prevent_initial_call=True
    )
    def update_signal_dropdowns(file_paths, current_x, current_y, time_range_info):
        """
        Update signal dropdowns with available columns from loaded files.
        Preserves current selections if they are valid.
        """
        if not file_paths or not DATAFRAMES:
            raise PreventUpdate
        
        # Get first dataframe to extract columns
        first_path = file_paths[0]
        if first_path not in DATAFRAMES:
            raise PreventUpdate
        
        df = DATAFRAMES[first_path]
        if df is None or df.empty:
            raise PreventUpdate
        
        # Get column names
        df_columns = list(df.columns)
        sorted_columns = sorted(df_columns)
        
        # Determine default x axis if not set
        default_x = current_x
        if default_x is None or default_x not in sorted_columns:
            default_x = "Time_[s]"
            if default_x not in sorted_columns:
                default_x = "Time" if "Time" in sorted_columns else sorted_columns[0]
        
        # Determine default y signals if not set
        default_y = current_y
        if default_y is None or not default_y or not all(y in sorted_columns for y in default_y):
            # Default y axis could be a few common signals
            common_signals = ["GenPwr_[kW]", "BldPitch1_[deg]", "RotSpeed_[rpm]", "WindVxi_[m/s]"]
            default_y = []
            
            # Try to find common signals or alternatives
            for signal in common_signals:
                # Try to find the exact signal
                if signal in sorted_columns:
                    default_y.append(signal)
                else:
                    # Try to find a similar signal
                    base_name = signal.split('_')[0]
                    for col in sorted_columns:
                        if (col.startswith(base_name)):
                            default_y.append(col)
                            break
            
            # If no common signals found, use first few columns
            if not default_y:
                default_y = sorted_columns[:2]  # Take first 2 columns if common signals not found
            
            # Don't include x-axis in y-axis
            if default_x in default_y:
                default_y.remove(default_x)
            
        # Set up time range limits
        min_time = 0
        max_time = 1000
        if 'min_time' in time_range_info and 'max_time' in time_range_info:
            min_time = time_range_info['min_time']
            max_time = time_range_info['max_time']
        else:
            # Default to first file's time range if no info available
            time_col = default_x
            try:
                min_time = df[time_col].min()
                max_time = df[time_col].max()
            except KeyError:
                # If time_col doesn't exist in the dataframe
                pass
        
        return (
            sorted_columns,
            default_x,
            sorted_columns,
            default_y,
            min_time,
            max_time,
            min_time,
            max_time
        )

    # Reset time range when reset button is pressed
    @app.callback(
        Output("time-start", "value"),
        Output("time-end", "value"),
        Input("reset-time-range-btn", "n_clicks"),
        State("time-range-info", "data"),
        prevent_initial_call=True
    )
    def reset_time_range(reset_clicks, time_range_info):
        """
        Reset time range control values when the reset button is clicked.
        """
        # Only triggered by reset button
        if not reset_clicks:
            raise PreventUpdate
        
        # Set values from time_range_info if available
        if 'min_time' in time_range_info and 'max_time' in time_range_info:
            return time_range_info['min_time'], time_range_info['max_time']
        else:
            # If no time range info available, return default None
            return None, None

    #######################
    # TIME DOMAIN PLOT CALLBACKS
    #######################
    
    # Update plots based on user selections
    @app.callback(
        Output("plot-output", "children"),
        Output("current-plot-data", "data"),
        Output("current-figure", "data"),
        Input("plot-btn", "n_clicks"),
        Input("loaded-files", "data"),
        State("file-path-list", "data"),
        State("signalx", "value"),
        State("signaly", "value"),
        State("plot-option", "value"),
        State("current-figure", "data"),
        State("time-start", "value"),
        State("time-end", "value"),
        prevent_initial_call=True
    )
    def update_plots(n_clicks, loaded_files, file_paths, signalx, signaly, plot_option, current_fig, start_time, end_time):
        """
        Update plots based on selected signals and plot options.
        
        This function:
        1. Creates plots based on user-selected signals
        2. Handles both overlay and separate plot modes
        3. Stores plot configuration for export
        4. Applies time range filtering
        """
        # Check if we have valid input data
        if not loaded_files or "files" not in loaded_files or not file_paths or not DATAFRAMES or not signalx or not signaly:
            return html.Div("Select signals to plot", className="text-center p-5 text-muted"), {}, None
        
        # Store the current plot configuration for export
        plot_config = {
            "file_paths": file_paths,
            "signalx": signalx,
            "signaly": signaly,
            "plot_option": plot_option,
            "start_time": start_time,
            "end_time": end_time
        }
        
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
            return html.Div("No data in selected time range", style={"color": "red"}), plot_config, None
        
        # If overlay option or only one file, create a combined plot
        if plot_option == "overlay" or len(valid_paths) == 1:
            # Generate new figure
            fig = draw_graph(valid_paths, filtered_dfs, signalx, signaly, "overlay")
                
            return dcc.Graph(figure=fig, id="main-plot-graph", config={'displayModeBar': True}), plot_config, fig
        
        # If separate option, create individual plots for each file
        elif plot_option == "separate":
            plots = []
            figures = []
            
            for i, (file_path, df) in enumerate(zip(valid_paths, filtered_dfs)):
                fig = draw_graph([file_path], [df], signalx, signaly, "separate")
                figures.append(fig)
                plot_id = f"plot-{uuid.uuid4()}"
                path_identifiers = get_unique_identifiers(valid_paths)
                # Create card header with tooltip
                header_with_tooltip = html.Div(
                    [
                        path_identifiers[file_path],
                        html.Span(
                            "ⓘ",
                            id={"type": "file-path-tooltip", "index": plot_id},
                            className="ms-2 text-muted",
                            style={"cursor": "pointer", "fontSize": "0.8rem"}
                        ),
                        dbc.Tooltip(
                            file_path,
                            target={"type": "file-path-tooltip", "index": plot_id},
                        )
                    ],
                    className="d-flex justify-content-between align-items-center"
                )
                plots.append(
                    dbc.Card([
                        dbc.CardHeader(header_with_tooltip, className="p-2"),
                        dbc.CardBody([
                            dcc.Graph(figure=fig, id=plot_id, config={'displayModeBar': False})
                        ], className="p-1")
                    ], className="mb-3")
                )
            
            # Return only the first figure for export purposes
            first_fig = figures[0] if figures else None
            return html.Div(plots), plot_config, first_fig
    
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
    
    #######################
    # FFT ANALYSIS CALLBACKS
    #######################
    
    # FFT Analysis calculation
    @app.callback(
        Output("fft-plot-output", "children"),
        Output("current-fft-figure", "data"),
        Input("fft-calculate-btn", "n_clicks"),
        State("file-path-list", "data"),
        State("signalx", "value"),
        State("signaly", "value"),
        State("fft-averaging", "value"),
        State("fft-windowing", "value"),
        State("fft-n-exp", "value"),
        State("fft-plot-style", "value"),  # Swapped position with detrend
        State("fft-detrend", "value"),     # Swapped position with plot_style
        State("fft-x-limit", "value"),
        State("fft-xscale", "value"),
        State("time-start", "value"),
        State("time-end", "value"),
        State("fft-annotations", "data"),
        prevent_initial_call=True
    )
    def calculate_fft(n_clicks, file_paths, time_col, signals, averaging, windowing, n_exp, plot_style, detrend, x_limit, xscale, start_time, end_time, annotations):
        """
        Calculate FFT for all selected signals across all files.
        
        This function:
        1. Retrieves the selected signals from all files
        2. Applies time range filtering if specified
        3. Calculates FFT using our custom module
        4. Creates plots of the FFT results
        """
        if not n_clicks:
            raise PreventUpdate
        
        if not file_paths or not DATAFRAMES:
            return html.Div("No files loaded", className="text-center p-5 text-muted"), None
        
        if not time_col:
            return html.Div("Please select a time column (X Signal)", style={"color": "red"}), None
        
        if not signals or len(signals) == 0:
            return html.Div("Please select at least one signal (Y Signal)", style={"color": "red"}), None
        
        # Convert detrend flag
        detrend_bool = "detrend" in detrend  # Convert from list to bool
        
        # OVERLAY PLOT STYLE - All signals in a single figure
        if plot_style == "overlay":
            fig = go.Figure()
            
            # Create one figure with all signals and files
            for signal_idx, signal in enumerate(signals):
                for file_idx, file_path in enumerate(file_paths):
                    if file_path not in DATAFRAMES:
                        continue
                    
                    df = DATAFRAMES[file_path]
                    
                    if signal not in df.columns or time_col not in df.columns:
                        continue
                    
                    try:
                        # Use our custom FFT implementation
                        fft_result = compute_fft(
                            df, 
                            signal, 
                            time_col=time_col,
                            start_time=start_time,
                            end_time=end_time,
                            averaging=averaging,
                            windowing=windowing,
                            detrend=detrend_bool,
                            n_exp=n_exp
                        )
                        
                        # Extract results
                        freq = fft_result.freq
                        amp = fft_result.amplitude
                        
                        # Get file identifier for legend
                        file_identifiers = get_unique_identifiers(file_paths)
                        file_name = file_identifiers.get(file_path, os.path.basename(file_path))
                        
                        # Create a color palette for signals
                        color_idx = signal_idx % len(plotly.colors.DEFAULT_PLOTLY_COLORS)
                        base_color = plotly.colors.DEFAULT_PLOTLY_COLORS[color_idx]
                        
                        # Create line style variations for different files
                        line_styles = ['solid', 'dash', 'dot', 'dashdot']
                        line_style = line_styles[file_idx % len(line_styles)]
                        
                        # Add FFT trace to figure with unique name for legend
                        fig.add_trace(go.Scatter(
                            x=freq,
                            y=amp,
                            mode='lines',
                            line=dict(
                                color=base_color,
                                dash=line_style if line_style != 'solid' else None
                            ),
                            name=f"{signal} - {file_name}"
                        ))
                    except Exception as e:
                        print(f"Error in FFT calculation for {file_path}, signal {signal}: {e}")
                        print(traceback.format_exc())
                        continue
            
            # Add annotation lines if any
            if annotations:
                for anno in annotations:
                    freq = anno["freq"]
                    label = anno["label"]
                    
                    # Skip if frequency is out of bounds
                    if x_limit and freq > x_limit:
                        continue
                    
                    # Add vertical line
                    fig.add_shape(
                        type="line",
                        x0=freq, x1=freq,
                        y0=0, y1=1,
                        yref="paper",
                        line=dict(color="rgba(0,0,0,0.5)", width=1, dash="dash"),
                    )
                    
                    # Add annotation text
                    fig.add_annotation(
                        x=freq,
                        y=0.90,  # High in the plot, but not at the very top
                        yref="paper",
                        text=f"{label}: {freq:.2f} Hz",  # Include frequency with 2 decimal places
                        showarrow=False,
                        textangle=0,  # Horizontal text
                        xanchor="right",
                        yanchor="middle",
                        font=dict(size=10),
                        bgcolor="rgba(255, 255, 255, 0.7)",
                        borderpad=2
                    )
            
            # Update layout
            fig.update_layout(
                title='FFT Analysis - All Signals',
                xaxis_title='Frequency (Hz)',
                yaxis_title='Amplitude',
                height=600,
                margin=dict(l=50, r=150, t=30, b=50),  # Reduced right margin
                xaxis_type=xscale,
                yaxis_type='log',
                showlegend=True,
                legend=dict(
                    orientation='v',  # Vertical orientation
                    yanchor='middle',  # Centered vertically
                    xanchor='left',  # Anchor to the left of the legend box
                    x=1.05,  # Bring legend closer to the plot
                    y=0.5   # Center legend vertically
                )
            )
            
            # Apply x-axis limit if specified
            if x_limit and xscale == 'log':
                fig.update_xaxes(range=[np.log10(0.001), np.log10(x_limit)])
            elif x_limit:
                fig.update_xaxes(range=[0, x_limit])
            
            # Create layout with plot
            layout = dbc.Row([
                dbc.Col(dcc.Graph(figure=fig, id="main-fft-graph", config={'displayModeBar': True}), width=12)
            ])
            
            return layout, fig
        
        # SEPARATE PLOT STYLE - One plot per signal
        else:
            fft_panels = []
            figures = []
            
            for signal in signals:
                # Create a subplot for each signal
                fig = go.Figure()
                
                file_results = []
                
                # Process each file
                for i, file_path in enumerate(file_paths):
                    if file_path not in DATAFRAMES:
                        continue
                    
                    df = DATAFRAMES[file_path]
                    
                    if signal not in df.columns or time_col not in df.columns:
                        continue
                    
                    try:
                        # Use our custom FFT implementation
                        fft_result = compute_fft(
                            df, 
                            signal, 
                            time_col=time_col,
                            start_time=start_time,
                            end_time=end_time,
                            averaging=averaging,
                            windowing=windowing,
                            detrend=detrend_bool,
                            n_exp=n_exp
                        )
                        
                        # Extract results
                        freq = fft_result.freq
                        amp = fft_result.amplitude
                        
                        # Store for later use
                        file_results.append({
                            'file_path': file_path,
                            'freq': freq,
                            'amp': amp,
                            'fft_result': fft_result
                        })
                        
                        # Get file identifier for legend
                        file_identifiers = get_unique_identifiers(file_paths)
                        file_name = file_identifiers.get(file_path, os.path.basename(file_path))
                        
                        # Add FFT trace to figure
                        fig.add_trace(go.Scatter(
                            x=freq,
                            y=amp,
                            mode='lines',
                            line=dict(color=plotly.colors.DEFAULT_PLOTLY_COLORS[i % len(plotly.colors.DEFAULT_PLOTLY_COLORS)]),
                            name=file_name
                        ))
                    except Exception as e:
                        print(f"Error in FFT calculation for {file_path}, signal {signal}: {e}")
                        print(traceback.format_exc())
                        continue
                
                if not file_results:
                    continue
                
                # Add annotation lines if any
                if annotations:
                    for anno in annotations:
                        freq = anno["freq"]
                        label = anno["label"]
                        
                        # Skip if frequency is out of bounds
                        if x_limit and freq > x_limit:
                            continue
                        
                        # Add vertical line
                        fig.add_shape(
                            type="line",
                            x0=freq, x1=freq,
                            y0=0, y1=1,
                            yref="paper",
                            line=dict(color="rgba(0,0,0,0.5)", width=1, dash="dash"),
                        )
                        
                        # Add annotation text
                        fig.add_annotation(
                            x=freq,
                            y=0.90,
                            yref="paper",
                            text=f"{label}: {freq:.2f} Hz",
                            showarrow=False,
                            textangle=0,
                            xanchor="right",
                            yanchor="middle",
                            font=dict(size=10),
                            bgcolor="rgba(255, 255, 255, 0.7)",
                            borderpad=2
                        )
                
                # Update layout
                fig.update_layout(
                    title=f'FFT Analysis of {signal}',
                    xaxis_title='Frequency (Hz)',
                    yaxis_title='Amplitude',
                    height=500,
                    margin=dict(l=50, r=150, t=30, b=50),  # Reduced right margin
                    xaxis_type=xscale,
                    yaxis_type='log',
                    showlegend=True,
                    legend=dict(
                        orientation='v',  # Vertical orientation
                        yanchor='middle',  # Centered vertically
                        xanchor='left',  # Anchor to the left of the legend box
                        x=1.05,  # Bring legend closer to the plot
                        y=0.5   # Center legend vertically
                    )
                )
                
                # Apply x-axis limit if specified
                if x_limit and xscale == 'log':
                    fig.update_xaxes(range=[np.log10(0.001), np.log10(x_limit)])
                elif x_limit:
                    fig.update_xaxes(range=[0, x_limit])
                
                figures.append(fig)
                
                # Add the graph to the panel    
                fft_panels.append(
                    dbc.Card([
                        dbc.CardHeader(f"FFT Analysis: {signal}"),
                        dbc.CardBody([
                            dcc.Graph(figure=fig, config={'displayModeBar': True})
                        ])
                    ], className="mb-4")
                )
            
            if not fft_panels:
                return html.Div("No valid FFT results could be calculated. Please check your signal selections.", className="alert alert-warning"), None
                
            # Return the layout with all panels and the first figure for export
            return html.Div(fft_panels), figures[0] if figures else None

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

    #######################
    # FFT ANNOTATION CALLBACKS
    #######################
    
    # Add callback to manage annotations
    @app.callback(
        Output("fft-annotations", "data"),
        Output("fft-annotations-display", "children"),
        Output("fft-annotation-freq", "value"),
        Output("fft-annotation-text", "value"),
        Input("fft-add-annotation-btn", "n_clicks"),
        Input("tabs", "active_tab"),  # Reset when switching tabs
        State("fft-annotation-freq", "value"),
        State("fft-annotation-text", "value"),
        State("fft-annotations", "data"),
        prevent_initial_call=True
    )
    def manage_fft_annotations(add_clicks, active_tab, freq_input, label_input, current_annotations):
        """
        Add and manage annotations for FFT plots
        """
        trigger = ctx.triggered_id
        
        # Don't reset annotations when switching tabs anymore
        if trigger == "tabs":
            # Only clear input fields but keep the annotations
            return current_annotations, create_annotation_badges(current_annotations), None, None
        
        # Skip if no click or no input
        if not add_clicks or not freq_input:
            raise PreventUpdate
        
        # Parse frequency input
        try:
            freqs = [float(f.strip()) for f in freq_input.split(",") if f.strip()]
        except ValueError:
            # Handle parsing error
            return current_annotations, [
                html.Div("Invalid frequency format. Use comma-separated numbers.", 
                         className="text-danger small")
            ] + create_annotation_badges(current_annotations), freq_input, label_input
        
        # Parse labels - if not provided or fewer than freqs, generate automatic labels
        if not label_input:
            labels = [f"F{i+1}" for i in range(len(freqs))]
        else:
            labels = [l.strip() for l in label_input.split(",")]
            # If fewer labels than frequencies, add generic labels
            if len(labels) < len(freqs):
                labels += [f"F{i+1}" for i in range(len(labels), len(freqs))]
        
        # Create new annotations
        new_annotations = current_annotations.copy() if current_annotations else []
        for freq, label in zip(freqs, labels):
            new_annotations.append({"freq": freq, "label": label})
        
        # Sort by frequency
        new_annotations.sort(key=lambda x: x["freq"])
        
        # Save annotations to user preferences
        save_custom_annotations(new_annotations)
        
        # Create badges for visual display
        badges = create_annotation_badges(new_annotations)
        
        return new_annotations, badges, None, None

    # Add callback to remove individual annotations
    @app.callback(
        Output("fft-annotations", "data", allow_duplicate=True),
        Output("fft-annotations-display", "children", allow_duplicate=True),
        Input({"type": "remove-annotation", "index": ALL}, "n_clicks"),
        State("fft-annotations", "data"),
        prevent_initial_call=True
    )
    def remove_annotation(n_clicks, current_annotations):
        """
        Remove an annotation when its delete button is clicked
        """
        if not any(n_clicks):
            raise PreventUpdate
        
        # Find which annotation to remove
        triggered_id = ctx.triggered_id
        if triggered_id and "index" in triggered_id:
            index_to_remove = triggered_id["index"]
            
            # Remove the annotation
            new_annotations = [a for i, a in enumerate(current_annotations) if i != index_to_remove]
            
            # Save to user preferences
            save_custom_annotations(new_annotations)
            
            # Update badges
            badges = create_annotation_badges(new_annotations)
            
            return new_annotations, badges
        
        raise PreventUpdate

    # Add callback to generate harmonics from Rotor RPM
    @app.callback(
        Output("fft-annotations", "data", allow_duplicate=True),
        Output("fft-annotations-display", "children", allow_duplicate=True),
        Output("rotor-rpm-input", "value"),
        Input("add-harmonics-btn", "n_clicks"),
        State("rotor-rpm-input", "value"),
        State("fft-annotations", "data"),
        prevent_initial_call=True
    )
    def generate_rotor_harmonics(n_clicks, rpm_value, current_annotations):
        """
        Generate frequency annotations for selected rotor harmonics 
        based on the rotor RPM input.
        """
        if not n_clicks or rpm_value is None or rpm_value <= 0:
            raise PreventUpdate
        
        # Convert RPM to Hz (frequency)
        freq_1p = rpm_value / 60.0
        
        # Define which harmonics to include
        harmonics = [1, 2, 3, 4, 6, 8, 9]
        
        # Generate annotations for selected harmonics
        new_annotations = current_annotations.copy() if current_annotations else []
        for i in harmonics:  # Only selected harmonics
            harmonic_freq = freq_1p * i
            harmonic_label = f"{i}P"
            
            # Check if this harmonic already exists (avoid duplicates)
            exists = any(abs(anno.get('freq', 0) - harmonic_freq) < 0.001 and 
                        anno.get('label', '') == harmonic_label 
                        for anno in new_annotations)
            
            if not exists:
                new_annotations.append({"freq": harmonic_freq, "label": harmonic_label})
        
        # Sort by frequency
        new_annotations.sort(key=lambda x: x["freq"])
        
        # Save to user preferences
        save_custom_annotations(new_annotations)
        
        # Create badges for visual display
        badges = create_annotation_badges(new_annotations)
        
        return new_annotations, badges, None
        
    # Add new callback for removing individual files
    @app.callback(
        [Output('loaded-files', 'data', allow_duplicate=True),
         Output('file-path-list', 'data', allow_duplicate=True),
         Output('loaded-files-pills', 'children', allow_duplicate=True),
         Output('loaded-files-count', 'children', allow_duplicate=True),
         Output('signalx', 'options', allow_duplicate=True),
         Output('signaly', 'options', allow_duplicate=True),
         Output('plot-output', 'children', allow_duplicate=True)],
        [Input({'type': 'remove-file-btn', 'index': ALL}, 'n_clicks')],
        [State('loaded-files', 'data'),
         State('file-path-list', 'data')],
        prevent_initial_call=True
    )
    def remove_loaded_file(n_clicks, loaded_files, file_paths):
        """
        Remove a loaded file when its remove button is clicked.
        """
        if not any(n_clicks) or not loaded_files or "files" not in loaded_files:
            raise PreventUpdate
        
        button_id = ctx.triggered_id
        if button_id is None:
            raise PreventUpdate
        
        index = button_id['index']
        current_files = loaded_files.get("files", [])
        
        if index >= len(current_files):
            raise PreventUpdate
        
        file_to_remove = current_files[index]
        remove_file(file_to_remove)
        
        updated_files = [f for i, f in enumerate(current_files) if i != index]
        updated_file_paths = [f for f in file_paths if f != file_to_remove]
        
        # Update the file pills
        file_pills = create_file_pills(updated_files)
        
        # Update the file count badge
        file_count = str(len(updated_files))
        
        # Get common signals across remaining files
        signal_options = []
        if updated_files:
            if updated_files[0] in DATAFRAMES:
                # Get common columns from first file
                signal_options = sorted(list(DATAFRAMES[updated_files[0]].columns))
        
        # Clear the plot if no files are left - use no_update instead of dash.no_update
        plot_output = html.Div("Select signals to plot", className="text-center p-5 text-muted") if not updated_files else no_update
        
        return ({"files": updated_files}, updated_file_paths, file_pills, file_count, signal_options, signal_options, plot_output)

    # Add favorite signals callbacks
    @app.callback(
        Output("signaly", "value", allow_duplicate=True),
        Input("favorite-signals-btn", "n_clicks"),
        State("signaly", "options"),
        prevent_initial_call=True
    )
    def load_favorite_signals(n_clicks, available_signals):
        """Load favorite signals from user preferences"""
        if not n_clicks:
            raise PreventUpdate
        
        prefs = load_preferences()
        favorites = prefs.get("favorite_signals", [])
        
        # If there are no favorites or no available signals, prevent update
        if not favorites or not available_signals:
            return no_update
            
        # Handle different formats of dropdown options
        # Check the type of the first option to determine format
        if isinstance(available_signals[0], dict) and 'value' in available_signals[0]:
            # Format is list of dicts with 'value' key
            available_signal_values = [opt['value'] for opt in available_signals]
        elif isinstance(available_signals[0], str):
            # Format is just a list of strings (the values themselves)
            available_signal_values = available_signals
        else:
            # Unknown format, prevent update
            return no_update
        
        # Filter favorites to only include available signals
        valid_favorites = [sig for sig in favorites if sig in available_signal_values]
        
        if not valid_favorites:
            return no_update
            
        return valid_favorites
    
    # Add callback to save favorite signals
    @app.callback(
        Output("favorite-signals-status", "children"),
        Input("save-favorites-btn", "n_clicks"),
        State("signaly", "value"),
        prevent_initial_call=True
    )
    def save_favorite_signals_callback(n_clicks, selected_signals):
        """Save currently selected signals as favorites"""
        if not n_clicks or not selected_signals:
            raise PreventUpdate
            
        update_favorite_signals(selected_signals)
        
        return html.Span("Saved!", className="text-success fade-out")

    # Add callbacks to save settings
    @app.callback(
        Output("plot-metadata", "data", allow_duplicate=True),  # Just a dummy output
        Input("plot-option", "value"),
        State("plot-metadata", "data"),
        prevent_initial_call=True
    )
    def save_plot_settings_callback(plot_option, metadata):
        """Save plot settings to user preferences when they change"""
        settings = {"plot_option": plot_option}
        save_plot_settings(settings)
        return no_update

    # Add callback to save FFT settings when they change
    @app.callback(
        Output("plot-metadata", "data", allow_duplicate=True),  # Just a dummy output
        Input("fft-averaging", "value"),
        Input("fft-windowing", "value"),
        Input("fft-n-exp", "value"),
        Input("fft-plot-style", "value"),
        Input("fft-detrend", "value"),
        Input("fft-xscale", "value"),
        Input("fft-x-limit", "value"),
        State("plot-metadata", "data"),
        prevent_initial_call=True
    )
    def save_fft_settings_callback(averaging, windowing, n_exp, plot_style, detrend, xscale, x_limit, metadata):
        """Save FFT settings to user preferences when they change"""
        settings = {
            "averaging": averaging,
            "windowing": windowing,
            "n_exp": n_exp,
            "plot_style": plot_style,
            "detrend": "detrend" in detrend,
            "xscale": xscale,
            "x_limit": x_limit
        }
        save_fft_settings(settings)
        return no_update