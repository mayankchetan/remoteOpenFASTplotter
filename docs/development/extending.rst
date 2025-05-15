=========
Extending
=========

This guide explains how to extend Remote OpenFAST Plotter with new features.

Overview
-------

The application is designed to be modular and extensible. This guide covers common extension scenarios:

1. Adding new analysis tools
2. Creating new UI components
3. Adding new callback functionality
4. Extending the FFT or phase analysis capabilities

Adding New Analysis Tools
-----------------------

To add a new analysis tool:

1. **Create a new module** in the ``tools/`` directory:

   .. code-block:: python
      :caption: tools/new_analysis.py

      """
      New analysis module for Remote OpenFAST Plotter.
      """
      
      import numpy as np
      
      def perform_analysis(signal, parameter1=0.5, parameter2=None):
          """
          Perform custom analysis on a signal.
          
          Args:
              signal (np.ndarray): Input signal data
              parameter1 (float): First analysis parameter
              parameter2 (any, optional): Second optional parameter
              
          Returns:
              dict: Analysis results
          """
          # Analysis implementation
          results = {
              'output1': np.mean(signal),
              'output2': np.std(signal)
          }
          return results

2. **Update the UI** to include controls for your tool in ``components.py``:

   .. code-block:: python
      
      # Add UI controls for your new analysis
      new_analysis_card = dbc.Card([
          dbc.CardHeader("New Analysis"),
          dbc.CardBody([
              dbc.Row([
                  dbc.Label("Parameter 1"),
                  dcc.Slider(0, 1, 0.1, value=0.5, id="param1-slider"),
              ]),
              dbc.Button("Run Analysis", id="run-analysis-btn")
          ])
      ])
      
      # Add the card to the appropriate tab layout

3. **Create new callbacks** in the callbacks directory:

   .. code-block:: python
      :caption: callbacks/new_analysis_callbacks.py
      
      """Callbacks for new analysis functionality."""
      
      from dash import Input, Output, State, callback
      import plotly.graph_objects as go
      from tools.new_analysis import perform_analysis
      from data_manager import DATAFRAMES
      
      def register_new_analysis_callbacks(app):
          """Register callbacks for new analysis."""
          
          @app.callback(
              Output("analysis-output", "figure"),
              Input("run-analysis-btn", "n_clicks"),
              State("file-dropdown", "value"),
              State("signal-dropdown", "value"),
              State("param1-slider", "value"),
              prevent_initial_call=True
          )
          def update_analysis(n_clicks, file_path, signal, param1):
              """Run the analysis when button is clicked."""
              if n_clicks is None:
                  return go.Figure()
                  
              df = DATAFRAMES.get(file_path)
              if df is None or signal not in df:
                  return go.Figure()
                  
              results = perform_analysis(df[signal].values, parameter1=param1)
              
              # Create figure with results
              fig = go.Figure()
              # Add visualization of results
              return fig

4. **Register the callbacks** in ``callbacks/__init__.py``:

   .. code-block:: python
      
      from .new_analysis_callbacks import register_new_analysis_callbacks
      
      def register_callbacks(app):
          # Existing registrations
          register_ui_callbacks(app)
          register_file_callbacks(app)
          # ... other registrations
          
          # Add your new callbacks
          register_new_analysis_callbacks(app)

Adding New UI Components
----------------------

To add new UI elements:

1. **Define the component** in ``components.py``
2. **Integrate** into the existing layout structure
3. **Add any necessary callbacks** in the appropriate callback module
4. **Update the CSS** if needed for styling

Extending FFT Analysis
-------------------

To extend the FFT analysis capabilities:

1. **Modify** ``tools/fft_analysis.py`` to add new methods or parameters
2. **Update** the FFT UI in the components module
3. **Enhance** the FFT callbacks in ``callbacks/fft_callbacks.py``

For example, to add a new windowing function:

.. code-block:: python
   
   # In tools/fft_analysis.py
   def apply_window(signal, window_type):
       """Apply a window to the signal."""
       if window_type == "hanning":
           return signal * np.hanning(len(signal))
       elif window_type == "hamming":
           return signal * np.hamming(len(signal))
       elif window_type == "blackman":  # New window type
           return signal * np.blackman(len(signal))
       else:
           return signal  # No window

   # Then update the UI to include the new option
   # In components.py
   window_dropdown = dcc.Dropdown(
       id="window-dropdown",
       options=[
           {"label": "None", "value": "none"},
           {"label": "Hanning", "value": "hanning"},
           {"label": "Hamming", "value": "hamming"},
           {"label": "Blackman", "value": "blackman"},  # New option
       ],
       value="hanning",
   )

Creating New Tabs
---------------

To add an entirely new tab to the application:

1. **Create the tab layout** in ``components.py``:

   .. code-block:: python
      
      # New tab layout
      new_tab_layout = dbc.Card(
          dbc.CardBody([
              # Your tab content here
          ]),
          className="mt-3",
      )

2. **Add the tab** to the main tabs component:

   .. code-block:: python
      
      def create_tabs():
          """Create the application tabs."""
          return dbc.Tabs(
              [
                  dbc.Tab(create_files_tab(), label="Files", tab_id="files-tab"),
                  dbc.Tab(create_time_domain_tab(), label="Time Domain", tab_id="time-tab"),
                  dbc.Tab(create_fft_tab(), label="FFT", tab_id="fft-tab"),
                  dbc.Tab(create_phase_tab(), label="Phase", tab_id="phase-tab"),
                  dbc.Tab(new_tab_layout, label="New Tab", tab_id="new-tab"),  # New tab
              ],
              id="tabs",
              active_tab="files-tab",
          )

3. **Create necessary callbacks** for the new tab functionality
4. **Register callbacks** in the callback registration system

Best Practices
------------

When extending Remote OpenFAST Plotter:

* Follow the existing code structure and naming conventions
* Keep the separation of concerns (UI, business logic, callbacks)
* Write tests for new functionality
* Update documentation to reflect new features
* Consider creating isolated modules for complex new features
* Maintain backward compatibility where possible