===================
Time Series Analysis
===================

This example demonstrates how to effectively analyze time series data from OpenFAST simulations.

Time Domain Analysis Overview
---------------------------

Time series analysis in Remote OpenFAST Plotter allows you to:

* Visualize signal behavior over time
* Compare multiple signals simultaneously
* Identify important events in the simulation
* Isolate specific time ranges for detailed examination

Loading and Plotting Time Series Data
----------------------------------

To analyze time series data:

1. **Load Your OpenFAST Files**:
   
   * Navigate to the Files tab
   * Enter the paths to your OpenFAST output files
   * Click "Load Files"

2. **Navigate to Time Domain Tab**:
   
   * Select the "Time Domain" tab in the main navigation

3. **Configure Plot Parameters**:
   
   * Select X-axis signal (usually "Time")
   * Select one or more Y-axis signals
   * Choose plot style (Overlay or Separate)
   * Adjust time range if needed

4. **Generate Plot**:
   
   * Click "Update Plot" to create the visualization

Example: Comparing Blade Root Moments
----------------------------------

Here's a specific example for analyzing blade root moments across different wind conditions:

1. **Load Multiple Files**:
   
   .. code-block:: text
      
      test_files/5MW_Land_DLL_WTurb.outb
      test_files/5MW_Land_BD_DLL_WTurb.outb

2. **Select Comparable Signals**:
   
   * For Y-axis: Select "RootMyc1" from both files
   * For X-axis: Select "Time"
   * Display option: "Separate"

3. **Analyze the Results**:
   
   * Compare the blade root moment magnitudes between simulations
   * Look for patterns, peaks, and transient events
   * Identify any phase differences or timing shifts

Advanced Time Series Techniques
----------------------------

The application provides several advanced time series analysis features:

1. **Time Range Selection**:
   
   * Enter specific start and end times to focus on a particular period
   * Useful for isolating startup transients, fault events, or specific maneuvers

2. **Overlaid Vs. Separate Plots**:
   
   * Overlay: Good for direct comparison of signal magnitudes
   * Separate: Better for seeing patterns when magnitude ranges differ significantly

3. **File Order Management**:
   
   * Ensure consistent color assignment across plots by managing file order
   * Particularly useful when comparing results across multiple analysis sessions

4. **Multiple Signal Selection**:
   
   * Compare different signal types (e.g., blade moments vs. tower moments)
   * Assess correlation between different measurements

5. **Plot Customization**:
   
   * Adjust axis scaling (linear vs. log)
   * Enable/disable grid lines
   * Configure legend position

Example: Analyzing Startup Transients
----------------------------------

For analyzing wind turbine startup behavior:

1. **Load a startup simulation file**

2. **Select relevant signals**:
   
   * Generator speed
   * Blade pitch angles
   * Tower base moments
   * Rotor thrust

3. **Focus on startup period**:
   
   * Enter time range (e.g., 0-60 seconds)
   * Click "Update Plot"

4. **Observe and analyze**:
   
   * Generator speed ramp-up
   * Pitch control activation
   * Structural loading during transition

5. **Export findings**:
   
   * Use the "Export as HTML" option to save the visualization

Troubleshooting Time Series Analysis
---------------------------------

Common issues with time series analysis:

* **Mismatched Time Scales**: If comparing files with different simulation lengths or time steps, adjust the time range accordingly
* **Signal Selection**: Ensure signal names match across files (may vary with model changes)
* **Large Files**: For very large files, consider using a time range to focus on relevant periods and improve performance
* **Missing Data**: If a signal appears to be missing, check if it's actually present in the file or if it has a different name