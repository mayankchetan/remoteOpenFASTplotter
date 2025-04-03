"""
Utility functions for OpenFAST Plotter
Contains plotting functions and other utilities
"""

import os
import numpy as np
import plotly.graph_objects as go
import plotly.colors
from dash import html
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc

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
                    f"{anno['label']}: {anno['freq']:.2f} Hz",  # Format frequency with 2 decimal places
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
