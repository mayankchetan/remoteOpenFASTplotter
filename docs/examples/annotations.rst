===================
Working with Annotations
===================

This example demonstrates how to effectively use the frequency annotation system in Remote OpenFAST Plotter for wind turbine analysis.

Understanding Frequency Annotations
--------------------------------

Frequency annotations allow you to mark important frequencies in FFT plots, helping you:

* Identify important peaks and frequencies
* Document known system frequencies
* Create consistent labeling across analyses
* Compare observed frequencies with theoretical values

Creating and Managing Annotations
------------------------------

Follow these steps to work with frequency annotations effectively:

1. **Accessing the Annotation System**:
   
   * Navigate to the FFT tab
   * Locate the annotation controls in the sidebar

2. **Adding Single Annotations**:
   
   * Enter a frequency value (in Hz)
   * Provide a descriptive label
   * Optionally choose a color
   * Click "Add" to place it on the plot

3. **Managing Annotation Sets**:
   
   * Enter a name for your annotation set
   * Click "Save" to store the current annotations
   * Use the dropdown to select and load saved annotation sets

4. **Applying to New Data**:
   
   * Load different OpenFAST files
   * Load your saved annotation set
   * Compare peaks with your annotations

Example: Wind Turbine Frequency Identification
-------------------------------------------

Here's a practical example for a 5MW wind turbine operating at 12 RPM:

1. **Calculate Key Frequencies**:
   
   * 1P = 12/60 = 0.2 Hz (once per revolution)
   * 3P = 0.6 Hz (three times per revolution)
   * Tower first fore-aft: ~0.32 Hz (from modal analysis)
   * First blade flapwise: ~0.7 Hz (from modal analysis)

2. **Create Annotations**:
   
   * Add 0.2 Hz as "1P" (red color)
   * Add 0.6 Hz as "3P" (red color)
   * Add 0.32 Hz as "Tower FA" (blue color)
   * Add 0.7 Hz as "Blade Flap" (green color)

3. **Save the Annotation Set**:
   
   * Name it "5MW Standard Frequencies"
   * Click "Save"

4. **Apply to Analysis**:
   
   * Generate FFT plots for relevant signals
   * Look for peaks near the annotated frequencies
   * Identify potential resonance issues

Color Coding for Clarity
----------------------

Establish a consistent color coding scheme for your annotations:

* **Red**: Forcing frequencies (1P, 3P, 6P, grid frequency)
* **Blue**: Tower natural frequencies
* **Green**: Blade natural frequencies
* **Purple**: Drivetrain natural frequencies
* **Orange**: Control system frequencies

This consistent color scheme makes it easier to visually categorize frequencies in complex plots.

Annotation Best Practices
----------------------

Follow these guidelines for effective annotations:

1. **Consistent Naming**:
   
   * Use standardized abbreviations (1P, 3P, etc.)
   * Include mode number and direction (e.g., "1st Tower FA")
   * Be consistent across projects

2. **Frequency Precision**:
   
   * Use appropriate decimal precision based on your analysis needs
   * For most wind turbine work, 2-3 decimal places is sufficient

3. **Minimal Overlapping**:
   
   * Don't overcrowd the plot with too many annotations
   * Prioritize the most important frequencies

4. **Documentation**:
   
   * Include the source of frequency values (theoretical, modal analysis, etc.)
   * Document any assumptions made when determining frequencies

Example: Harmonics Analysis
------------------------

Analyzing harmonics in a wind turbine:

1. **Setup**:
   
   * Load OpenFAST file with significant rotor imbalance
   * Calculate FFT for blade root moments

2. **Create Harmonic Annotations**:
   
   Assuming 0.2 Hz as the 1P frequency:
   
   * Add 0.2 Hz as "1P" (red)
   * Add 0.4 Hz as "2P" (lighter red)
   * Add 0.6 Hz as "3P" (red)
   * Add 0.8 Hz as "4P" (lighter red)
   * Add 1.0 Hz as "5P" (lighter red)

3. **Analysis**:
   
   * Look for higher amplitudes at 1P (mass imbalance)
   * Look for higher amplitudes at 2P (aerodynamic imbalance)
   * Check if any harmonics align with natural frequencies

Combining Annotations with Modal Analysis
---------------------------------------

For more advanced analysis:

1. **Import Frequencies from Modal Analysis**:
   
   * Use results from an external modal analysis tool
   * Create annotations for each significant mode

2. **Compare with Observed Peaks**:
   
   * Load turbine simulation data
   * Apply modal frequency annotations
   * Look for alignment or shifts between theoretical and observed frequencies

3. **Document Findings**:
   
   * Export plots with annotations
   * Note any significant discrepancies
   * Update your structural models if needed

Exporting Annotated Plots
-----------------------

To share your annotated FFT analysis:

1. **Ensure Annotations are Visible**:
   
   * Verify annotations appear correctly on the plot
   * Adjust colors and positions if needed

2. **Export to HTML**:
   
   * Click "Export FFT as HTML"
   * Save the file with a descriptive name

3. **Include in Reports**:
   
   * The exported HTML can be opened in any browser
   * All annotations are preserved
   * Interactive features remain functional