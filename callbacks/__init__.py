"""
Callbacks Package for OpenFAST Plotter

This package organizes callbacks into logical modules:
- UI: User interface components and interactions
- Files: File loading and management
- Signals: Signal selection and filtering
- TimeDomain: Time domain plotting
- FFT: FFT analysis and plotting
- Annotations: FFT annotations management
- Export: Exporting plots as HTML
- PathManagement: Saved file paths management
- Preferences: User preferences management
- FileOrder: File ordering functionality
"""

from .ui_callbacks import register_ui_callbacks
from .file_callbacks import register_file_callbacks
from .signal_callbacks import register_signal_callbacks
from .time_domain_callbacks import register_time_domain_callbacks
from .fft_callbacks import register_fft_callbacks
from .annotation_callbacks import register_annotation_callbacks
from .export_callbacks import register_export_callbacks
from .path_management_callbacks import register_path_management_callbacks
from .preference_callbacks import register_preference_callbacks
from .file_order_callbacks import register_file_order_callbacks


def register_callbacks(app):
    """
    Register all callbacks with the Dash app
    
    Parameters:
    -----------
    app : dash.Dash
        The Dash application instance
    """
    # Register callbacks from each module
    register_ui_callbacks(app)
    register_file_callbacks(app)
    register_signal_callbacks(app)
    register_time_domain_callbacks(app)
    register_fft_callbacks(app)
    register_annotation_callbacks(app)
    register_export_callbacks(app)
    register_path_management_callbacks(app)
    register_preference_callbacks(app)
    register_file_order_callbacks(app)  # Register file order callbacks
