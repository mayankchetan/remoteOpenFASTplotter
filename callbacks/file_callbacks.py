"""
File-related callbacks for OpenFAST Plotter
Contains callbacks for file loading and management
"""

import os
import datetime
import traceback
import pandas as pd

from dash import Input, Output, State, html, ctx, ALL, no_update
from dash.exceptions import PreventUpdate

# Import local modules
from data_manager import DATAFRAMES, store_dataframes, get_file_info, remove_file
from utils import create_file_pills
from user_preferences import update_recent_files


def register_file_callbacks(app):
    """Register file-related callbacks with the Dash app"""
    
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
        Input("reload-files-btn", "n_clicks"),
        Input("clear-files-btn", "n_clicks"),
        State("loaded-files", "data"),
        State("file-path-list", "data"),
        State("file-paths-input", "value"),
        prevent_initial_call=True
    )
    def load_files_from_input(load_clicks, reload_clicks, clear_clicks, current_loaded_files, current_file_paths, file_paths_input):
        """
        Load files from input text area, avoiding reload of already loaded files.
        
        This callback handles:
        1. Loading new files when the "Load Files" button is clicked
        2. Reloading existing files when the "Reload Files" button is clicked
        3. Clearing all loaded files when the "Clear All" button is clicked
        4. Displaying status messages and error details
        5. Creating file pills for visual representation of loaded files
        """
        
        trigger_id = ctx.triggered_id
        
        if trigger_id == "clear-files-btn":
            DATAFRAMES.clear()  # Clear the global dictionary
            return {}, [], html.Div("All files cleared"), "", html.Div(), "0", {"display": "none"}, {"display": "none"}, [], False, {}
        
        # Handle reload files button click
        if trigger_id == "reload-files-btn":
            if not current_file_paths:
                return current_loaded_files, current_file_paths, html.Div("No files to reload", style={"color": "red"}), "", create_file_pills(current_file_paths), str(len(current_file_paths)), {"display": "none"}, {"display": "none"}, [], False, {}
            
            # Clear existing dataframes but keep the paths
            for file_path in current_file_paths:
                if file_path in DATAFRAMES:
                    DATAFRAMES.pop(file_path)
            
            # Load all files again
            valid_paths = []
            invalid_paths = []
            for path in current_file_paths:
                if os.path.exists(path) and os.path.isfile(path):
                    valid_paths.append(path)
                else:
                    invalid_paths.append(path)
            
            # Load valid files in parallel
            if valid_paths:
                new_dfs, failed_files, load_times = store_dataframes(valid_paths)
                
                # Log loading times
                for file_path, elapsed in load_times.items():
                    print(f"Reloaded {os.path.basename(file_path)} in {elapsed:.2} seconds")
                
                # Update the global DATAFRAMES dictionary with new DataFrames
                for path, df in new_dfs.items():
                    DATAFRAMES[path] = df
                
                # Get list of files that failed to load
                failed_paths = [f[0] for f in failed_files]
                
                # Create status message
                status_elements = []
                
                if new_dfs:
                    status_elements.append(
                        html.Span(f"✓ Reloaded {len(new_dfs)} files", style={"color": "green"})
                    )
                
                if failed_paths:
                    status_elements.append(
                        html.Span(f" | ⚠️ {len(failed_paths)} files failed to reload", style={"color": "red", "marginLeft": "10px"})
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
                
                # Create file pills for all valid loaded files
                reloaded_files = list(new_dfs.keys())
                pills = create_file_pills(reloaded_files)
                
                # Set visibility based on whether we have errors
                error_container_style = {"display": "block"} if has_errors else {"display": "none"}
                error_button_style = {"display": "block"} if has_errors else {"display": "none"}
                
                # Determine time range from loaded files
                time_range_info = {}
                if reloaded_files:
                    for file_path in reloaded_files:
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
                    {"files": reloaded_files},
                    reloaded_files,
                    html.Div(status_elements),
                    "",
                    pills,
                    str(len(reloaded_files)),
                    error_container_style,
                    error_button_style,
                    error_details,
                    False,  # Loading done
                    time_range_info
                )
            else:
                # No valid files to reload
                return (
                    {"files": []},
                    [],
                    html.Div("No valid files found to reload", style={"color": "red"}),
                    "",
                    html.Div(),
                    "0",
                    {"display": "none"},
                    {"display": "none"},
                    [],
                    False,
                    {}
                )
        
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
                print(f"Loaded {os.path.basename(file_path)} in {elapsed:.2} seconds")
            
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
        
        # Clear the plot if no files are left
        plot_output = html.Div("Select signals to plot", className="text-center p-5 text-muted") if not updated_files else no_update
        
        return ({"files": updated_files}, updated_file_paths, file_pills, file_count, signal_options, signal_options, plot_output)
