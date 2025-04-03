"""
UI Components for OpenFAST Plotter
Contains layout components and UI elements
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
import datetime
import socket
import getpass
import subprocess
from pathlib import Path
import os

def get_metadata():
    """Gather metadata for plot exports"""
    # Get current date and time
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get system info (NREL_CLUSTER or hostname)
    system_name = os.environ.get("NREL_CLUSTER", socket.gethostname())
    
    # Get username
    username = getpass.getuser()
    
    # Try to get git version info
    try:
        git_version = subprocess.check_output(
            ["git", "describe", "--abbrev=8", "--always", "--tags", "--dirty"],
            cwd=Path(__file__).parent,
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        git_version = "unknown"
    
    return {
        "datetime": now,
        "system": system_name,
        "user": username,
        "version": git_version
    }

# Loading spinner for visual feedback during file loading
loading_spinner = dbc.Spinner(
    html.Div(id="loading-placeholder"),
    spinner_style={"width": "3rem", "height": "3rem"},
    color="primary",
    fullscreen=False,
)

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

# Time range selection component
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

# Signal selection component
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

# Plot controls card for time-domain plotting
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
        # Add metadata info that will be included in exports
        dbc.Row([
            dbc.Col(
                html.Small(
                    "Exports include metadata: date/time, system, user, and version info",
                    className="text-muted mt-2"
                ),
                width=12
            )
        ])
    ])
])

# FFT controls card
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
                    value="Welch"
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
                    value="hamming"
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
                    value=15
                ),
            ], width=4),
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                html.Label("X-axis Scale"),
                dbc.RadioItems(
                    id="fft-xscale",
                    options=[
                        {"label": "Log", "value": "log"},
                        {"label": "Linear", "value": "linear"}
                    ],
                    value="linear",
                    inline=True
                ),
            ], width=4),
            
            dbc.Col([
                html.Label("Plot Style"),
                dcc.Dropdown(
                    id="fft-plot-style",
                    options=[
                        {"label": "Separate", "value": "separate"},
                        {"label": "Overlay", "value": "overlay"}
                    ],
                    value="separate"
                ),
            ], width=4),
            
            dbc.Col([
                html.Label("X-axis Limit (Hz)"),
                dbc.Input(
                    id="fft-x-limit",
                    type="number",
                    min=0.001,
                    step="any",
                    placeholder="Max frequency",
                    value=5
                ),
            ], width=4),
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Checklist(
                    options=[{"label": "Detrend", "value": "detrend"}],
                    value=["detrend"],
                    id="fft-detrend",
                    inline=True,
                    className="mt-2 mb-3"
                ),
            ], width=12),
        ]),
        
        # Annotations section
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
        
        # Rotor RPM input
        dbc.Row([
            dbc.Col([
                html.Label("Rotor RPM", className="mt-3 mb-1"),
                dbc.InputGroup([
                    dbc.Input(
                        id="rotor-rpm-input",
                        type="number",
                        placeholder="Enter rotor RPM",
                        step="any",
                        min=0
                    ),
                    dbc.InputGroupText("RPM"),
                    dbc.Button("Add Harmonics", id="add-harmonics-btn", outline=True, color="secondary", size="sm"),
                ], size="sm"),
            ], width=12),
        ], className="mb-3"),
        
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
        # Add metadata info that will be included in exports
        dbc.Row([
            dbc.Col(
                html.Small(
                    "Exports include metadata: date/time, system, user, and version info",
                    className="text-muted mt-2"
                ),
                width=12
            )
        ])
    ])
])

# Tooltip for displaying file information
file_info_tooltip = dbc.Tooltip(
    id="file-info-content",
    target="file-info-link",
    placement="bottom",
    style={"maxWidth": "600px"}
)

# Create tabs for different features
def create_tabs():
    """Create tabbed interface for the application"""
    return dbc.Tabs(
        [
            dbc.Tab(
                [
                    dbc.Row([
                        dbc.Col([
                            plot_controls_card,
                            html.Div(loading_spinner, className="text-center my-3", id="loading-container", style={"display": "none"}),
                        ], width=12)
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col(
                            html.Div(id="plot-output"),
                            width=12
                        )
                    ]),
                ],
                label="Time Domain",
                tab_id="tab-time-domain",
            ),
            dbc.Tab(
                [
                    dbc.Row([
                        dbc.Col(fft_controls_card, width=12)
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col(
                            html.Div(id="fft-plot-output"),
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

def create_layout():
    """Create the main application layout"""
    return dbc.Container([
        # Data stores for maintaining state between callbacks
        dcc.Store(id="loaded-files", data={}),
        dcc.Store(id="file-path-list", data=[]),
        dcc.Store(id="current-plot-data", data={}),
        dcc.Store(id="current-figure", data=None),
        dcc.Store(id="current-fft-figure", data=None),
        dcc.Store(id="time-range-info", data={}),
        dcc.Store(id="fft-annotations", data=[]),
        dcc.Store(id="plot-metadata", data=get_metadata()),  # Store metadata for exports
        
        # App title
        dbc.Row([
            dbc.Col(html.H2("Remote OpenFAST Plotter", className="my-2"), width="auto"),
            dbc.Col(html.Small(f"v{get_metadata()['version']}", className="text-muted pt-3"), width="auto")
        ], className="mb-2"),
        
        # File input section
        dbc.Row([
            dbc.Col(file_input_card, width=12)
        ], className="mb-2"),
        
        # Global time range selection
        dbc.Row([
            dbc.Col(time_range_card, width=12)
        ], className="mb-2"),
        
        # Global signal selection
        dbc.Row([
            dbc.Col(signal_selection_card, width=12)
        ], className="mb-2"),
        
        # Main content with tabs
        dbc.Row([
            dbc.Col(create_tabs(), width=12)
        ]),
        
        file_info_tooltip,
        
        # Download components
        dcc.Download(id="download-html"),
        dcc.Download(id="download-fft-html"),
        
        # Loading state store
        dcc.Store(id="is-loading", data=False),
    ], fluid=True)
