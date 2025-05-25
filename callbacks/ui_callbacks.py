"""
UI-related callbacks for OpenFAST Plotter
Contains callbacks for UI components like spinners, error details, etc.
"""

from dash import Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate


def register_ui_callbacks(app):
    """Register UI-related callbacks with the Dash app"""

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

    # Toggle saved paths collapse
    @app.callback(
        Output("saved-paths-collapse", "is_open"),
        Output("toggle-saved-paths-btn", "children"),
        Input("toggle-saved-paths-btn", "n_clicks"),
        State("saved-paths-collapse", "is_open"),
        prevent_initial_call=True
    )
    def toggle_saved_paths_section(n_clicks, is_open):
        """Toggle the visibility of the saved file paths section"""
        if n_clicks is None:
            raise PreventUpdate

        # Toggle visibility and change button text
        if is_open:
            return False, "Saved File Path Sets ▾"
        else:
            return True, "Saved File Path Sets ▴"
