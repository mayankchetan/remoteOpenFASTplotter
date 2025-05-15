==============
Development
==============

This section provides information for developers who want to contribute to the Remote OpenFAST Plotter project.

.. toctree::
   :maxdepth: 2
   :caption: Development:

   setup
   contributing
   testing
   extending

Development Environment Setup
---------------------------

To set up a development environment for Remote OpenFAST Plotter:

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/NREL/remote-openfast-plotter.git
      cd remote-openfast-plotter

2. Create a conda environment (recommended):

   .. code-block:: bash

      conda env create -f environment.yaml
      conda activate remoteopenfast

3. Install development dependencies:

   .. code-block:: bash

      pip install pytest pytest-cov flake8

Code Organization
---------------

The application follows a modular architecture:

* ``app.py``: Main entry point
* ``data_manager.py``: Data loading and management
* ``components.py``: UI layout and components
* ``utils.py``: Utility functions
* ``callbacks/``: Organized callback modules
* ``tools/``: Specialized analysis modules
* ``tests/``: Test suite

Testing
------

The project includes a comprehensive test suite:

.. code-block:: bash

   # Run all tests
   python -m pytest

   # Run with coverage report
   python -m pytest --cov=. --cov-report=term

   # Run specific test
   python -m pytest tests/test_utils.py -v

Recommended development workflow:

1. Write tests for your changes first
2. Implement your changes
3. Run tests to verify functionality
4. Submit a pull request

Adding New Features
-----------------

When adding new features:

1. **New UI Component**:
   Add to ``components.py`` and integrate into the layout

2. **New Analysis Feature**:
   Add core logic to ``utils.py`` or create a new module in ``tools/``

3. **New Interactive Feature**:
   Create callback functions in appropriate modules within ``callbacks/``

4. **Documentation**:
   Update relevant documentation and add examples

Building Documentation
--------------------

To build this documentation locally:

.. code-block:: bash

   cd docs
   sphinx-build -b html . _build/html

View the generated documentation in ``_build/html/index.html``.