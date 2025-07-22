"""
Signal selection callbacks for OpenFAST Plotter
Contains callbacks for updating signal dropdowns and handling signal selection
"""

from dash import Input, Output, State, no_update, html
from dash.exceptions import PreventUpdate

# Import local modules
from data_manager import DATAFRAMES
from user_preferences import update_favorite_signals


def register_signal_callbacks(app):
    """Register signal selection callbacks with the Dash app"""

    # Update signal dropdowns based on loaded files
    @app.callback(
        Output("signalx", "options"),
        Output("signalx", "value"),
        Output("signaly", "options"),
        Output("signaly", "value"),
        Output("time-start", "min"),
        Output("time-start", "max"),
        Output("time-end", "min"),
        Output("time-end", "max"),
        Input("file-path-list", "data"),
        State("signalx", "value"),
        State("signaly", "value"),
        State("time-range-info", "data"),
        prevent_initial_call=True
    )
    def update_signal_dropdowns(
            file_paths,
            current_x,
            current_y,
            time_range_info):
        """
        Update signal dropdowns with available columns from loaded files.
        Preserves current selections if they are valid.
        """
        if not file_paths or not DATAFRAMES:
            raise PreventUpdate

        # Get first dataframe to extract columns
        first_path = file_paths[0]
        if first_path not in DATAFRAMES:
            raise PreventUpdate

        df = DATAFRAMES[first_path]
        if df is None or df.empty:
            raise PreventUpdate

        # Get column names
        df_columns = list(df.columns)
        sorted_columns = sorted(df_columns)

        # Determine default x axis if not set
        default_x = current_x
        if default_x is None or default_x not in sorted_columns:
            default_x = "Time_[s]"
            if default_x not in sorted_columns:
                default_x = "Time" if "Time" in sorted_columns else sorted_columns[0]

        # Determine default y signals if not set
        default_y = current_y
        if default_y is None or not default_y or not all(
                y in sorted_columns for y in default_y):
            # Default y axis could be a few common signals
            common_signals = [
                "GenPwr_[kW]",
                "BldPitch1_[deg]",
                "RotSpeed_[rpm]",
                "WindVxi_[m/s]"]
            default_y = []

            # Try to find common signals or alternatives
            for signal in common_signals:
                # Try to find the exact signal
                if signal in sorted_columns:
                    default_y.append(signal)
                else:
                    # Try to find a similar signal
                    base_name = signal.split('_')[0]
                    for col in sorted_columns:
                        if (col.startswith(base_name)):
                            default_y.append(col)
                            break

            # If no common signals found, use first few columns
            if not default_y:
                # Take first 2 columns if common signals not found
                default_y = sorted_columns[:2]

            # Don't include x-axis in y-axis
            if default_x in default_y:
                default_y.remove(default_x)

        # Set up time range limits
        min_time = 0
        max_time = 1000
        if 'min_time' in time_range_info and 'max_time' in time_range_info:
            min_time = time_range_info['min_time']
            max_time = time_range_info['max_time']
        else:
            # Default to first file's time range if no info available
            time_col = default_x
            try:
                min_time = df[time_col].min()
                max_time = df[time_col].max()
            except KeyError:
                # If time_col doesn't exist in the dataframe
                pass

        return (
            sorted_columns,
            default_x,
            sorted_columns,
            default_y,
            min_time,
            max_time,
            min_time,
            max_time
        )

    # Reset time range when reset button is pressed
    @app.callback(
        Output("time-start", "value"),
        Output("time-end", "value"),
        Input("reset-time-range-btn", "n_clicks"),
        State("time-range-info", "data"),
        prevent_initial_call=True
    )
    def reset_time_range(reset_clicks, time_range_info):
        """
        Reset time range control values when the reset button is clicked.
        """
        # Only triggered by reset button
        if not reset_clicks:
            raise PreventUpdate

        # Set values from time_range_info if available
        if 'min_time' in time_range_info and 'max_time' in time_range_info:
            return time_range_info['min_time'], time_range_info['max_time']
        else:
            # If no time range info available, return default None
            return None, None

    # Add favorite signals callbacks
    @app.callback(
        Output("signaly", "value", allow_duplicate=True),
        Input("favorite-signals-btn", "n_clicks"),
        State("signaly", "options"),
        prevent_initial_call=True
    )
    def load_favorite_signals(n_clicks, available_signals):
        """Load favorite signals from user preferences"""
        if not n_clicks:
            raise PreventUpdate

        from user_preferences import load_preferences
        prefs = load_preferences()
        favorites = prefs.get("favorite_signals", [])

        # If there are no favorites or no available signals, prevent update
        if not favorites or not available_signals:
            return no_update

        # Handle different formats of dropdown options
        # Check the type of the first option to determine format
        if isinstance(
                available_signals[0],
                dict) and 'value' in available_signals[0]:
            # Format is list of dicts with 'value' key
            available_signal_values = [opt['value']
                                       for opt in available_signals]
        elif isinstance(available_signals[0], str):
            # Format is just a list of strings (the values themselves)
            available_signal_values = available_signals
        else:
            # Unknown format, prevent update
            return no_update

        # Filter favorites to only include available signals
        valid_favorites = [
            sig for sig in favorites if sig in available_signal_values]

        if not valid_favorites:
            return no_update

        return valid_favorites

    # Add callback to save favorite signals
    @app.callback(
        Output("favorite-signals-status", "children"),
        Input("save-favorites-btn", "n_clicks"),
        State("signaly", "value"),
        prevent_initial_call=True
    )
    def save_favorite_signals_callback(n_clicks, selected_signals):
        """Save currently selected signals as favorites"""
        if not n_clicks or not selected_signals:
            raise PreventUpdate

        update_favorite_signals(selected_signals)

        return html.Span("Saved!", className="text-success fade-out")
