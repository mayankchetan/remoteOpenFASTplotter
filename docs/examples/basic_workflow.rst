=============
Basic Workflow
=============

This example demonstrates a complete workflow using Remote OpenFAST Plotter to analyze wind turbine simulation data.

Step 1: Loading OpenFAST Files
-----------------------------

Start by loading one or more OpenFAST output files:

1. Navigate to the **Files tab**
2. Enter file paths in the text area (one per line):

   .. code-block:: text

      /path/to/simulation1.outb
      /path/to/simulation2.outb

3. Click the "Load Files" button
4. Wait for the green status indicators showing files are loaded successfully

.. tip::
   You can download test files using the included utility:
   ``python utils/download_test_files.py``

Step 2: Creating Time Domain Plots
--------------------------------

After loading files, visualize time series data:

1. Navigate to the **Time Domain tab**
2. Select signals for visualization:
   
   * Select Y-axis signals (e.g., "RootMycX1", "TwrBsMxt")
   * Select X-axis signal (typically "Time")
   * Choose display option (Overlay Files or Separate Files)

3. Click "Update Plot" to generate visualizations
4. Interact with the plot:
   
   * Zoom: Click and drag to select a region
   * Pan: Click and drag in the plot area
   * Reset view: Double-click in the plot area
   * Hover: See exact values for any point

Step 3: Performing FFT Analysis
-----------------------------

For frequency domain analysis:

1. Navigate to the **FFT tab**
2. Configure FFT parameters:
   
   * Averaging Method: Choose between None, Welch, or Bartlett
   * Window Function: Select Hanning, Hamming, or None
   * Segment Size: Adjust based on desired frequency resolution
   * Overlap: Set percentage for overlapping segments

3. Click "Calculate FFT" to generate frequency plots
4. Add annotations for important frequencies:
   
   * Enter frequency value and description
   * Click "Add" to mark it on the plot
   * Save annotations for future reference

Step 4: Exporting Results
-----------------------

To share your analysis with others:

1. From any tab with plots, click "Export Plot as HTML"
2. Save the HTML file to your computer
3. The exported file includes:
   
   * The interactive plot with all data points
   * Metadata about the analysis
   * Any annotations or markers you've added

The HTML files can be opened in any web browser without requiring additional software.

Complete Example: Analyzing Tower Response
----------------------------------------

Here's a complete workflow analyzing tower response:

1. Load OpenFAST files containing tower data:
   
   .. code-block:: text
      
      test_files/5MW_Land_DLL_WTurb.outb

2. In Time Domain tab:
   
   * Select "TwrBsMxt" and "TwrBsMyt" as Y-axis signals
   * Keep default "Time" as X-axis
   * Set "Overlay Files" display option
   * Click "Update Plot"
   * Observe the tower base moment time series

3. In FFT tab:
   
   * Keep default Welch averaging and Hanning window
   * Set segment size exponent to 11 for adequate resolution
   * Click "Calculate FFT"
   * Add annotations at key frequencies:
     * 0.2 Hz: "1P" (assuming a 12 RPM rotor speed)
     * 0.6 Hz: "3P"
     * 0.33 Hz: "Tower FA" (assumed first fore-aft mode)

4. Export the FFT plot as HTML for documentation
   
   * Click "Export FFT as HTML"
   * Save to your preferred location

This example demonstrates the core functionality of Remote OpenFAST Plotter for a basic wind turbine analysis workflow.