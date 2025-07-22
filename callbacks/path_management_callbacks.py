"""
File path management callbacks for OpenFAST Plotter
Contains callbacks for saving, loading, and deleting file path sets
"""

from dash import Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate
import traceback

# Import local modules
from user_preferences import (
    save_file_path_set,
    get_saved_file_paths,
    delete_saved_file_path_set,
    rename_saved_file_path_set)


def register_path_management_callbacks(app):
    """Register path management callbacks with the Dash app"""

    # Load a saved file path set
    @app.callback(
        Output("file-paths-input", "value", allow_duplicate=True),
        Input("load-saved-paths-btn", "n_clicks"),
        State("saved-paths-dropdown", "value"),
        prevent_initial_call=True
    )
    def load_saved_paths(n_clicks, selected_path_set):
        """Load a saved file path set into the textarea"""
        if n_clicks is None or selected_path_set is None:
            raise PreventUpdate

        saved_paths = get_saved_file_paths()
        if selected_path_set in saved_paths:
            paths = saved_paths[selected_path_set]
            return "\n".join(paths)

        return no_update

    # Save current file paths as a named set
    @app.callback(
        [Output("saved-paths-dropdown", "options"),
         Output("save-paths-name-input", "value"),
         Output("status-message", "children")],
        Input("save-paths-btn", "n_clicks"),
        [State("file-paths-input", "value"),
         State("save-paths-name-input", "value")],
        prevent_initial_call=True
    )
    def save_current_paths(n_clicks, file_paths_text, path_set_name):
        """Save the current file paths as a named set"""
        try:
            print(
                f"DEBUG: save_current_paths callback triggered! n_clicks={n_clicks}")
            print(f"DEBUG: path_set_name='{path_set_name}'")
            print(
                f"DEBUG: file_paths_text length={len(file_paths_text) if file_paths_text else 0}")

            if n_clicks is None:
                print("DEBUG: n_clicks is None, preventing update") # F541 fix
                raise PreventUpdate

            if not file_paths_text:
                print("DEBUG: file_paths_text is empty") # F541 fix
                return no_update, no_update, html.Div(
                    "No file paths to save", style={"color": "red"})

            if not path_set_name:
                print("DEBUG: path_set_name is empty") # F541 fix
                return no_update, no_update, html.Div(
                    "Please enter a name for the path set", style={
                        "color": "red"})

            # Split the text into a list of file paths
            file_paths = [path.strip()
                          for path in file_paths_text.split("\n") if path.strip()]
            print(f"DEBUG: parsed {len(file_paths)} file paths")

            if not file_paths:
                print("DEBUG: No valid file paths found") # F541 fix
                return no_update, no_update, html.Div(
                    "No valid file paths found", style={"color": "red"})

            # Save the file paths
            print(
                f"DEBUG: Calling save_file_path_set with name='{path_set_name}' and {len(file_paths)} paths")
            success = save_file_path_set(path_set_name, file_paths)
            print(f"DEBUG: save_file_path_set returned {success}")

            # Update the dropdown options
            saved_paths = get_saved_file_paths()
            print(
                f"DEBUG: After save, get_saved_file_paths returned {len(saved_paths)} entries: {list(saved_paths.keys())}")
            options = [{"label": name, "value": name}
                       for name in saved_paths.keys()]

            if success:
                status = html.Div(
                    f"Saved file paths as '{path_set_name}'", style={
                        "color": "green"})
                print(f"DEBUG: Returning success message: {status}")
                return options, "", status
            else:
                status = html.Div(
                    f"Failed to save path set '{path_set_name}'", style={
                        "color": "red"})
                print(f"DEBUG: Returning error message: {status}")
                return no_update, no_update, status

        except Exception as e:
            import traceback
            print(f"ERROR in save_current_paths: {e}")
            print(traceback.format_exc())
            return no_update, no_update, html.Div(
                f"Error: {str(e)}", style={"color": "red"})

    # Toggle delete confirmation modal
    @app.callback(
        Output("delete-path-modal", "is_open"),
        [Input("delete-saved-paths-btn", "n_clicks"),
         Input("delete-path-cancel", "n_clicks"),
         Input("delete-path-confirm", "n_clicks")],
        State("delete-path-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_delete_modal(
            open_clicks,
            cancel_clicks,
            confirm_clicks,
            is_open):
        """Toggle the delete confirmation modal"""
        if open_clicks or cancel_clicks or confirm_clicks:
            return not is_open
        return is_open

    # Delete a saved path set
    @app.callback(
        [Output("saved-paths-dropdown", "options", allow_duplicate=True),
         Output("saved-paths-dropdown", "value"),
         Output("status-message", "children", allow_duplicate=True)],
        Input("delete-path-confirm", "n_clicks"),
        State("saved-paths-dropdown", "value"),
        prevent_initial_call=True
    )
    def delete_path_set(n_clicks, selected_path_set):
        """Delete a saved file path set"""
        if n_clicks is None or selected_path_set is None:
            raise PreventUpdate

        success = delete_saved_file_path_set(selected_path_set)

        if success:
            # Update the dropdown options
            saved_paths = get_saved_file_paths()
            options = [{"label": name, "value": name}
                       for name in saved_paths.keys()]
            return options, None, f"Deleted path set '{selected_path_set}'"

        return no_update, no_update, "Failed to delete path set"

    # Toggle rename modal
    @app.callback(
        Output("rename-path-modal", "is_open"),
        [Input("rename-saved-paths-btn", "n_clicks"),
         Input("rename-path-cancel", "n_clicks"),
         Input("rename-path-confirm", "n_clicks")],
        State("rename-path-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_rename_modal(
            open_clicks,
            cancel_clicks,
            confirm_clicks,
            is_open):
        """Toggle the rename modal"""
        if open_clicks or cancel_clicks or confirm_clicks:
            return not is_open
        return is_open

    # Rename a saved path set
    @app.callback(
        [Output("saved-paths-dropdown", "options", allow_duplicate=True),
         Output("saved-paths-dropdown", "value", allow_duplicate=True),
         Output("status-message", "children", allow_duplicate=True)],
        Input("rename-path-confirm", "n_clicks"),
        [State("saved-paths-dropdown", "value"),
         State("rename-path-set-input", "value")],
        prevent_initial_call=True
    )
    def rename_path_set(n_clicks, old_name, new_name):
        """Rename a saved file path set"""
        if n_clicks is None or old_name is None or not new_name:
            raise PreventUpdate

        success = rename_saved_file_path_set(old_name, new_name)

        if success:
            # Update the dropdown options
            saved_paths = get_saved_file_paths()
            options = [{"label": name, "value": name}
                       for name in saved_paths.keys()]
            return options, new_name, f"Renamed path set '{old_name}' to '{new_name}'"

        return no_update, no_update, "Failed to rename path set"
