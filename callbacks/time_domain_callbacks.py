"""
Time domain plotting callbacks for OpenFAST Plotter
Contains callbacks for creating time domain plots
"""

import uuid
import pandas as pd

from dash import Input, Output, State, html, dcc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# Import local modules
from data_manager import DATAFRAMES
from utils import draw_graph, get_unique_identifiers


def register_time_domain_callbacks(app):
    """Register time domain plotting callbacks with the Dash app"""
    
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
