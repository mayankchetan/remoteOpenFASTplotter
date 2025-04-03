'''
Remote OpenFAST Plotter - A DASH application to read and plot OpenFAST output files on remote computers

Features:
- Load and visualize multiple OpenFAST output files
- Interactive signal selection and plotting
- Customizable display options (overlay or separate plots)
- Direct HTML export for sharing and reporting
- Memory-efficient handling of large datasets
- Spectral (FFT) analysis with advanced configuration options
'''

# Import Packages
import os
import sys
import dash
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.colors
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html, ctx, no_update, ALL, MATCH
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots
import yaml
import re
from pathlib import Path
import concurrent.futures
import time
import uuid
import json
import math

# Import local modules
from openfast_io.FAST_output_reader import FASTOutputFile

# Import our custom FFT analysis module
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))
from tools.fft_analysis import compute_fft

# Initialize the Dash app with Bootstrap styling
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP, 
        'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css'
    ],
    suppress_callback_exceptions=True  # Allow dynamic components
)

#######################
# UTILITY FUNCTIONS
#######################

def load_file(file_path):
    """
    Load a single OpenFAST file
    
    Parameters:
    -----------
    file_path : str
        Path to OpenFAST output file
        
    Returns:
    --------
    tuple : (file_path, dataframe or None, error_message or None, elapsed_time)
    """
    try:
        start_time = time.time()
        tempObj = FASTOutputFile(file_path)
        df = tempObj.toDataFrame()
        elapsed = time.time() - start_time
        return (file_path, df, None, elapsed)
    except Exception as e:
        return (file_path, None, str(e), 0)

def store_dataframes(file_paths, max_workers=None):
    """
    Read OpenFAST output files and store them as dataframes using parallel processing
    
    Parameters:
    -----------
    file_paths : list of str
        List of paths to OpenFAST output files
    max_workers : int, optional
        Maximum number of worker threads
        
    Returns:
    --------
    tuple : (Dictionary of dataframes {file_path: dataframe}, list of failed files, dict of load times)
    """
    dfs = {}
    failed = []
    times = {}
    
    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all file loading tasks
        future_to_file = {executor.submit(load_file, file): file for file in file_paths}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            file_path, df, error, elapsed = future.result()
            if df is not None:
                dfs[file_path] = df
                times[file_path] = elapsed
            else:
                failed.append((file_path, error))
    
    return dfs, failed, times

def get_file_info(file_path):
    """
    Get file information such as size, creation time, and modification time.
    
    Parameters:
    -----------
    file_path : str
        Path to file
        
    Returns:
    --------
    dict : Dictionary of file information
    """
    try:
        file_stats = os.stat(file_path)
        file_info = {
            'file_abs_path': file_path,
            'file_size': file_stats.st_size / (1024 * 1024),  # Store in MB without rounding initially
            'creation_time': file_stats.st_ctime,
            'modification_time': file_stats.st_mtime
        }
        return file_info
    except Exception as e:
        print(f"Error getting file info for {file_path}: {e}")
        return {
            'file_abs_path': file_path,
            'file_size': 0,
            'creation_time': 0,
            'modification_time': 0
        }

def remove_duplicated_legends(fig):
    """
    Remove duplicated legends in plotly figure to avoid clutter.
    
    Parameters:
    -----------
    fig : plotly.graph_objects.Figure
        The figure to modify
        
    Returns:
    --------
    plotly.graph_objects.Figure
        The modified figure with duplicate legends removed
    """
    names = set()
    fig.for_each_trace(
        lambda trace:
            trace.update(showlegend=False)
            if (trace.name in names)
            else names.add(trace.name)
    )
    return fig

