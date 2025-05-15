===========
Contributing
===========

This guide provides information for contributing to the Remote OpenFAST Plotter project.

Contribution Workflow
-------------------

1. **Fork the Repository**:
   
   Fork the repository on GitHub to your personal account.

2. **Clone Your Fork**:
   
   .. code-block:: bash

      git clone https://github.com/YOUR-USERNAME/remote-openfast-plotter.git
      cd remote-openfast-plotter
      git remote add upstream https://github.com/NREL/remote-openfast-plotter.git

3. **Create a Branch**:
   
   Create a branch for your feature or bugfix:

   .. code-block:: bash

      git checkout -b feature-name

4. **Make Changes**:
   
   Make your changes to the codebase.

5. **Test Your Changes**:
   
   Run the test suite to ensure your changes don't break existing functionality:

   .. code-block:: bash

      python -m pytest

6. **Update Documentation**:
   
   Update or add documentation relevant to your changes.

7. **Commit Changes**:
   
   Commit your changes with a descriptive commit message:

   .. code-block:: bash

      git add .
      git commit -m "Add feature X" 

8. **Push Changes**:
   
   Push your branch to your fork:

   .. code-block:: bash

      git push origin feature-name

9. **Submit a Pull Request**:
   
   Open a pull request from your fork to the main repository.

Code Style Guidelines
-------------------

Please follow these style guidelines:

* Use consistent naming conventions
* Write docstrings for all functions and classes
* Include type hints where appropriate
* Follow PEP 8 style guidelines

Example:

.. code-block:: python

   def calculate_fft(signal, window='hanning'):
       """
       Calculate FFT of a signal with the specified window function.
       
       Args:
           signal (np.ndarray): Input time series signal
           window (str, optional): Window function name. Defaults to 'hanning'.
           
       Returns:
           tuple: (frequencies, amplitudes)
       """
       # Implementation
       return frequencies, amplitudes

Documentation
-----------

Documentation contributions are highly valued:

* Ensure all functions and classes have proper docstrings
* Update README.md with significant changes
* Add examples for new features
* Update installation instructions if dependencies change

When adding a new feature, please include:

1. API documentation
2. Usage examples
3. Explanation of the feature's purpose

Testing Requirements
------------------

New code should include tests:

* Unit tests for individual functions
* Integration tests for features
* Tests should cover both normal and edge cases
* Tests should be placed in the ``tests/`` directory

Feature Requests and Bug Reports
------------------------------

* For feature requests: Clearly describe the feature and its use case
* For bug reports: Include steps to reproduce, expected vs. actual behavior
* Include environment information (OS, Python version, dependencies)
* If possible, provide a minimal example demonstrating the issue

Thank you for contributing to Remote OpenFAST Plotter!