"""
FFT analysis callbacks for OpenFAST Plotter
Contains callbacks for FFT calculation and plotting
"""

import os
import sys
import traceback
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.colors

from dash import Input, Output, State, html, dcc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# Import local modules
from data_manager import DATAFRAMES
from utils import get_unique_identifiers

# Import FFT analysis module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools'))
from tools.fft_analysis import compute_fft


def register_fft_callbacks(app):
    """Register FFT analysis callbacks with the Dash app"""
    
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
        State("fft-plot-style", "value"),
        State("fft-detrend", "value"),
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
                            name=f"{signal} - {file_name}",
                            hovertemplate=f"<b>{file_name}</b><br>" +
                                         f"<b>Signal:</b> {signal}<br>" +
                                         f"<b>Frequency:</b> %{{x:.4g}} Hz<br>" +
                                         f"<b>Amplitude:</b> %{{y:.4g}}<extra></extra>"
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
                        textangle=-90,  # Horizontal text
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
                            name=file_name,
                            hovertemplate=f"<b>{file_name}</b><br>" +
                                         f"<b>Signal:</b> {signal}<br>" +
                                         f"<b>Frequency:</b> %{{x:.4g}} Hz<br>" +
                                         f"<b>Amplitude:</b> %{{y:.4g}}<extra></extra>"
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
