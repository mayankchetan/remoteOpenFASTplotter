"""
File ordering callbacks for OpenFAST Plotter
Contains callbacks for reordering the loaded files
"""

import os
import numpy as np
from dash import Input, Output, State, html, ctx, ALL, MATCH, no_update, dcc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# Import local modules
from data_manager import DATAFRAMES


def register_file_order_callbacks(app):
    """Register file ordering callbacks with the Dash app"""

    @app.callback(
        Output("file-order-list", "children"),
        Output("file-order", "data"),
        [Input("loaded-files", "data"),
         Input("file-order", "data"),
         Input("reset-file-order-btn", "n_clicks")],
        [State("file-order-list", "children")]
    )
    def update_file_order_list(
            loaded_files,
            current_order,
            reset_clicks,
            current_list):
        """
        Update the file order list when files are loaded or when order is reset.
        Also initializes the file order store when new files are loaded.
        """
        if not loaded_files or "files" not in loaded_files or not loaded_files["files"]:
            return html.Div(
                "No files loaded", className="text-center p-3 text-muted"), []

        trigger_id = ctx.triggered_id

        # List of file paths from loaded files
        file_paths = loaded_files["files"]

        # If we're resetting the order, or if file_order is empty, initialize
        # with default order
        if trigger_id == "reset-file-order-btn" or not current_order:
            # Default order is the same as loaded files
            file_order = file_paths.copy()
        else:
            # Keep existing order but add new files at the end
            # and remove files that are no longer loaded
            file_order = []
            # First add existing files that are still loaded, preserving their
            # order
            for file_path in current_order:
                if file_path in file_paths:
                    file_order.append(file_path)

            # Then add any new files that weren't in the current order
            for file_path in file_paths:
                if file_path not in file_order:
                    file_order.append(file_path)

        # Create the list items for each file
        list_items = []
        for i, file_path in enumerate(file_order):
            file_name = os.path.basename(file_path)

            # Create the list item with move up/down buttons
            list_items.append(
                dbc.ListGroupItem(
                    [
                        html.Div([
                            # Order number badge
                            dbc.Badge(
                                f"{i+1}", color="primary", className="me-2"),
                            # File name with tooltip
                            html.Span(
                                file_name, className="me-auto", title=file_path),
                            # Control buttons using text symbols instead of
                            # Bootstrap icons
                            html.Div([
                                # Move up button (disabled for first item)
                                dbc.Button(
                                    "▲",  # Up triangle symbol
                                    id={"type": "move-up-btn", "index": i},
                                    size="sm",
                                    color="secondary",
                                    outline=True,
                                    className="me-1",
                                    disabled=(i == 0),
                                    style={
                                        "fontSize": "14px", "padding": "2px 8px"}
                                ),
                                # Move down button (disabled for last item)
                                dbc.Button(
                                    "▼",  # Down triangle symbol
                                    id={"type": "move-down-btn", "index": i},
                                    size="sm",
                                    color="secondary",
                                    outline=True,
                                    disabled=(i == len(file_order) - 1),
                                    style={
                                        "fontSize": "14px", "padding": "2px 8px"}
                                ),
                            ], className="d-flex")
                        ], className="d-flex align-items-center justify-content-between")
                    ],
                    className="py-2"
                )
            )

        # Return the list items wrapped in a ListGroup and the file order
        return dbc.ListGroup(list_items), file_order

    # Callback for handling file reordering (move up)
    @app.callback(
        Output("file-order", "data", allow_duplicate=True),
        Input({"type": "move-up-btn", "index": ALL}, "n_clicks"),
        State("file-order", "data"),
        prevent_initial_call=True
    )
    def move_file_up(n_clicks, current_order):
        """Move a file up in the order when its up button is clicked"""
        if not any(n_clicks) or not current_order:
            raise PreventUpdate

        # Get the clicked button's ID
        button_id = ctx.triggered_id
        if button_id is None:
            raise PreventUpdate

        # Get the index of the file to move up
        index = button_id["index"]
        if index <= 0 or index >= len(current_order):
            raise PreventUpdate

        # Swap with the file above it
        new_order = current_order.copy()
        new_order[index], new_order[index -
                                    1] = new_order[index - 1], new_order[index]

        return new_order

    # Callback for handling file reordering (move down)
    @app.callback(
        Output("file-order", "data", allow_duplicate=True),
        Input({"type": "move-down-btn", "index": ALL}, "n_clicks"),
        State("file-order", "data"),
        prevent_initial_call=True
    )
    def move_file_down(n_clicks, current_order):
        """Move a file down in the order when its down button is clicked"""
        if not any(n_clicks) or not current_order:
            raise PreventUpdate

        # Get the clicked button's ID
        button_id = ctx.triggered_id
        if button_id is None:
            raise PreventUpdate

        # Get the index of the file to move down
        index = button_id["index"]
        if index < 0 or index >= len(current_order) - 1:
            raise PreventUpdate

        # Swap with the file below it
        new_order = current_order.copy()
        new_order[index], new_order[index +
                                    1] = new_order[index + 1], new_order[index]

        return new_order
