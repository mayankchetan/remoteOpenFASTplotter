# OpenFAST Plotter - Callback Organization

## Overview

This directory contains the callback modules for the OpenFAST Plotter application.
The callbacks have been organized into logical modules based on their functionality
to improve code maintainability and readability.

## Callback Modules

The following callback modules are available:

- **UI Callbacks** (`ui_callbacks.py`): Manages user interface components like spinners, error details, etc.
- **File Callbacks** (`file_callbacks.py`): Handles file loading and management operations.
- **Signal Callbacks** (`signal_callbacks.py`): Manages signal selection dropdowns and time range controls.
- **Time Domain Callbacks** (`time_domain_callbacks.py`): Creates time domain plots based on selected signals.
- **FFT Callbacks** (`fft_callbacks.py`): Performs FFT analysis and creates frequency domain plots.
- **Annotation Callbacks** (`annotation_callbacks.py`): Manages frequency annotations for FFT plots.
- **Export Callbacks** (`export_callbacks.py`): Handles exporting plots as HTML files.
- **Path Management Callbacks** (`path_management_callbacks.py`): Manages saved file path sets.
- **Preference Callbacks** (`preference_callbacks.py`): Loads and saves user preferences.

## Adding New Callbacks

To add a new callback:

1. Identify which module it belongs to (or create a new one if needed).
2. Add the callback to the appropriate module.
3. If creating a new module, follow this pattern:

```python
# filepath: callbacks/new_module_callbacks.py

def register_new_module_callbacks(app):
    """Register new module callbacks with the Dash app"""
    
    @app.callback(...)
    def my_new_callback(...):
        # Implementation
        pass
```

4. Update the `__init__.py` to import and register the new module.

## Dependencies

Most callback modules depend on:
- `data_manager.py`: For accessing loaded dataframes
- `utils.py`: For utility functions like creating plots
- `user_preferences.py`: For loading/saving user preferences

## Testing

Unit tests for callbacks are in the `tests/` directory. Run them with:
```bash
python -m unittest discover -s tests
```
