"""
Debug utility for the OpenFAST Plotter application.
This script helps troubleshoot UI issues by creating a simple UI that
demonstrates the file path saving functionality.
"""

import os
import dash
from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from user_preferences import (save_file_path_set, get_saved_file_paths, 
                            load_preferences, save_preferences)

# Initialize the Dash app with Bootstrap styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create a simple UI for testing path saving
app.layout = dbc.Container([
    html.H1("OpenFAST Plotter Debug Tool", className="mt-4 mb-4"),
    
    html.Div([
        html.H4("Test File Path Saving"),
        dbc.Textarea(
            id="file-paths-input",
            placeholder="Enter file paths (one per line)",
            value="/path/to/file1.out\n/path/to/file2.out",
            style={"height": "150px"},
            className="mb-2"
        ),
        dbc.Row([
            dbc.Col([
                dbc.Input(
                    id="save-paths-name-input",
                    placeholder="Enter name for path set",
                    value="test_set",
                    className="mb-2"
                ),
            ], width=8),
            dbc.Col([
                dbc.Button("Save Paths", id="save-paths-btn", color="primary"),
            ], width=4),
        ]),
        html.Div(id="status-message", className="mt-2"),
    ], className="border p-3 mb-4"),
    
    html.Div([
        html.H4("Current Saved Path Sets"),
        html.Pre(id="current-paths-display"),
        dbc.Button("Refresh", id="refresh-btn", color="secondary"),
    ], className="border p-3"),
], fluid=True)

# Callback to save paths
@app.callback(
    Output("status-message", "children"),
    Output("current-paths-display", "children"),
    Input("save-paths-btn", "n_clicks"),
    State("file-paths-input", "value"),
    State("save-paths-name-input", "value"),
    prevent_initial_call=True
)
def save_paths(n_clicks, file_paths_text, path_set_name):
    """Save paths and display result"""
    if n_clicks is None or not file_paths_text or not path_set_name:
        return "Please enter file paths and a name", display_current_paths()
    
    # Split the text into a list of file paths
    file_paths = [path.strip() for path in file_paths_text.split("\n") if path.strip()]
    
    if not file_paths:
        return "No file paths to save", display_current_paths()
    
    # Save the file paths
    try:
        print(f"Saving {len(file_paths)} paths as '{path_set_name}'")
        success = save_file_path_set(path_set_name, file_paths)
        
        if success:
            message = html.Div(f"Successfully saved {len(file_paths)} paths as '{path_set_name}'", 
                             style={"color": "green"})
        else:
            message = html.Div(f"Failed to save path set '{path_set_name}'", 
                             style={"color": "red"})
    except Exception as e:
        import traceback
        print(f"Error saving paths: {e}")
        print(traceback.format_exc())
        message = html.Div(f"Error: {str(e)}", style={"color": "red"})
    
    return message, display_current_paths()

# Callback to refresh the display
@app.callback(
    Output("current-paths-display", "children", allow_duplicate=True),  # Added allow_duplicate=True
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def refresh_display(_):
    """Refresh the paths display"""
    return display_current_paths()

def display_current_paths():
    """Get and format current saved paths"""
    try:
        saved_paths = get_saved_file_paths()
        
        if not saved_paths:
            return "No saved path sets found"
        
        output = []
        for name, paths in saved_paths.items():
            output.append(f"Set: {name} ({len(paths)} paths)")
            for path in paths[:3]:  # Show first 3 paths
                output.append(f"  - {path}")
            if len(paths) > 3:
                output.append(f"  - ... and {len(paths) - 3} more")
            output.append("")
        
        return "\n".join(output)
    except Exception as e:
        import traceback
        print(f"Error displaying paths: {e}")
        print(traceback.format_exc())
        return f"Error retrieving saved paths: {str(e)}"

if __name__ == "__main__":
    print("=== OpenFAST Plotter Debug Tool ===")
    print(f"Preferences file: {os.path.expanduser('~/.openfast_plotter/preferences.json')}")
    print("Starting debug server...")
    app.run(debug=True, port=8059)
