===============
Getting Started
===============

This page provides a quick introduction to using the Remote OpenFAST Plotter application.

Application Interface
-------------------

When you first open the Remote OpenFAST Plotter, you'll see the main interface divided into several tabs:

.. figure:: ../../assets/wind_turbine_plot.png
   :alt: Remote OpenFAST Plotter Interface
   :width: 800px
   :align: center
   
   Remote OpenFAST Plotter main interface

The interface is organized into the following tabs:

* **Files Tab**: Where you load and manage OpenFAST output files
* **Time Domain Tab**: For creating time series plots
* **FFT Tab**: For frequency analysis with Fast Fourier Transform
* **Phase Tab**: For phase relationship analysis between signals

Files Tab
--------

The Files tab is your starting point for working with OpenFAST data:

1. **Loading Files**:
   
   * Enter the paths to your OpenFAST output files (one per line)
   * Click "Load Files" to process the data
   * The application will show status indicators for each file

2. **Managing File Sets**:
   
   * Save frequently used file paths by entering a name and clicking "Save"
   * Load saved file sets using the dropdown menu and "Load" button

3. **File Order**:
   
   * Reorder files for consistent plotting using the file order panel
   * Use drag and drop or the reset button to manage file order

Time Domain Tab
-------------

Once files are loaded, you can create time series plots:

1. **Signal Selection**:
   
   * Choose signals for the Y-axes (multiple selections possible)
   * Select a signal for the X-axis (typically "Time")
   * Set the display option (Overlay or Separate)

2. **Plot Controls**:
   
   * Click "Update Plot" to generate visualizations
   * Use the interactive controls to zoom, pan, and hover for details
   * Select time ranges to focus on specific portions of the data

FFT Tab
------

For frequency domain analysis:

1. **FFT Parameters**:
   
   * Choose the averaging method (None, Welch, or Bartlett)
   * Select the window function (Hanning, Hamming, or None)
   * Set segment size and overlap percentage
   * Configure plot appearance options

2. **Frequency Annotations**:
   
   * Add markers for important frequencies
   * Save and load annotation sets
   * Use color-coding to categorize different frequency types

Phase Tab
--------

To analyze phase relationships:

1. **Signal Selection**:
   
   * Choose a reference signal
   * Select signals to compare against the reference
   * Click "Calculate Phase" to generate plots

2. **Interpretation**:
   
   * Examine magnitude and phase plots
   * Identify resonance points and phase changes
   * Compare across different signals or files

Quick Workflow Example
--------------------

Here's a typical workflow for analyzing wind turbine data:

1. **Load Files**:
   
   * Navigate to the Files tab
   * Enter paths to your OpenFAST output files
   * Click "Load Files"

2. **Create Time Domain Plot**:
   
   * Go to the Time Domain tab
   * Select blade root moment signals (e.g., "RootMycX1")
   * Choose "Time" as X-axis
   * Click "Update Plot"

3. **Perform FFT Analysis**:
   
   * Switch to the FFT tab
   * Configure FFT parameters (typically Welch averaging, Hanning window)
   * Click "Calculate FFT"
   * Add annotations for known frequencies (1P, 3P, etc.)

4. **Export Results**:
   
   * Click "Export Plot as HTML" on either tab
   * Save the HTML file to share with colleagues

Next Steps
---------

Once you're comfortable with the basics, explore these topics in the user guide:

* Managing file path sets for repeated analyses
* Advanced FFT analysis techniques
* Using phase analysis to detect resonances
* Customizing and exporting plots for reports