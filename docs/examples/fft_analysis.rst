=============
FFT Analysis
=============

This example provides a detailed guide to using the FFT analysis capabilities of Remote OpenFAST Plotter.

FFT Analysis Basics
-----------------

Fast Fourier Transform (FFT) analysis converts time domain signals into the frequency domain, allowing you to:

* Identify dominant frequencies in your data
* Detect resonances in the structure
* Observe harmonic relationships
* Compare frequency content across different simulations

Configuring FFT Parameters
------------------------

The FFT tab provides several configuration options that affect your analysis:

1. **Averaging Method**:
   
   * **None**: Simple FFT without averaging (higher variance)
   * **Welch**: Welch's method - divides the signal into overlapping segments, computes FFT for each, then averages (reduced variance, better statistical stability)
   * **Bartlett**: Similar to Welch but uses non-overlapping segments

2. **Window Function**:
   
   * **Hanning**: General-purpose window with good frequency resolution
   * **Hamming**: Modified Hanning window with different coefficients
   * **None**: No windowing (may introduce spectral leakage)

3. **Segment Size**:
   
   * Controls the frequency resolution
   * Larger segments give finer frequency resolution but less averaging
   * Expressed as 2^N samples per segment

4. **Overlap**:
   
   * Percentage of overlap between segments (used with Welch's method)
   * Higher overlap increases the amount of averaging
   * Typical values range from 50% to 75%

5. **Plot Appearance**:
   
   * X-scale: Linear or logarithmic frequency axis
   * Y-scale: Linear or logarithmic amplitude axis
   * Plot style: Overlay or separate plots for multiple signals

FFT Analysis Step-by-Step
-----------------------

Here's a detailed walkthrough for performing FFT analysis:

1. **Load Files**:
   
   * Start by loading one or more OpenFAST output files containing the signals you want to analyze

2. **Access FFT Tab**:
   
   * Click on the FFT tab in the main navigation

3. **Select Signals**:
   
   * Choose the signals you want to analyze
   * For wind turbine analysis, common signals include:
     * Blade root moments (e.g., "RootMycX1")
     * Tower base moments (e.g., "TwrBsMxt")
     * Generator or shaft torque

4. **Configure FFT Parameters**:
   
   * For most wind turbine analysis, recommended settings are:
     * Averaging Method: Welch
     * Window Function: Hanning
     * Segment Size: 2^11 to 2^13 (adjust based on signal length)
     * Overlap: 50% to 75%

5. **Set Axis Scales**:
   
   * Select appropriate X and Y scales:
     * Logarithmic X-scale is useful for viewing a wide frequency range
     * Logarithmic Y-scale helps visualize peaks of different magnitudes

6. **Calculate FFT**:
   
   * Click the "Calculate FFT" button to generate the frequency domain plot

7. **Analyze Results**:
   
   * Identify dominant peaks in the frequency spectrum
   * Look for expected frequencies (e.g., 1P, 3P, tower frequencies)

8. **Add Annotations**:
   
   * Mark important frequencies using the annotation system
   * Common annotations for wind turbines:
     * 1P: Once-per-revolution frequency
     * 3P: Three times per revolution (for three-bladed turbines)
     * Tower natural frequencies
     * Blade mode frequencies

9. **Save or Export Results**:
   
   * Export the annotated FFT plot as HTML for documentation
   * Save annotation sets for future use

Example: Comparing Natural Frequencies
------------------------------------

Here's a specific example for identifying and comparing natural frequencies:

1. **Load baseline model and modified model files**:
   
   .. code-block:: text
      
      test_files/5MW_Land_DLL_WTurb.outb
      test_files/5MW_Land_BD_DLL_WTurb.outb

2. **Configure optimal FFT parameters**:
   
   * Averaging: Welch
   * Window: Hanning
   * Segment Size: 2^12
   * Overlap: 50%
   * X-scale: Logarithmic (to emphasize lower frequencies)

3. **Select tower base moments**:
   
   * Choose "TwrBsMxt" from both files
   * Click "Calculate FFT"

4. **Add annotations for known frequencies**:
   
   * Add 0.32 Hz with label "Tower FA" (fore-aft mode)
   * Add 0.31 Hz with label "Tower SS" (side-side mode)
   * Add 0.2 Hz with label "1P" (assuming 12 RPM rotor speed)
   * Add 0.6 Hz with label "3P"

5. **Analyze differences**:
   
   * Compare peak locations between baseline and modified model
   * Look for frequency shifts indicating structural changes
   * Identify if any peaks align with forcing frequencies (1P, 3P)

6. **Export the comparison**:
   
   * Click "Export FFT as HTML" to create a shareable document
   * Include annotations in the export

Advanced FFT Techniques
---------------------

For more advanced analysis:

1. **Segment Size Optimization**:
   
   * Smaller segments (e.g., 2^8): Better for statistical stability, less frequency resolution
   * Larger segments (e.g., 2^14): Higher frequency resolution, less averaging
   * Choose based on your signal length and analysis goals

2. **Window Function Selection**:
   
   * Hanning: General purpose, good compromise between leakage and resolution
   * Hamming: Slightly different mainlobe/sidelobe characteristics
   * No window: Maximum frequency resolution but may have spectral leakage

3. **Frequency Range Focus**:
   
   * Use X-axis limits to focus on specific frequency ranges
   * For wind turbines, often 0-2 Hz contains most relevant dynamics

4. **Multiple Signal Comparison**:
   
   * Compare the same signal across different files to identify changes
   * Compare different signals from the same file to identify relationships

Troubleshooting
-------------

Common issues with FFT analysis:

* **Low Resolution**: Increase segment size for better frequency resolution
* **Noisy Spectrum**: Use Welch's method with more averaging (smaller segments)
* **Missing Peaks**: Ensure your simulation time is long enough to capture low frequencies
* **Unexpected Harmonics**: Check for physical phenomena or numerical issues in the simulation