============================================
Remote OpenFAST Plotter Documentation
============================================

.. image:: ../assets/wind_turbine_plot.png
   :width: 400
   :alt: Remote OpenFAST Plotter Logo
   :align: center

Welcome to the Remote OpenFAST Plotter documentation. This web-based application is designed for visualizing and analyzing OpenFAST simulation outputs, with a focus on wind turbine data analysis.

About Remote OpenFAST Plotter
-----------------------------

The Remote OpenFAST Plotter is a specialized tool for wind energy researchers and engineers who need to analyze OpenFAST simulation results. It provides a user-friendly, web-based interface accessible from any modern browser, making it ideal for:

* Working with simulation data on remote servers without transferring large files
* Interactive visualization of time series data from wind turbine simulations
* Performing frequency domain analysis with Fast Fourier Transform (FFT)
* Analyzing phase relationships between different signals
* Creating exportable, shareable visualizations

Features
--------

* **Fast Loading**: Efficiently loads OpenFAST output files using parallel processing
* **Time Domain Analysis**: Interactive plots of simulation data over time
* **FFT Analysis**: Frequency domain analysis with configurable parameters
* **Phase Analysis**: Examine phase relationships between selected signals
* **Frequency Annotations**: Mark and label important frequencies in FFT plots
* **File Path Management**: Save and reuse sets of file paths for analysis
* **HTML Export**: Generate standalone HTML files for sharing results
* **Remote Accessibility**: Access via web browser when running on remote machines

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   user_guide/index
   architecture
   api/index
   examples/index
   annotations
   development/index

Getting Started
--------------

A quick introduction to get started with Remote OpenFAST Plotter:

.. code-block:: bash

   # Install dependencies
   pip install -r requirements.txt

   # Start the application
   python app.py

   # Access the application
   # Open http://localhost:8050 in your browser

For testing with example data:

.. code-block:: bash

   # Download test OpenFAST files
   python utils/download_test_files.py

Documentation Development
------------------------

Portions of this documentation were developed with the assistance of GitHub Copilot, a generative AI tool based on OpenAI's technology. This includes the file management documentation and other supplementary content. For more details on how AI was used in the development process, see the :ref:`AI-assisted development <ai_assisted_development>` section.

Indices and tables
-----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

License
------

This software is distributed under the Apache License, Version 2.0.