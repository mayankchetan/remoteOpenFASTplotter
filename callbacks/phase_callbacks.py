"""
Phase/Magnitude analysis callbacks for OpenFAST Plotter
Contains callbacks for phase/magnitude calculation, plotting, and peak selection
"""

from tools.phase_analysis import compute_phase_fft, find_peaks
import os
import sys
import traceback
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.colors
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots

from dash import Input, Output, State, html, dcc, MATCH, ALL, ctx, no_update
from dash.exceptions import PreventUpdate

# Import local modules
from data_manager import DATAFRAMES
from utils import get_unique_identifiers
from html_exporter import prepare_html_for_export, export_figures_from_plotly_objects

# Import phase analysis module
sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)),
        'tools'))


def register_phase_callbacks(app):
    """Register phase/magnitude analysis callbacks with the Dash app"""

    # Phase/Magnitude Analysis calculation
    @app.callback(
        Output("phase-plot-output", "children"),
        Output("current-phase-figure", "data"),
        Output("peak-table-container", "children", allow_duplicate=True),
        Output("selected-peaks", "data", allow_duplicate=True),
        Output("phase-raw-data", "data"),
        Input("phase-calculate-btn", "n_clicks"),
        State("file-path-list", "data"),
        State("signalx", "value"),
        State("signaly", "value"),
        State("phase-n-exp", "value"),
        State("phase-plot-style", "value"),
        State("phase-detrend", "value"),
        State("phase-x-limit", "value"),
        State("phase-xscale", "value"),
        State("time-start", "value"),
        State("time-end", "value"),
        State("selected-peaks", "data"),
        prevent_initial_call=True
    )
    def calculate_phase_fft(
            n_clicks,
            file_paths,
            time_col,
            signals,
            n_exp,
            plot_style,
            detrend,
            x_limit,
            xscale,
            start_time,
            end_time,
            existing_peaks):
        """
        Calculate Phase/Magnitude FFT for all selected signals across all files.

        This function:
        1. Retrieves the selected signals from all files
        2. Applies time range filtering if specified
        3. Calculates FFT with phase information using our custom module
        4. Creates plots for magnitude and phase results
        5. Creates an empty peak table or preserves existing selected peaks
        """
        if not n_clicks:
            raise PreventUpdate

        if not file_paths or not DATAFRAMES:
            return html.Div(
                "No files loaded", className="text-center p-5 text-muted"), None, no_update, no_update, {}

        if not time_col:
            return html.Div("Please select a time column (X Signal)", style={
                            "color": "red"}), None, no_update, no_update, {}

        if not signals or len(signals) == 0:
            return html.Div("Please select at least one signal (Y Signal)", style={
                            "color": "red"}), None, no_update, no_update, {}

        # Convert detrend flag
        detrend_bool = "detrend" in detrend  # Convert from list to bool

        figures = []
        panels = []

        # Create a dictionary to store the raw FFT data for reliable lookup
        raw_data = {}

        # OVERLAY PLOT STYLE - All signals in a single figure pair
        if (plot_style == "overlay"):
            # Create a subplot figure with two rows (magnitude and phase)
            fig = make_subplots(
                rows=2,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=(
                    "Magnitude Analysis - All Signals",
                    "Phase Analysis - All Signals"))

            # Process each signal for each file
            for signal_idx, signal in enumerate(signals):
                for file_idx, file_path in enumerate(file_paths):
                    if file_path not in DATAFRAMES:
                        continue

                    df = DATAFRAMES[file_path]

                    if signal not in df.columns or time_col not in df.columns:
                        continue

                    try:
                        # Use our custom Phase FFT implementation
                        fft_result = compute_phase_fft(
                            df,
                            signal,
                            time_col=time_col,
                            start_time=start_time,
                            end_time=end_time,
                            n_exp=n_exp,
                            detrend=detrend_bool
                        )

                        # Extract results
                        freq = fft_result.freq
                        mag = fft_result.magnitude
                        phase = fft_result.phase

                        # Get file identifier for legend
                        file_identifiers = get_unique_identifiers(file_paths)
                        file_name = file_identifiers.get(
                            file_path, os.path.basename(file_path))

                        # Create trace name for consistent identification
                        trace_name = f"{signal} - {file_name}"

                        # Store raw data for reliable lookup
                        raw_data[trace_name] = {
                            "freq": freq.tolist(),
                            "mag": mag.tolist(),
                            "phase": phase.tolist()
                        }

                        # Create a color palette for signals
                        color_idx = signal_idx % len(
                            plotly.colors.DEFAULT_PLOTLY_COLORS)
                        base_color = plotly.colors.DEFAULT_PLOTLY_COLORS[color_idx]

                        # Create line style variations for different files
                        line_styles = ['solid', 'dash', 'dot', 'dashdot']
                        line_style = line_styles[file_idx % len(line_styles)]

                        # Add magnitude trace to figure (top subplot)
                        fig.add_trace(
                            go.Scatter(
                                x=freq,
                                y=mag,
                                mode='lines',
                                line=dict(
                                    color=base_color,
                                    dash=line_style if line_style != 'solid' else None),
                                name=trace_name,
                                legendgroup=trace_name,
                                hovertemplate=f"<b>{file_name}</b><br>" +
                                f"<b>Signal:</b> {signal}<br>" +
                                f"<b>Frequency:</b> %{{x:.4g}} Hz<br>" +
                                f"<b>Magnitude:</b> %{{y:.4g}}<extra></extra>"),
                            row=1,
                            col=1)

                        # Add phase trace to figure (bottom subplot)
                        fig.add_trace(
                            go.Scatter(
                                x=freq,
                                y=phase,
                                mode='lines',
                                line=dict(
                                    color=base_color,
                                    dash=line_style if line_style != 'solid' else None
                                ),
                                name=trace_name,
                                legendgroup=trace_name,
                                showlegend=False,  # Don't show duplicate legend entries
                                hovertemplate=f"<b>{file_name}</b><br>" +
                                f"<b>Signal:</b> {signal}<br>" +
                                f"<b>Frequency:</b> %{{x:.4g}} Hz<br>" +
                                f"<b>Phase:</b> %{{y:.4g}} rad<extra></extra>"
                            ),
                            row=2, col=1
                        )
                    except Exception as e:
                        print(
                            f"Error in Phase/Magnitude calculation for {file_path}, signal {signal}: {e}")
                        print(traceback.format_exc())
                        continue

            # Update layout for magnitude subplot (top)
            fig.update_yaxes(title_text="Magnitude", type="log", row=1, col=1)

            # Update layout for phase subplot (bottom)
            fig.update_yaxes(title_text="Phase (rad)", row=2, col=1)

            # Update shared x-axis
            fig.update_xaxes(
                title_text="Frequency (Hz)",
                type=xscale,
                row=2,
                col=1)

            # Apply x-axis limit if specified
            if x_limit and xscale == 'log':
                fig.update_xaxes(range=[np.log10(0.001), np.log10(x_limit)])
            elif x_limit:
                fig.update_xaxes(range=[0, x_limit])

            # Update overall layout
            fig.update_layout(
                height=800,  # Taller to accommodate both plots
                margin=dict(l=50, r=150, t=50, b=50),
                showlegend=True,
                legend=dict(
                    orientation='v',
                    yanchor='middle',
                    xanchor='left',
                    x=1.02,
                    y=0.5
                ),
                clickmode='event'  # Enable click events for peak selection
            )

            # Store subplot data structure for click handling
            subplot_data = {
                'magnitude_subplot': {'row': 1, 'col': 1},
                'phase_subplot': {'row': 2, 'col': 1}
            }

            # Store the figure for later use
            figures = [fig, subplot_data]

            # Create layout with the combined plot
            layout = html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Phase/Magnitude Analysis"),
                            dbc.CardBody(dcc.Graph(figure=fig, id="combined-phase-mag-graph", config={'displayModeBar': True}))
                        ])
                    ], width=12)
                ])
            ])

            # Create empty peak table or preserve existing
            if not existing_peaks or len(existing_peaks) == 0:
                peak_table = html.Div([
                    dbc.Alert("Click on peaks in either the magnitude or phase plot to select them. Selected peaks will appear here.", color="info"),
                    dbc.Table([
                        html.Thead(html.Tr([
                            html.Th("Frequency (Hz)"),
                            html.Th("Magnitude"),
                            html.Th("Phase (rad)"),
                            html.Th("Signal"),
                            html.Th("Actions")
                        ])),
                        html.Tbody(id="peak-table-body")
                    ], bordered=True, hover=True, responsive=True, id="peak-data-table", className="mt-3")
                ])
            else:
                # Keep existing peak table
                peak_table = no_update

            return layout, figures, peak_table, existing_peaks, raw_data

        # SEPARATE PLOT STYLE - One plot pair per signal
        else:
            for signal in signals:
                # Create a subplot figure with two rows (magnitude and phase)
                fig = make_subplots(
                    rows=2,
                    cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.1,
                    subplot_titles=(
                        f"Magnitude Analysis: {signal}",
                        f"Phase Analysis: {signal}"))

                file_results = []

                # Process each file
                for i, file_path in enumerate(file_paths):
                    if file_path not in DATAFRAMES:
                        continue

                    df = DATAFRAMES[file_path]

                    if signal not in df.columns or time_col not in df.columns:
                        continue

                    try:
                        # Use our custom Phase FFT implementation
                        fft_result = compute_phase_fft(
                            df,
                            signal,
                            time_col=time_col,
                            start_time=start_time,
                            end_time=end_time,
                            n_exp=n_exp,
                            detrend=detrend_bool
                        )

                        # Extract results
                        freq = fft_result.freq
                        mag = fft_result.magnitude
                        phase = fft_result.phase

                        # Store for later use
                        file_results.append({
                            'file_path': file_path,
                            'freq': freq,
                            'mag': mag,
                            'phase': phase,
                            'fft_result': fft_result
                        })

                        # Get file identifier for legend
                        file_identifiers = get_unique_identifiers(file_paths)
                        file_name = file_identifiers.get(
                            file_path, os.path.basename(file_path))

                        # Create trace name for consistent identification
                        trace_name = file_name

                        # Store raw data for reliable lookup
                        raw_data[f"{signal} - {trace_name}"] = {
                            "freq": freq.tolist(),
                            "mag": mag.tolist(),
                            "phase": phase.tolist()
                        }

                        # Add magnitude trace to figure (top subplot)
                        fig.add_trace(
                            go.Scatter(
                                x=freq,
                                y=mag,
                                mode='lines',
                                line=dict(color=plotly.colors.DEFAULT_PLOTLY_COLORS[i % len(plotly.colors.DEFAULT_PLOTLY_COLORS)]),
                                name=trace_name,
                                legendgroup=trace_name,
                                hovertemplate=f"<b>{file_name}</b><br>" +
                                f"<b>Signal:</b> {signal}<br>" +
                                f"<b>Frequency:</b> %{{x:.4g}} Hz<br>" +
                                f"<b>Magnitude:</b> %{{y:.4g}}<extra></extra>"
                            ),
                            row=1, col=1
                        )

                        # Add phase trace to figure (bottom subplot)
                        fig.add_trace(
                            go.Scatter(
                                x=freq,
                                y=phase,
                                mode='lines',
                                line=dict(color=plotly.colors.DEFAULT_PLOTLY_COLORS[i % len(
                                    plotly.colors.DEFAULT_PLOTLY_COLORS)]),
                                name=trace_name,
                                legendgroup=trace_name,
                                showlegend=False,  # Don't show duplicate legend entries
                                hovertemplate=f"<b>{file_name}</b><br>" +
                                f"<b>Signal:</b> {signal}<br>" +
                                f"<b>Frequency:</b> %{{x:.4g}} Hz<br>" +
                                f"<b>Phase:</b> %{{y:.4g}} rad<extra></extra>"
                            ),
                            row=2, col=1
                        )
                    except Exception as e:
                        print(
                            f"Error in Phase/Magnitude calculation for {file_path}, signal {signal}: {e}")
                        print(traceback.format_exc())
                        continue

                if not file_results:
                    continue

                # Update layout for magnitude subplot (top)
                fig.update_yaxes(
                    title_text="Magnitude", type="log", row=1, col=1)

                # Update layout for phase subplot (bottom)
                fig.update_yaxes(title_text="Phase (rad)", row=2, col=1)

                # Update shared x-axis
                fig.update_xaxes(title_text="Frequency (Hz)",
                                 type=xscale, row=2, col=1)

                # Apply x-axis limit if specified
                if x_limit and xscale == 'log':
                    fig.update_xaxes(
                        range=[
                            np.log10(0.001),
                            np.log10(x_limit)],
                        row=1,
                        col=1)
                    fig.update_xaxes(
                        range=[
                            np.log10(0.001),
                            np.log10(x_limit)],
                        row=2,
                        col=1)
                elif x_limit:
                    fig.update_xaxes(range=[0, x_limit], row=1, col=1)
                    fig.update_xaxes(range=[0, x_limit], row=2, col=1)

                # Update overall layout
                fig.update_layout(
                    height=800,  # Taller to accommodate both plots
                    margin=dict(l=50, r=150, t=60, b=50),
                    showlegend=True,
                    legend=dict(
                        orientation='v',
                        yanchor='middle',
                        xanchor='left',
                        x=1.02,
                        y=0.5
                    ),
                    clickmode='event'  # Enable click events for peak selection
                )

                # Store subplot data for click handling
                subplot_data = {
                    'magnitude_subplot': {'row': 1, 'col': 1},
                    'phase_subplot': {'row': 2, 'col': 1}
                }

                # Store figures
                figures.append([fig, subplot_data])

                # Add the graph to the panel
                panels.append(
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader(f"Phase/Magnitude Analysis: {signal}"),
                                    dbc.CardBody(dcc.Graph(
                                        figure=fig,
                                        id={"type": "combined-graph", "signal": signal},
                                        config={'displayModeBar': True}
                                    ))
                                ])
                            ], width=12, className="mb-4")
                        ])
                    ])
                )

            if not panels:
                return html.Div("No valid Phase/Magnitude results could be calculated. Please check your signal selections.",
                                className="alert alert-warning"), None, no_update, no_update, {}

            # Create empty peak table
            if not existing_peaks or len(existing_peaks) == 0:
                peak_table = html.Div([
                    dbc.Alert("Click on peaks in either the magnitude or phase plot to select them. Selected peaks will appear here.", color="info"),
                    dbc.Table([
                        html.Thead(html.Tr([
                            html.Th("Frequency (Hz)"),
                            html.Th("Magnitude"),
                            html.Th("Phase (rad)"),
                            html.Th("Signal"),
                            html.Th("Actions")
                        ])),
                        html.Tbody(id="peak-table-body")
                    ], bordered=True, hover=True, responsive=True, id="peak-data-table", className="mt-3")
                ])
            else:
                # Keep existing peak table
                peak_table = no_update

            # Return the layout with all panels and the first figure for export
            return html.Div(
                panels), figures[0] if figures else None, peak_table, existing_peaks, raw_data

    # Peak detection callback
    @app.callback(
        Output("selected-peaks", "data"),
        Input("find-peaks-btn", "n_clicks"),
        State("current-phase-figure", "data"),
        State("peak-prominence", "value"),
        prevent_initial_call=True
    )
    def detect_peaks(n_clicks, figures, prominence):
        """Auto-detect peaks in the magnitude spectrum using scipy.signal.find_peaks"""
        if not n_clicks or not figures:
            raise PreventUpdate

        try:
            # With our new subplot structure, figures[0] is the combined figure
            # and figures[1] contains subplot information
            fig = figures[0]

            # We need to extract traces from the magnitude subplot (row 1, col
            # 1)
            magnitude_traces = []
            for trace in fig['data']:
                # Check if this trace belongs to the magnitude subplot (row 1,
                # col 1)
                if trace.get(
                        'xaxis',
                        'x') == 'x' and trace.get(
                        'yaxis',
                        'y') == 'y':
                    magnitude_traces.append(trace)

            # We need to find the trace with the highest peak for detection
            max_peak_height = 0
            best_trace = None

            for trace in magnitude_traces:
                # Handle different possible data formats safely
                x_array = []
                y_array = []

                if 'x' in trace:
                    if isinstance(trace['x'], list):
                        x_array = trace['x']
                    elif isinstance(trace['x'], np.ndarray):
                        x_array = trace['x'].tolist()
                    else:
                        # Skip this trace if we can't get x values
                        continue

                if 'y' in trace:
                    if isinstance(trace['y'], list):
                        y_array = trace['y']
                    elif isinstance(trace['y'], np.ndarray):
                        y_array = trace['y'].tolist()
                    else:
                        # Skip this trace if we can't get y values
                        continue

                # Ensure we have valid data
                if not x_array or not y_array:
                    continue

                # Convert to numpy arrays for calculation
                x_np = np.array(x_array)
                y_np = np.array(y_array)

                if len(y_np) > 0 and np.max(y_np) > max_peak_height:
                    max_peak_height = np.max(y_np)
                    best_trace = {'x': x_np, 'y': y_np, 'name': trace['name']}

            if not best_trace:
                print("No valid traces found for peak detection")
                return []

            # Find peaks in the best trace
            peaks = find_peaks(
                best_trace['x'],
                best_trace['y'],
                prominence=prominence)

            # Find corresponding phase values from the phase subplot (row 2, col 1)
            # Phase traces start at index len(magnitude_traces)
            phase_traces = []
            for trace in fig['data']:
                # Check if this trace belongs to the phase subplot (row 2, col
                # 1)
                if trace.get(
                        'xaxis',
                        'x') == 'x2' and trace.get(
                        'yaxis',
                        'y') == 'y2':
                    phase_traces.append(trace)

            # Find the matching phase trace with the same legendgroup/name
            phase_trace = None
            for trace in phase_traces:
                # Match based on legendgroup (which we set to be the same as
                # name)
                if trace.get('legendgroup') == best_trace['name'] or trace.get(
                        'name') == best_trace['name']:
                    # Handle different possible data formats safely
                    x_array = []
                    y_array = []

                    if 'x' in trace:
                        if isinstance(trace['x'], list):
                            x_array = trace['x']
                        elif isinstance(trace['x'], np.ndarray):
                            x_array = trace['x'].tolist()
                        else:
                            continue

                    if 'y' in trace:
                        if isinstance(trace['y'], list):
                            y_array = trace['y']
                        elif isinstance(trace['y'], np.ndarray):
                            y_array = trace['y'].tolist()
                        else:
                            continue

                    # Ensure we have valid data
                    if x_array and y_array:
                        phase_trace = {
                            'x': np.array(x_array),
                            'y': np.array(y_array)}
                        break

            if not phase_trace:
                print("No matching phase trace found")
                return []

            # Create peak data with interpolated phase values
            peak_data = []

            for i, freq in enumerate(peaks['frequencies']):
                # Find closest point in the phase data
                idx = np.abs(phase_trace['x'] - freq).argmin()
                phase_val = phase_trace['y'][idx]

                peak_data.append({
                    'frequency': float(freq),
                    'magnitude': float(peaks['magnitudes'][i]),
                    'phase': float(phase_val),
                    'trace': best_trace['name']
                })

            # Sort by frequency
            peak_data.sort(key=lambda x: x['frequency'])

            return peak_data

        except Exception as e:
            print(f"Error in peak detection: {e}")
            print(traceback.format_exc())
            return []

    # Peak selection callback from plot click
    @app.callback(
        Output("selected-peaks", "data", allow_duplicate=True),
        Input("combined-phase-mag-graph", "clickData"),
        Input({"type": "combined-graph", "signal": ALL}, "clickData"),
        State("phase-raw-data", "data"),
        State("current-phase-figure", "data"),
        State("selected-peaks", "data"),
        prevent_initial_call=True
    )
    def select_peak_from_click(
            main_combined_click,
            separate_combined_clicks,
            raw_data,
            figures,
            existing_peaks):
        """
        Add a peak to the selected peaks when a user clicks on either magnitude or phase plot

        This function identifies which plot was clicked (magnitude or phase), extracts the
        clicked frequency, and finds corresponding values from all traces at that frequency
        to create a complete comparison table.
        """
        if not figures or not raw_data:
            raise PreventUpdate

        click_data = None
        is_phase_plot = False  # Flag to identify if a phase plot was clicked
        signal_name = None

        # Determine which graph was clicked
        trigger_id = ctx.triggered_id

        if trigger_id == "combined-phase-mag-graph" and main_combined_click:
            click_data = main_combined_click
            # Determine if the click was in the phase subplot by checking curveNumber and y-axis
            # Points in phase subplot have yaxis = 'y2'
            if 'points' in main_combined_click and len(
                    main_combined_click['points']) > 0:
                if main_combined_click['points'][0].get('yaxis') == 'y2':
                    is_phase_plot = True
        elif any(separate_combined_clicks):
            # Find which combined graph was clicked
            for i, click in enumerate(separate_combined_clicks):
                if click is not None:
                    click_data = click
                    signal_name = ctx.triggered_id.get('signal', '')
                    # Determine if the click was in the phase subplot by
                    # checking yaxis
                    if 'points' in click and len(click['points']) > 0:
                        if click['points'][0].get('yaxis') == 'y2':
                            is_phase_plot = True
                    break

        if not click_data:
            raise PreventUpdate

        try:
            # Extract clicked point data
            point = click_data['points'][0]
            freq = float(point['x'])  # Clicked frequency is always on x-axis
            curve_number = int(point['curveNumber'])

            print(
                f"Click point: freq={freq}, curve_number={curve_number}, is_phase_plot={is_phase_plot}")

            # Get the trace name of the clicked curve
            clicked_trace_name = None

            # With the new subplot structure, we need to determine which trace
            # was clicked differently
            if isinstance(
                    figures[0],
                    dict):  # For combined plot (overlay mode)
                fig = figures[0]
                # The order in data is: [mag traces...], [phase traces...]
                # For phase subplot, need to adjust curve number to account for
                # magnitude traces
                if is_phase_plot:
                    # Count magnitude traces (those with yaxis='y')
                    mag_trace_count = sum(
                        1 for trace in fig['data'] if trace.get(
                            'yaxis', 'y') == 'y')
                    # Ensure curve_number is within bounds
                    if curve_number >= 0 and curve_number < len(
                            fig['data']) - mag_trace_count:
                        # The phase trace index = magnitude trace count +
                        # curve_number
                        phase_trace_idx = mag_trace_count + curve_number
                        clicked_trace_name = fig['data'][phase_trace_idx].get(
                            'name', '')
                        # Use legendgroup if available (consistent naming)
                        if not clicked_trace_name:
                            clicked_trace_name = fig['data'][phase_trace_idx].get(
                                'legendgroup', '')
                else:
                    # For magnitude subplot, just use the curve number directly
                    if curve_number >= 0 and curve_number < len(fig['data']):
                        clicked_trace_name = fig['data'][curve_number].get(
                            'name', '')
                        # Use legendgroup if available
                        if not clicked_trace_name:
                            clicked_trace_name = fig['data'][curve_number].get(
                                'legendgroup', '')
            else:  # For separate plots (one per signal)
                # Find which figure was clicked based on signal name
                fig_idx = 0
                if signal_name:
                    for i, fig_pair in enumerate(figures):
                        if isinstance(fig_pair[0], dict):
                            subplot_titles = fig_pair[0].get(
                                'layout', {}).get('annotations', [])
                            for title in subplot_titles:
                                if title.get('text', '').endswith(signal_name):
                                    fig_idx = i
                                    break

                if fig_idx < len(figures) and len(figures[fig_idx]) > 0:
                    fig = figures[fig_idx][0]  # The actual figure object

                    # The order in data is: [mag traces...], [phase traces...]
                    if is_phase_plot:
                        # Count magnitude traces (those with yaxis='y')
                        mag_trace_count = sum(
                            1 for trace in fig['data'] if trace.get(
                                'yaxis', 'y') == 'y')
                        # The phase trace index = magnitude trace count +
                        # curve_number
                        if curve_number >= 0 and curve_number < len(
                                fig['data']) - mag_trace_count:
                            phase_trace_idx = mag_trace_count + curve_number
                            clicked_trace_name = fig['data'][phase_trace_idx].get(
                                'name', '')
                            # Use legendgroup if available
                            if not clicked_trace_name:
                                clicked_trace_name = fig['data'][phase_trace_idx].get(
                                    'legendgroup', '')
                    else:
                        # For magnitude subplot
                        if curve_number >= 0 and curve_number < len(
                                fig['data']):
                            clicked_trace_name = fig['data'][curve_number].get(
                                'name', '')
                            # Use legendgroup if available
                            if not clicked_trace_name:
                                clicked_trace_name = fig['data'][curve_number].get(
                                    'legendgroup', '')

                    # For separate mode, need to add signal name to trace name
                    # for lookup
                    if signal_name and clicked_trace_name and not clicked_trace_name.startswith(
                            signal_name):
                        clicked_trace_name = f"{signal_name} - {clicked_trace_name}"

            if not clicked_trace_name:
                print("Could not determine trace name from click data")
                return existing_peaks or []

            print(f"Identified clicked trace: {clicked_trace_name}")

            # Create a list of new peaks - one for each trace at the clicked
            # frequency
            new_peaks = []
            frequency_label = f"{freq:.4f}"

            # Collect data from all traces at this frequency
            for trace_name, trace_data in raw_data.items():
                try:
                    # Convert to numpy arrays for lookup
                    freq_array = np.array(trace_data['freq'])
                    mag_array = np.array(trace_data['mag'])
                    phase_array = np.array(trace_data['phase'])

                    # Find the closest frequency in this trace's data
                    idx = np.argmin(np.abs(freq_array - freq))

                    # Check if the frequency is reasonably close
                    # (only include if within 1% of the clicked frequency)
                    if abs(freq_array[idx] - freq) / freq > 0.01:
                        continue

                    # Get the exact values for this trace
                    exact_freq = freq_array[idx]
                    magnitude = mag_array[idx]
                    phase_val = phase_array[idx]

                    # Create a peak entry for this trace
                    new_peak = {
                        'frequency': exact_freq,
                        # Ensure it's a float for serialization
                        'magnitude': float(magnitude),
                        # Ensure it's a float for serialization
                        'phase': float(phase_val),
                        'trace': trace_name,
                        'frequency_label': frequency_label  # Group identifier for the comparison
                    }

                    # Only add if we have valid data
                    if not np.isnan(magnitude) and not np.isnan(phase_val):
                        new_peaks.append(new_peak)

                except Exception as e:
                    print(f"Error processing trace {trace_name}: {e}")
                    continue

            # Only proceed if we found at least one valid peak
            if not new_peaks:
                print(f"No valid data found at frequency {freq}")
                return existing_peaks or []

            # Sort the new peaks by magnitude (descending)
            new_peaks.sort(key=lambda x: x['magnitude'], reverse=True)

            # Check if we already have peaks at this frequency
            peaks = existing_peaks or []
            existing_freq_labels = set(
                peak.get(
                    'frequency_label',
                    '') for peak in peaks)

            # If this frequency group already exists, remove all peaks with
            # this label
            if frequency_label in existing_freq_labels:
                peaks = [
                    peak for peak in peaks if peak.get(
                        'frequency_label',
                        '') != frequency_label]

            # Add all the new peaks
            peaks.extend(new_peaks)

            # Sort by frequency first, then by trace name
            peaks.sort(
                key=lambda x: (
                    x.get(
                        'frequency', 0), x.get(
                        'trace', '')))

            return peaks

        except Exception as e:
            print(f"Error in peak selection: {e}")
            print(f"Click data structure: {click_data}")
            print(traceback.format_exc())
            return existing_peaks or []

    # Update the peak table based on selected peaks
    @app.callback(
        Output("peak-table-container", "children"),
        Input("selected-peaks", "data"),
        prevent_initial_call=True
    )
    def update_peak_table(peaks):
        """Update the peak data table with the current selected peaks"""
        if not peaks:
            table = html.Div([
                dbc.Alert("Click on peaks in either the magnitude or phase plot to select them. Selected peaks will appear here.", color="info"),
                dbc.Table([
                    html.Thead(html.Tr([
                        html.Th("Frequency (Hz)"),
                        html.Th("Magnitude"),
                        html.Th("Phase (rad)"),
                        html.Th("Signal"),
                        html.Th("Actions")
                    ])),
                    html.Tbody(id="peak-table-body")
                ], bordered=True, hover=True, responsive=True, id="peak-data-table", className="mt-3")
            ])
            return table

        # Create table rows from peaks
        rows = []
        for i, peak in enumerate(peaks):
            rows.append(html.Tr([
                html.Td(f"{peak['frequency']:.4f}"),
                html.Td(f"{peak['magnitude']:.6e}"),
                html.Td(f"{peak['phase']:.4f}"),
                html.Td(peak['trace']),
                html.Td(
                    dbc.Button(
                        html.I(className="bi bi-trash"),
                        id={"type": "remove-peak-btn", "index": i},
                        color="danger",
                        size="sm",
                        outline=True
                    )
                )
            ]))

        # Create the table
        table_container = html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Copy to Clipboard",
                        id="copy-peaks-btn",
                        color="secondary",
                        size="sm",
                        outline=True,
                        className="me-2"
                    ),
                    dbc.Button(
                        "Download CSV",
                        id="download-peaks-btn",
                        color="primary",
                        size="sm",
                        outline=True,
                        className="me-2"
                    ),
                    dbc.Button(
                        "Clear All",
                        id="clear-peaks-btn",
                        color="danger",
                        size="sm",
                        outline=True
                    )
                ], width="auto")
            ], className="mb-2"),
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Frequency (Hz)"),
                    html.Th("Magnitude"),
                    html.Th("Phase (rad)"),
                    html.Th("Signal"),
                    html.Th("Actions")
                ])),
                html.Tbody(rows)
            ], bordered=True, hover=True, responsive=True, id="peak-data-table", className="mt-3"),
            dcc.Download(id="download-peaks-csv")
        ])

        return table_container

    # Handle peak removal
    @app.callback(
        Output("selected-peaks", "data", allow_duplicate=True),
        Input({"type": "remove-peak-btn", "index": ALL}, "n_clicks"),
        State("selected-peaks", "data"),
        prevent_initial_call=True
    )
    def remove_peak(n_clicks, peaks):
        """Remove a peak from the selected peaks"""
        if not any(n for n in n_clicks if n) or not peaks:
            raise PreventUpdate

        # Find which button was clicked
        triggered_id = ctx.triggered_id
        if triggered_id is None:
            raise PreventUpdate

        index = triggered_id.get('index')
        if index is None or index >= len(peaks):
            raise PreventUpdate

        # Remove the peak at the specified index
        new_peaks = peaks.copy()
        new_peaks.pop(index)

        return new_peaks

    # Clear all peaks
    @app.callback(
        Output("selected-peaks", "data", allow_duplicate=True),
        Input("clear-peaks-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def clear_peaks(n_clicks):
        """Clear all selected peaks"""
        if not n_clicks:
            raise PreventUpdate

        return []

    # Copy peaks to clipboard
    @app.callback(
        Output("copy-peaks-btn", "children"),
        Input("copy-peaks-btn", "n_clicks"),
        State("selected-peaks", "data"),
        prevent_initial_call=True
    )
    def copy_peaks_to_clipboard(n_clicks, peaks):
        """Copy peak data to clipboard in a tab-separated format"""
        if not n_clicks or not peaks:
            raise PreventUpdate

        # Create a JS function to copy to clipboard instead of using a textarea
        # This avoids the 'value' attribute error
        clipboard_js = """
        function copyToClipboard() {
            const text = `%s`;
            navigator.clipboard.writeText(text)
                .then(() => {
                    // Success
                })
                .catch(err => {
                    console.error('Error copying to clipboard:', err);
                });
        }
        copyToClipboard();
        """

        # Create CSV text
        csv_text = "Frequency (Hz)\tMagnitude\tPhase (rad)\tSignal\n"
        for peak in peaks:
            csv_text += f"{peak['frequency']:.6f}\t{peak['magnitude']:.6e}\t{peak['phase']:.6f}\t{peak['trace']}\n"

        # Use a JavaScript function to copy to clipboard instead of textarea
        copy_js = clipboard_js % csv_text

        # Return a combination of components
        copy_component = html.Div([
            "Copied!",
            # Add script tag that executes the copy function
            html.Script(children=copy_js),
            # Timer to reset button text
            dcc.Interval(
                id="copy-reset-interval",
                interval=2000,
                n_intervals=0)
        ])

        return copy_component

    # Download peaks as CSV
    @app.callback(
        Output("download-peaks-csv", "data"),
        Input("download-peaks-btn", "n_clicks"),
        State("selected-peaks", "data"),
        prevent_initial_call=True
    )
    def download_peaks_csv(n_clicks, peaks):
        """Download the selected peaks as a CSV file"""
        if not n_clicks or not peaks:
            raise PreventUpdate

        # Create DataFrame
        df = pd.DataFrame([
            {
                'Frequency (Hz)': peak['frequency'],
                'Magnitude': peak['magnitude'],
                'Phase (rad)': peak['phase'],
                'Signal': peak['trace']
            } for peak in peaks
        ])

        # Generate timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        return dict(
            content=df.to_csv(index=False),
            filename=f"peak_data_{timestamp}.csv"
        )

    # Reset copy button text after copying
    @app.callback(
        Output("copy-peaks-btn", "children", allow_duplicate=True),
        Input("copy-reset-interval", "n_intervals"),
        prevent_initial_call=True
    )
    def reset_copy_button_text(n_intervals):
        """Reset the copy button text after a delay"""
        return "Copy to Clipboard"

    # Export phase/magnitude plots as HTML
    @app.callback(
        Output("download-phase-html", "data"),
        Input("export-phase-btn", "n_clicks"),
        State("current-phase-figure", "data"),
        State("plot-metadata", "data"),
        State("signalx", "value"),
        State("signaly", "value"),
        prevent_initial_call=True
    )
    def export_phase_plots(n_clicks, figures, metadata, time_col, signals):
        """Export the current phase/magnitude plots as HTML"""
        if not n_clicks or not figures:
            raise PreventUpdate

        # Add plot-specific metadata
        plot_metadata = metadata.copy() if metadata else {}
        plot_metadata.update({
            'time_col': time_col,
            'signals': signals
        })

        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"phase_magnitude_analysis_{timestamp}.html"

        # With our new structure, figures[0] is the figure and figures[1] is
        # subplot info
        if isinstance(
                figures,
                list) and len(figures) >= 1 and isinstance(
                figures[0],
                dict):
            # Single plot (overlay mode with subplots)
            html_content = export_figures_from_plotly_objects(
                [figures[0]],
                plot_metadata,
                title="Phase/Magnitude Analysis",
                plot_type="Phase/Magnitude Analysis"
            )
        else:
            # Multiple plots (separate view, one per signal)
            # Extract just the figure objects from each figure+subplot_data
            # pair
            flattened_figures = []
            for fig_pair in figures:
                if isinstance(fig_pair, list) and len(fig_pair) >= 1:
                    # Just the figure, not the subplot data
                    flattened_figures.append(fig_pair[0])

            html_content = export_figures_from_plotly_objects(
                flattened_figures,
                plot_metadata,
                title="Phase/Magnitude Analysis",
                plot_type="Phase/Magnitude Analysis"
            )

        return dict(
            content=html_content,
            filename=filename
        )