def get_unique_identifiers(file_paths):
    """
    Generate unique identifiers for files by comparing paths and extracting differences.
    
    Parameters:
    -----------
    file_paths : list of str
        List of file paths
        
    Returns:
    --------
    dict : Dictionary of {file_path: unique_identifier}
    """
    if not file_paths:
        return {}
    
    if len(file_paths) == 1:
        return {file_paths[0]: os.path.basename(file_paths[0])}
    
    # First try just filenames
    filenames = [os.path.basename(path) for path in file_paths]
    if len(set(filenames)) == len(filenames):
        return {path: os.path.basename(path) for path in file_paths}
    
    # If filenames aren't unique, try parent dir + filename
    parent_and_filename = [os.path.join(os.path.basename(os.path.dirname(path)), os.path.basename(path)) for path in file_paths]
    if len(set(parent_and_filename)) == len(parent_and_filename):
        return {path: os.path.join(os.path.basename(os.path.dirname(path)), os.path.basename(path)) for path in file_paths}
    
    # Find common prefix and suffix in paths
    paths = [os.path.normpath(p) for p in file_paths]
    parts = [p.split(os.sep) for p in paths]
    
    # Find the first differing element and last differing element
    min_len = min(len(p) for p in parts)
    first_diff = 0
    while first_diff < min_len:
        if len(set(p[first_diff] for p in parts)) > 1:
            break
        first_diff += 1
    
    last_diff = -1
    min_last = -min_len
    while last_diff >= min_last:
        if len(set(p[last_diff] for p in parts)) > 1:
            break
        last_diff -= 1
    
    # Extract only the differentiating parts of paths
    unique_parts = []
    for path, part in zip(file_paths, parts):
        if first_diff >= len(part) or abs(last_diff) >= len(part):
            # If we can't find meaningful differences, use full filename
            unique_parts.append(os.path.basename(path))
        else:
            if last_diff == -1:  # Only beginning differs
                unique_part = os.path.join(*part[first_diff:])
            else:  # Both beginning and end differ
                unique_part = os.path.join(*part[first_diff:len(part)+last_diff+1])
            unique_parts.append(unique_part)
    
    # Ensure we still have unique identifiers
    if len(set(unique_parts)) != len(file_paths):
        # Fallback: use shorter but still unique paths
        common_prefix_len = 0
        for chars in zip(*paths):
            if len(set(chars)) == 1:
                common_prefix_len += 1
            else:
                break
        
        common_suffix_len = 0
        for chars in zip(*[p[::-1] for p in paths]):
            if len(set(chars)) == 1:
                common_suffix_len += 1
            else:
                break
        
        unique_parts = [p[common_prefix_len:len(p)-common_suffix_len if common_suffix_len > 0 else len(p)] for p in paths]
        
        # If still not unique, just use numbered identifiers with filenames
        if len(set(unique_parts)) != len(file_paths):
            return {path: f"{i+1}:{os.path.basename(path)}" for i, path in enumerate(file_paths)}
    
    return {path: part for path, part in zip(file_paths, unique_parts)}

def draw_graph(file_path_list, df_list, signalx, signaly, plot_option):
    """
    Draw graphs based on the selected signals and plot options.
    
    Parameters:
    -----------
    file_path_list : list of str
        List of file paths
    df_list : list of pandas.DataFrame
        List of DataFrames corresponding to file_path_list
    signalx : str
        X-axis signal
    signaly : list of str
        List of Y-axis signals
    plot_option : str
        'overlay' or 'separate'
        
    Returns:
    --------
    plotly.graph_objects.Figure
        The generated figure
    """
    # Create figure with subplots for each Y signal
    fig = make_subplots(rows=len(signaly), cols=1, shared_xaxes=True, vertical_spacing=0.05)
    
    # Colors for different files
    cols = plotly.colors.DEFAULT_PLOTLY_COLORS
    
    # Get unique identifiers for file paths
    path_identifiers = get_unique_identifiers(file_path_list)
    
    # If we're plotting multiple files
    if plot_option == 'overlay' and len(df_list) > 1:
        for idx, df in enumerate(df_list):
            file_path = file_path_list[idx]
            identifier = path_identifiers[file_path]
            
            for row_idx, label in enumerate(signaly):
                fig.append_trace(go.Scatter(
                    x=df[signalx],
                    y=df[label],
                    mode='lines',
                    line=dict(color=cols[idx % len(cols)]),
                    name=identifier
                ),
                row=row_idx + 1,
                col=1)
                fig.update_yaxes(title_text=label, row=row_idx+1, col=1)
        
        # Remove duplicated legends
        remove_duplicated_legends(fig)
        
    # If we're plotting a single file or separate plots  
    else:
        for idx, df in enumerate(df_list):
            for row_idx, label in enumerate(signaly):
                fig.append_trace(go.Scatter(
                    x=df[signalx],
                    y=df[label],
                    mode='lines',
                    showlegend=False),
                    row=row_idx + 1,
                    col=1)
                fig.update_yaxes(title_text=label, row=row_idx+1, col=1)
    
    # Common layout updates
    fig.update_layout(
        height=200 * len(signaly),  # Increased from 150 to 200 for taller subplots
        margin=dict(l=50, r=20, t=30, b=50),  # Reduce margins
        legend=dict(orientation='h', yanchor='bottom', xanchor='center', x=0.5, y=1.02)
    )
    fig.update_xaxes(title_text=signalx, row=len(signaly), col=1)
    
    return fig

