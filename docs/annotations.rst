======================
Frequency Annotations
======================

This guide explains how to use the frequency annotation system in Remote OpenFAST Plotter, which allows you to mark and label important frequencies in FFT plots.

Why Use Annotations?
------------------

Frequency annotations are valuable for:

* Marking known excitation frequencies (1P, 3P, etc.)
* Highlighting system natural frequencies
* Creating consistent labels across multiple analyses
* Documenting findings in exported plots
* Comparing frequency peaks with expected values

Using the Annotation System
-------------------------

Adding Annotations
~~~~~~~~~~~~~~~~

In the FFT tab, you'll find the annotation controls:

1. Enter a frequency value (in Hz)
2. Add a descriptive label for the annotation
3. Click "Add" to place the annotation on the plot
4. Optionally select a color for better categorization

Annotations appear as vertical lines on the FFT plot with attached labels.

Managing Annotations
~~~~~~~~~~~~~~~~~

The application provides several tools for managing annotations:

* **Save Annotations**: Store a set of annotations with a name
* **Load Annotations**: Apply previously saved annotation sets to new plots
* **Remove**: Delete a specific annotation
* **Clear All**: Remove all annotations from the current plot

Annotation sets are saved between sessions, making them available for future use.

Common Annotation Practices
-------------------------

Wind Turbine Analysis
~~~~~~~~~~~~~~~~~~~

For wind turbine analysis, typical annotations include:

* **1P**: Once-per-revolution frequency (rotor rotation frequency)
* **3P**: Three-times-per-revolution (for three-bladed turbines)
* **Tower Frequencies**: First and second modes for fore-aft and side-side
* **Blade Frequencies**: First and higher flapwise and edgewise modes
* **Drivetrain Frequencies**: Torsional modes
* **Grid Frequency**: 50 Hz or 60 Hz depending on region

Naming Conventions
~~~~~~~~~~~~~~~~

Consistent naming helps with interpretation:

* Use a short, descriptive name ("1P", "Tower FA")
* Include the frequency value when helpful ("1P (0.2 Hz)")
* Use standardized color coding for different types of frequencies
* Be consistent across analyses for easier comparison

Example Workflow
--------------

Using annotations effectively:

1. **Create FFT Plot**:
   * Load your OpenFAST files
   * Configure FFT parameters
   * Generate frequency plots

2. **Add Known Frequencies**:
   * Add 1P frequency based on rotor speed
   * Add relevant multiples (3P, 6P, etc.)
   * Mark tower and blade modes if known

3. **Save Annotation Set**:
   * Name the set (e.g., "5MW Baseline")
   * Save for future use

4. **Compare with New Data**:
   * Load new simulation data
   * Apply the saved annotation set
   * Identify shifts or new peaks

5. **Export for Documentation**:
   * Export the annotated FFT plot as HTML
   * All annotations are included in the export

Best Practices
------------

For effective use of annotations:

* Create standard annotation sets for project types
* Document the meaning of annotations in reports
* Use color coding consistently (e.g., red for critical frequencies)
* Include both excitation and natural frequencies
* Compare annotated frequencies with design values