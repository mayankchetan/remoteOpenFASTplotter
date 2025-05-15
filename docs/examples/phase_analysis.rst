=============
Phase Analysis
=============

This example demonstrates the phase analysis capabilities of Remote OpenFAST Plotter for examining phase relationships between signals.

Phase Analysis Fundamentals
-------------------------

Phase analysis helps you understand the timing relationships between different signals. In wind turbine analysis, phase relationships can reveal:

* Structural dynamics and resonance conditions
* Control system response characteristics
* Interactions between different components
* Potential design issues where forces and responses are out of phase

Using the Phase Analysis Tab
--------------------------

The phase analysis tab provides specialized tools for examining signal phase relationships:

1. **Access the Phase Tab**:
   
   * Click on the "Phase" tab in the main navigation

2. **Configure Analysis**:
   
   * Select a reference signal
   * Choose one or more signals to compare against the reference
   * Set analysis parameters if available

3. **Generate Phase Plots**:
   
   * Click "Calculate Phase" to generate the analysis
   * View both magnitude and phase plots

4. **Interpret Results**:
   
   * Examine phase differences across frequency ranges
   * Look for 0°, 90°, or 180° phase relationships at key frequencies
   * Identify resonance points where phase shifts occur

Example: Tower-Blade Phase Relationships
--------------------------------------

Here's a step-by-step example analyzing the phase relationship between tower and blade motions:

1. **Load Files**:
   
   * Load your OpenFAST output files containing tower and blade measurements

2. **Setup Phase Analysis**:
   
   * Select "TwrBsMxt" (Tower base fore-aft moment) as the reference signal
   * Select "RootMycX1" (Blade 1 root out-of-plane moment) as the comparison signal

3. **Calculate Phase**:
   
   * Click "Calculate Phase" to generate the analysis plots

4. **Analyze Results**:
   
   * Look for frequencies where phase crosses -90° (indicates resonance)
   * Examine the magnitude plot to see if there are peaks at these frequencies
   * Identify frequencies where the phase is near 0° (in-phase motion) or 180° (counter-phase motion)

Interpreting Phase Plots
----------------------

Phase plots show how the phase angle between signals varies with frequency. Key aspects to examine:

1. **Phase Crossing -90°**:
   
   * Indicates a resonance condition
   * The structure is most responsive at these frequencies
   * Important to check if these align with common excitation frequencies (1P, 3P)

2. **0° Phase**:
   
   * Signals are in phase - moving together
   * Can indicate rigid body motion or strong coupling

3. **180° Phase**:
   
   * Signals are in counter-phase - opposing motion
   * Can indicate certain types of mode shapes or control interactions

4. **Phase Curve Slope**:
   
   * Steeper slopes around crossings indicate more damped systems
   * Gentler slopes may indicate less damping

Advanced Phase Analysis Techniques
-------------------------------

For more sophisticated analysis:

1. **Multiple Signal Comparison**:
   
   * Compare phase relationships across multiple components
   * Look for patterns in how different parts of the structure respond

2. **Operational Condition Comparison**:
   
   * Compare phase relationships under different operating conditions
   * Identify how structural dynamics change with wind speed, control settings, etc.

3. **Combining with FFT Analysis**:
   
   * Use FFT analysis to identify frequencies of interest
   * Then examine phase relationships at those specific frequencies

Example: Detecting Resonance Conditions
-------------------------------------

A practical example for identifying potential resonance issues:

1. **Initial Setup**:
   
   * Load simulation results from a turbine operational analysis
   * Navigate to the Phase tab

2. **Reference Selection**:
   
   * Select a forcing function as reference (e.g., "RotSpeed" or "WindVxi")
   * Select structural responses to analyze (tower motions, blade moments)

3. **Analysis Focus**:
   
   * Look particularly at frequencies near known excitation sources:
     * 1P (once-per-revolution)
     * 3P (three-times-per-revolution for three-bladed turbines)
     * Control frequencies

4. **Identifying Issues**:
   
   * Look for -90° phase crossings that align with excitation frequencies
   * Check magnitude plots for amplification at these frequencies
   * Document any potential resonance conditions for further investigation

Tips for Effective Phase Analysis
-------------------------------

* **Signal Quality**: Ensure signals have sufficient resolution and length for accurate phase calculation
* **Frequency Range**: Focus on the most relevant frequency range for your analysis (often 0-5 Hz for wind turbines)
* **Multiple References**: Try different reference signals to understand the system from various perspectives
* **Documentation**: Export plots with clear labels for inclusion in reports or presentations