#######################
# LAYOUT COMPONENTS
#######################

# File input card for loading and displaying OpenFAST files
file_input_card = dbc.Card([
    dbc.CardHeader([
        html.Span("Load OpenFAST Files", className="me-auto"),
        html.Span([
            dbc.Badge(id="loaded-files-count", color="primary", className="me-1"),
            html.Span(" files loaded", className="small")
        ])
    ], className="d-flex justify-content-between align-items-center"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col(
                dbc.Textarea(
                    id="file-paths-input",
                    placeholder="Paste file paths here, one per line...",
                    style={"height": "100px"},
                ),
                width=9
            ),
            dbc.Col([
                dbc.Button("Load Files", id="load-files-btn", color="primary", className="w-100 mb-2"),
                dbc.Button("Clear All", id="clear-files-btn", color="secondary", outline=True, className="w-100")
            ], width=3)
        ], className="mb-2"),
        html.Div(id="file-loading-status", className="mt-2 small"),
        html.Div([
            html.Div([
                dbc.Button(
                    "Show error details",
                    id="error-details-button",
                    size="sm",
                    color="link",
                    className="p-0 mt-1",
                    style={"display": "none"}
                ),
            ]),
            dbc.Collapse(
                id="error-details-collapse",
                is_open=False,
                className="mt-2"
            )
        ], id="error-details-container", style={"display": "none"}),
        html.Div(id="loaded-files-pills", className="mt-3"),
        # Add file info link to file input card
        html.Div([
            html.A(id="file-info-link", children=[
                html.I(className="bi bi-info-circle me-1", style={"fontSize": "1.1rem"}),
                "File Info"
            ], href="#", className="text-decoration-none")
        ], className="d-flex justify-content-end mt-2")
    ])
])

# Time range selection component - Now promoted to be used globally
time_range_card = dbc.Card([
    dbc.CardHeader("Time Range Selection"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Label("Start Time"),
                dbc.InputGroup([
                    dbc.Input(
                        id="time-start", 
                        type="number", 
                        placeholder="Start time",
                        step="any",
                        min=0
                    ),
                    dbc.InputGroupText("s")
                ])
            ], width=6),
            dbc.Col([
                html.Label("End Time"),
                dbc.InputGroup([
                    dbc.Input(
                        id="time-end", 
                        type="number", 
                        placeholder="End time",
                        step="any",
                        min=0
                    ),
                    dbc.InputGroupText("s")
                ])
            ], width=6)
        ]),
        dbc.Row([
            dbc.Col(
                dbc.Button(
                    "Reset Time Range",
                    id="reset-time-range-btn",
                    color="link",
                    size="sm",
                    className="mt-2"
                ),
                width="auto"
            )
        ])
    ])
])

# Signal selection component - Now promoted to be used globally
signal_selection_card = dbc.Card([
    dbc.CardHeader("Signal Selection"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col(
                [
                    html.Label("Y Signals"),
                    dcc.Dropdown(id="signaly", options=[], value=None, multi=True),
                ],
                width=6
            ),
            dbc.Col(
                [
                    html.Label("X Signal"),
                    dcc.Dropdown(id="signalx", options=[], value=None),
                ],
                width=6
            ),
        ]),
    ])
])

# Plot controls card for time-domain plotting - Now with fewer components
plot_controls_card = dbc.Card([
    dbc.CardHeader("Plot Controls"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col(
                [
                    html.Label("Display"),
                    dbc.RadioItems(
                        id="plot-option",
                        options=[
                            {"label": "Overlay Files", "value": "overlay"},
                            {"label": "Separate Files", "value": "separate"}
                        ],
                        value="overlay",
                        className="mb-3"
                    ),
                    dbc.Button("Update Plot", id="plot-btn", color="success", className="w-100"),
                ],
                width=12
            ),
        ]),
        dbc.Row([
            dbc.Col(
                dbc.Button(
                    [html.I(className="bi bi-download me-2"), "Export Plot as HTML"],
                    id="export-plot-btn",
                    color="info",
                    outline=True,
                    className="mt-3 w-100",
                ),
                width="auto"
            ),
        ]),
    ])
])

