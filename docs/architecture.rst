==================================
Remote OpenFAST Plotter Architecture
==================================

This document describes the architecture of the Remote OpenFAST Plotter application, explaining how the code is organized and how the different modules interact with each other.

Overview
-------

The application is built using a modular structure to improve maintainability, testability, and extensibility. The code is divided into several Python modules, each with a specific responsibility:

.. figure:: ../assets/wind_turbine_plot.png
   :alt: Architecture Diagram
   :width: 500px
   :align: center

   Application architecture diagram

Module Structure
--------------

app.py
~~~~~~

This is the main entry point for the application. It:

* Initializes the Dash application with proper configuration
* Imports and registers the components and callbacks
* Provides the server startup functionality with automatic port retry

data_manager.py
~~~~~~~~~~~~~

Responsible for handling all data loading and management operations:

* Defines the global ``DATAFRAMES`` dictionary that stores loaded data
* Provides functions for loading OpenFAST files in parallel
* Implements file information retrieval

utils.py
~~~~~~~

Contains general utility functions used throughout the application:

* Plot generation and customization functions
* File path handling and unique identifiers generation
* UI helper functions for creating badges and other components

components.py
~~~~~~~~~~~

Defines all the UI components and layout structure:

* Creates the main application layout
* Defines individual UI cards for file input, signal selection, plot controls, etc.
* Provides functions to generate the tabbed interface

callbacks.py
~~~~~~~~~~

Contains all the callback functions that enable interactivity:

* File loading and management callbacks
* Signal selection and time range callbacks
* Plotting and FFT analysis callbacks
* Export and download callbacks
* Annotation management callbacks

tools/fft_analysis.py
~~~~~~~~~~~~~~~~~~

A specialized module for FFT computation and analysis:

* Provides the ``FFTResult`` class for storing results
* Implements various FFT calculation methods (direct FFT, Welch's method, binning)
* Handles signal preprocessing (windowing, detrending)

Data Flow
--------

1. **File Loading**:

   * User inputs file paths in the UI
   * The file loading callback reads the files using ``data_manager.py``
   * Loaded dataframes are stored in the global ``DATAFRAMES`` dictionary
   * File information and status are displayed in the UI

2. **Signal Selection**:

   * Available signals are extracted from loaded dataframes
   * User selects signals for X and Y axes

3. **Plotting**:

   * User configures plot options and time range
   * The plotting callback retrieves data from ``DATAFRAMES``
   * ``utils.py`` generates the plot using Plotly
   * The plot is displayed in the UI

4. **FFT Analysis**:

   * User configures FFT parameters
   * The FFT callback retrieves data and calls the FFT module
   * Results are plotted and displayed

5. **Export**:

   * User requests HTML export
   * The export callback generates a downloadable HTML file with the current plot

Adding New Features
-----------------

To add new features to the application:

1. **New UI Components**: Add them to ``components.py``
2. **New Functionality**: Implement core logic in ``utils.py`` or create a new module
3. **New Interactivity**: Add callbacks to ``callbacks.py`` and register them in ``register_callbacks()``
4. **Update Documentation**: Document new features in the README and other documentation files

Testing
------

The application includes tests for each module:

* ``test_utils.py``: Tests utility functions
* ``test_fft_analysis.py``: Tests FFT calculation functions
* ``test_app.py``: Tests basic application functionality
* ``test_app_with_files.py``: Tests using actual OpenFAST files

Deployment
---------

The application can be deployed in various environments:

* Local development: Run ``python app.py``
* Containerized: Use the provided Docker configuration
* Production: Configure for WSGI deployment with Gunicorn or similar