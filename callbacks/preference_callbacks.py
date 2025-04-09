"""
User preferences callbacks for OpenFAST Plotter
Contains callbacks for loading and saving user preferences
"""

from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate

# Import local modules
from user_preferences import (load_preferences, save_plot_settings, 
                             save_fft_settings)
from utils import create_annotation_badges


def register_preference_callbacks(app):
    """Register preference-related callbacks with the Dash app"""
    
    # Initialize and load user preferences when app starts
    @app.callback(
        Output("fft-annotations", "data", allow_duplicate=True),
        Output("fft-annotations-display", "children", allow_duplicate=True),
        Output("fft-averaging", "value", allow_duplicate=True),
        Output("fft-windowing", "value", allow_duplicate=True),
        Output("fft-n-exp", "value", allow_duplicate=True),
        Output("fft-plot-style", "value", allow_duplicate=True),
        Output("fft-detrend", "value", allow_duplicate=True),
        Output("fft-xscale", "value", allow_duplicate=True),
        Output("fft-x-limit", "value", allow_duplicate=True),
        Output("plot-option", "value", allow_duplicate=True),
        Input("plot-metadata", "data"),  # Use the metadata store as a trigger on app start
        prevent_initial_call=True
    )
    def initialize_from_preferences(metadata):
        """Initialize app settings from saved user preferences"""
        prefs = load_preferences()
        
        # Initialize FFT annotations
        annotations = prefs.get("custom_annotations", [])
        badges = create_annotation_badges(annotations)
        
        # Initialize FFT settings
        fft_settings = prefs.get("fft_settings", {})
        averaging = fft_settings.get("averaging", "Welch")
        windowing = fft_settings.get("windowing", "hamming")
        n_exp = fft_settings.get("n_exp", 15)
        plot_style = fft_settings.get("plot_style", "overlay")
        detrend = ["detrend"] if fft_settings.get("detrend", True) else []
        xscale = fft_settings.get("xscale", "linear")
        x_limit = fft_settings.get("x_limit", 5)
        
        # Initialize plot settings
        plot_settings = prefs.get("plot_settings", {})
        plot_option = plot_settings.get("plot_option", "overlay")
        
        return (annotations, badges, averaging, windowing, n_exp, plot_style, 
                detrend, xscale, x_limit, plot_option)
    
    # Add callbacks to save plot settings when they change
    @app.callback(
        Output("plot-metadata", "data", allow_duplicate=True),  # Just a dummy output
        Input("plot-option", "value"),
        State("plot-metadata", "data"),
        prevent_initial_call=True
    )
    def save_plot_settings_callback(plot_option, metadata):
        """Save plot settings to user preferences when they change"""
        settings = {"plot_option": plot_option}
        save_plot_settings(settings)
        return no_update
    
    # Add callback to save FFT settings when they change
    @app.callback(
        Output("plot-metadata", "data", allow_duplicate=True),  # Just a dummy output
        Input("fft-averaging", "value"),
        Input("fft-windowing", "value"),
        Input("fft-n-exp", "value"),
        Input("fft-plot-style", "value"),
        Input("fft-detrend", "value"),
        Input("fft-xscale", "value"),
        Input("fft-x-limit", "value"),
        State("plot-metadata", "data"),
        prevent_initial_call=True
    )
    def save_fft_settings_callback(averaging, windowing, n_exp, plot_style, detrend, xscale, x_limit, metadata):
        """Save FFT settings to user preferences when they change"""
        settings = {
            "averaging": averaging,
            "windowing": windowing,
            "n_exp": n_exp,
            "plot_style": plot_style,
            "detrend": "detrend" in detrend,
            "xscale": xscale,
            "x_limit": x_limit
        }
        save_fft_settings(settings)
        return no_update