# FFT controls card - updating default values
fft_controls_card = dbc.Card([
    dbc.CardHeader("FFT Controls"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Label("Averaging"),
                dcc.Dropdown(
                    id="fft-averaging",
                    options=[
                        {"label": "None", "value": "None"},
                        {"label": "Welch", "value": "Welch"},
                        {"label": "Binning", "value": "Binning"}
                    ],
                    value="Welch"  # Changed from "None" to "Welch"
                ),
            ], width=4),
            
            dbc.Col([
                html.Label("Windowing"),
                dcc.Dropdown(
                    id="fft-windowing",
                    options=[
                        {"label": "Hamming", "value": "hamming"},
                        {"label": "Hann", "value": "hann"},
                        {"label": "Rectangular", "value": "rectangular"}
                    ],
                    value="hamming"  # Default already set to hamming
                ),
            ], width=4),
            
            dbc.Col([
                html.Label("2^n Exponent"),
                dbc.Input(
                    id="fft-n-exp",
                    type="number",
                    min=1,
                    max=20,
                    step=1,
                    value=15  # Changed from 10 to 15
                ),
            ], width=4),
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Checklist(
                    options=[{"label": "Detrend", "value": "detrend"}],
                    value=["detrend"],  # Changed from [] to ["detrend"] to set default to True
                    id="fft-detrend",
                    inline=True,
                    className="mt-2"
                ),
            ], width=3),
            dbc.Col([
                html.Label("X-axis Limit (Hz)"),
                dbc.Input(
                    id="fft-x-limit",
                    type="number",
                    min=0.001,
                    step="any",
                    placeholder="Max frequency",
                    value=5  # Added default value of 5Hz
                ),
            ], width=3),
            dbc.Col([
                html.Label("X-axis Scale"),
                dbc.RadioItems(
                    id="fft-xscale",
                    options=[
                        {"label": "Log", "value": "log"},
                        {"label": "Linear", "value": "linear"}
                    ],
                    value="linear",  # Changed from "log" to "linear"
                    inline=True
                ),
            ], width=3),
            dbc.Col([
                html.Label("Plot Style"),
                dbc.RadioItems(
                    id="fft-plot-style",
                    options=[
                        {"label": "Separate", "value": "separate"},
                        {"label": "Overlay", "value": "overlay"}
                    ],
                    value="separate",
                    inline=True
                ),
            ], width=3),
        ], className="mb-3"),
        
        # Add new annotations section
        dbc.Row([
            dbc.Col([
                html.Label("Frequency Annotations", className="mt-3 mb-1"),
                dbc.InputGroup([
                    dbc.Input(id="fft-annotation-freq", type="text", placeholder="Hz (comma separated)", size="sm"),
                    dbc.Input(id="fft-annotation-text", type="text", placeholder="Labels (comma separated)", size="sm"),
                    dbc.Button("Add", id="fft-add-annotation-btn", outline=True, color="secondary", size="sm"),
                ], size="sm"),
            ], width=12),
        ], className="mb-1"),
        
        # Badge display for current annotations
        dbc.Row([
            dbc.Col([
                html.Div(id="fft-annotations-display", className="mb-2")
            ], width=12),
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Button("Calculate FFT", id="fft-calculate-btn", color="success", className="w-100"),
            ], width=12),
        ]),
        
        dbc.Row([
            dbc.Col(
                dbc.Button(
                    [html.I(className="bi bi-download me-2"), "Export FFT as HTML"],
                    id="export-fft-btn",
                    color="info",
                    outline=True,
                    className="mt-3 w-100",
                ),
                width="auto"
            ),
        ]),
    ])
])

# Tooltip for displaying file information
file_info_tooltip = dbc.Tooltip(
    id="file-info-content",
    target="file-info-link",
    placement="bottom",
    style={"maxWidth": "600px"}
)

# Loading spinner for visual feedback during file loading
loading_spinner = dbc.Spinner(
    html.Div(id="loading-placeholder"),
    spinner_style={"width": "3rem", "height": "3rem"},
    color="primary",
    fullscreen=False,
)

# Create tabs for different features
tabs = dbc.Tabs(
    [
        dbc.Tab(
            [
                # Time domain plotting tab - No longer contains time range or signal selection
                dbc.Row([
                    dbc.Col([
                        plot_controls_card,
                        html.Div(loading_spinner, className="text-center my-3", id="loading-container", style={"display": "none"}),
                    ], width=12)
                ], className="mb-2"),
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            # Removed file info link from here
                            html.Div(id="plot-output")
                        ]),
                        width=12
                    )
                ]),
            ],
            label="Time Domain",
            tab_id="tab-time-domain",
        ),
        dbc.Tab(
            [
                # FFT Analysis tab - No longer contains signal selection
                dbc.Row([
                    dbc.Col(fft_controls_card, width=12)
                ], className="mb-2"),
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.Div(id="fft-plot-output")
                        ]),
                        width=12
                    )
                ]),
            ],
            label="FFT Analysis",
            tab_id="tab-fft",
        ),
    ],
    id="tabs",
    active_tab="tab-time-domain",
)

# Updated app layout to REMOVE the global export button at the top
app.layout = dbc.Container([
    # Data stores for maintaining state between callbacks
    dcc.Store(id="loaded-files", data={}),
    dcc.Store(id="file-path-list", data=[]),
    dcc.Store(id="current-plot-data", data={}),
    dcc.Store(id="current-figure", data=None),
    dcc.Store(id="current-fft-figure", data=None),
    dcc.Store(id="time-range-info", data={}),
    dcc.Store(id="fft-annotations", data=[]),
    
    # App title - removed global export button
    dbc.Row([
        dbc.Col(html.H2("Remote OpenFAST Plotter", className="my-2"), width="auto"),
        # REMOVED: dbc.Col(global_export_button, width="auto", className="d-flex align-items-center")
    ], className="mb-2"),
    
    # File input section
    dbc.Row([
        dbc.Col(file_input_card, width=12)
    ], className="mb-2"),
    
    # Global time range selection - Now just containing time range card (export card moved to top)
    dbc.Row([
        dbc.Col(time_range_card, width=12)
    ], className="mb-2"),
    
    # Global signal selection - Moved up, outside of tabs
    dbc.Row([
        dbc.Col(signal_selection_card, width=12)
    ], className="mb-2"),
    
    # Main content with tabs
    dbc.Row([
        dbc.Col(tabs, width=12)
    ]),
    
    file_info_tooltip,
    
    # Download components
    dcc.Download(id="download-html"),
    dcc.Download(id="download-fft-html"),
    # REMOVED: dcc.Download(id="download-all-html"),
    
    # Loading state store
    dcc.Store(id="is-loading", data=False),
], fluid=True)

# Global variable to store DataFrames in Python memory
# This avoids JSON serialization/deserialization overhead
DATAFRAMES = {}

#######################
# CALLBACKS
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

# Main callback for loading files
@app.callback(
    Output("loaded-files", "data"),
    Output("file-path-list", "data"),  # Changed from dataframes to file-path-list
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
    State("file-path-list", "data"),  # Changed from dataframes to file-path-list
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
    global DATAFRAMES
    
    trigger_id = ctx.triggered_id
    
    if trigger_id == "clear-files-btn":
        DATAFRAMES = {}  # Clear the global dictionary
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
            
        return (
            {"files": all_files},
            all_files,  # Return a list of file paths instead of DataFrame dict
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
            False,  # Loading done
            {}
        )

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

def create_file_pills(file_paths):
    """
    Create pills showing loaded files with unique identifiers.
    
    Parameters:
    -----------
    file_paths : list
        List of file paths
        
    Returns:
    --------
    dash component
        HTML div containing the file pills
    """
    if not file_paths:
        return html.Div()
    
    # Get unique identifiers for file paths
    path_identifiers = get_unique_identifiers(file_paths)
        
    pills = []
    for path in sorted(file_paths):
        # Use unique identifier instead of just filename
        display_name = path_identifiers[path]
        
        pills.append(
            dbc.Badge(
                display_name,
                color="light",
                text_color="primary",
                className="me-1 mb-1",
                pill=True,
                title=path  # Add full path as tooltip
            )
        )
    
    return html.Div(pills)

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
    global DATAFRAMES
    
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
                    if col.startswith(base_name):
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

# Modified: Update signal dropdowns callback - Now only reset time range when reset button is pressed
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
    This callback ONLY affects the time range controls, not signal selection.
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
    # Access DATAFRAMES without global keyword - it's already available to the function
    
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
            
            # Create card header with tooltip using an HTML div with data-bs-toggle
            header_with_tooltip = html.Div(
                [
                    path_identifiers[file_path],
                    # Create tooltip using Bootstrap's data attributes
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
    # Access DATAFRAMES without global keyword - it's already available to the function

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

# Modified FFT Analysis calculation to support overlay option and linear x-axis scale
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
    State("fft-detrend", "value"),
    State("fft-x-limit", "value"),
    State("fft-xscale", "value"),
    State("fft-plot-style", "value"),
    State("time-start", "value"),
    State("time-end", "value"),
    State("fft-annotations", "data"),
    prevent_initial_call=True
)
def calculate_fft(n_clicks, file_paths, time_col, signals, averaging, windowing, n_exp, detrend, x_limit, xscale, plot_style, start_time, end_time, annotations):
    """
    Calculate FFT for all selected signals across all files.
    
    This function:
    1. Retrieves the selected signals from all files
    2. Applies time range filtering if specified
    3. Calculates FFT using our custom module
    4. Creates plots of the FFT results
    """
    # Access DATAFRAMES without global keyword - it's already available to the function

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
                    import traceback
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
                
                # Add annotation text - positioned to the left of the line and within the plot area
                # Position the label at 90% of the plot height to avoid overlap with the title
                fig.add_annotation(
                    x=freq,
                    y=0.90,  # High in the plot, but not at the very top
                    yref="paper",
                    text=label,
                    showarrow=False,
                    textangle=0,  # Horizontal text
                    xanchor="right",  # Place text to the left of the frequency line
                    yanchor="middle",
                    font=dict(size=10),
                    bgcolor="rgba(255, 255, 255, 0.7)",  # Semi-transparent background
                    borderpad=2
                )
        
        # Update layout
        fig.update_layout(
            title='FFT Analysis - All Signals',
            xaxis_title='Frequency (Hz)',
            yaxis_title='Amplitude',
            height=600,
            margin=dict(l=50, r=20, t=60, b=50),
            xaxis_type=xscale,  # Use selected x-axis scale
            yaxis_type='log',
            showlegend=True,
            legend=dict(
                orientation="v", 
                yanchor="top", 
                y=0.98, 
                xanchor="right", 
                x=0.99
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
                    import traceback
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
                    
                    # Add annotation text - positioned to the left of the line and within the plot area
                    # Position the label at 90% of the plot height to avoid overlap with the title
                    fig.add_annotation(
                        x=freq,
                        y=0.90,  # High in the plot, but not at the very top
                        yref="paper",
                        text=label,
                        showarrow=False,
                        textangle=0,  # Horizontal text
                        xanchor="right",  # Place text to the left of the frequency line
                        yanchor="middle",
                        font=dict(size=10),
                        bgcolor="rgba(255, 255, 255, 0.7)",  # Semi-transparent background
                        borderpad=2
                    )
            
            # Update layout
            fig.update_layout(
                title=f'FFT Analysis of {signal}',
                xaxis_title='Frequency (Hz)',
                yaxis_title='Amplitude',
                height=500,
                margin=dict(l=50, r=20, t=60, b=50),
                xaxis_type=xscale,  # Use selected x-axis scale
                yaxis_type='log',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
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

# Add a callback for exporting FFT plot as HTML
@app.callback(
    Output("download-fft-html", "data"),
    Input("export-fft-btn", "n_clicks"),
    State("current-fft-figure", "data"),
    prevent_initial_call=True
)
def download_fft_html(export_clicks, current_fig):
    """Generate and download an HTML file of the current FFT plot."""
    if not export_clicks or current_fig is None:
        raise PreventUpdate
    
    # Use the stored figure
    fig = go.Figure(current_fig)
    
    # Generate the HTML content
    html_str = fig.to_html(include_plotlyjs='cdn')
    
    # Create timestamp for filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"openfast_fft_{timestamp}.html"
    
    # Return the content as a download
    return dict(
        content=html_str,
        filename=filename
    )

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
    
    This callback handles:
    1. Adding new frequency annotations when the Add button is clicked
    2. Clearing annotations when switching to the FFT tab
    3. Validating frequency input to ensure it's numerical
    4. Auto-generating labels if not provided
    
    Parameters:
    -----------
    add_clicks : int
        Number of times the add button has been clicked
    active_tab : str
        Currently active tab ID
    freq_input : str
        Comma-separated list of frequencies to annotate
    label_input : str
        Comma-separated list of labels for annotations
    current_annotations : list
        List of current annotation objects
    
    Returns:
    --------
    (list, list, str, str): 
        - Updated annotations data
        - Updated annotations display badges
        - Cleared frequency input
        - Cleared label input
    """
    trigger = ctx.triggered_id
    
    # Reset when switching to FFT tab
    if trigger == "tabs" and active_tab == "tab-fft":
        return [], [], None, None
    
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
    
    # Create badges for visual display
    badges = create_annotation_badges(new_annotations)
    
    return new_annotations, badges, None, None

def create_annotation_badges(annotations):
    """
    Create badge components for annotation display
    
    Generates interactive Bootstrap badges for each annotation with a 
    delete button that allows removing individual annotations.
    
    Parameters:
    -----------
    annotations : list of dict
        List of annotation objects, each with 'freq' and 'label' keys
    
    Returns:
    --------
    list
        List of dbc.Badge components
    """
    if not annotations:
        return []
    
    badges = []
    for i, anno in enumerate(annotations):
        badges.append(
            dbc.Badge(
                [
                    f"{anno['label']}: {anno['freq']} Hz",
                    html.I(
                        className="bi bi-x ms-1",
                        id={"type": "remove-annotation", "index": i},
                        style={"cursor": "pointer"}
                    )
                ],
                color="info",
                className="me-1 mb-1"
            )
        )
    return badges

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
    
    This callback uses pattern-matching to identify which annotation's
    delete button was clicked, and removes that annotation from the list.
    
    Parameters:
    -----------
    n_clicks : list of int
        Number of clicks for each remove button
    current_annotations : list
        List of current annotation objects
    
    Returns:
    --------
    (list, list):
        - Updated annotations data with the selected annotation removed
        - Updated annotation badges display
    """
    if not any(n_clicks):
        raise PreventUpdate
    
    # Find which annotation to remove
    triggered_id = ctx.triggered_id
    if triggered_id and "index" in triggered_id:
        index_to_remove = triggered_id["index"]
        
        # Remove the annotation
        new_annotations = [a for i, a in enumerate(current_annotations) if i != index_to_remove]
        
        # Update badges
        badges = create_annotation_badges(new_annotations)
        
        return new_annotations, badges
    
    raise PreventUpdate

#######################
# RUN THE APP
#######################

def run_server_with_retry(app, host='localhost', port=8050, max_retries=5):
    """
    Run the Dash server with automatic retry on port conflicts.
    
    Parameters:
    -----------
    app : dash.Dash
        The Dash application instance
    host : str
        Host to bind the server to
    port : int
        Initial port to try
    max_retries : int
        Maximum number of port increments to try
    
    """
    import socket
    import time
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"Port {port-1} is in use. Trying port {port}...")
            print(f"\nStarting Remote OpenFAST Plotter on http://{host}:{port}/")
            print("Press Ctrl+C to abort the application.")
            app.run(debug=True, host=host, port=port)
            break
        except OSError as e:
            # Socket error - port likely in use
            if "Address already in use" in str(e):
                port += 1
                time.sleep(2)  # Wait before trying the next port
            else:
                # Some other socket error, re-raise
                raise
    else:
        # We've exhausted our retries
        print(f"Could not find an available port after {max_retries} attempts.")
        print(f"Please specify a different port using the --port argument.")

if __name__ == "__main__":
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Remote OpenFAST Plotter')
    parser.add_argument('--host', default='localhost', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=8050, help='Port to bind the server to')
    args = parser.parse_args()
    
    # Run the server with automatic retry
    run_server_with_retry(app, host=args.host, port=args.port)
