=======
Testing
=======

This guide covers testing the Remote OpenFAST Plotter application.

Testing Framework
---------------

The project uses pytest as its testing framework. Tests are located in the ``tests/`` directory and can be run using the ``pytest`` command.

Running Tests
-----------

To run the full test suite:

.. code-block:: bash

   python -m pytest

To run with coverage reporting:

.. code-block:: bash

   python -m pytest --cov=. --cov-report=term

To run a specific test file:

.. code-block:: bash

   python -m pytest tests/test_utils.py

To run a specific test function:

.. code-block:: bash

   python -m pytest tests/test_utils.py::test_function_name -v

Test Files
---------

For running tests that require OpenFAST output files, you can download test files using:

.. code-block:: bash

   python utils/download_test_files.py

This will download sample ``.outb`` files to the ``test_files`` directory.

Test Structure
------------

The test suite is organized by module:

* ``test_app.py``: Tests for the main application setup
* ``test_app_with_files.py``: Integration tests using actual OpenFAST files
* ``test_utils.py``: Tests for utility functions
* ``test_fft_analysis.py``: Tests for FFT analysis functionality
* ``test_html_export.py``: Tests for HTML export functionality
* ``test_preferences.py``: Tests for user preferences management
* ``test_callback_modules.py``: Tests for callback modules
* ``test_signal_selection.py``: Tests for signal selection functionality

Writing Tests
-----------

When writing tests for Remote OpenFAST Plotter:

1. **Unit Tests**: Test individual functions in isolation

   .. code-block:: python

      def test_unique_identifiers():
          """Test the generation of unique identifiers from file paths."""
          paths = ['/path/to/file1.outb', '/path/to/file2.outb']
          identifiers = get_unique_identifiers(paths)
          assert len(identifiers) == 2
          assert identifiers[0] != identifiers[1]

2. **Integration Tests**: Test components working together

   .. code-block:: python

      def test_file_loading(app_instance):
          """Test loading of OpenFAST files."""
          # Arrange
          file_paths = ['test_files/5MW_Land_DLL_WTurb.outb']
          
          # Act
          store_dataframes(file_paths)
          
          # Assert
          assert len(DATAFRAMES) == 1
          assert 'Time' in DATAFRAMES[file_paths[0]].columns

3. **Mocking Dependencies**: Use pytest fixtures and mocks when needed

   .. code-block:: python

      @pytest.fixture
      def mock_dataframe():
          """Create a mock dataframe for testing."""
          return pd.DataFrame({
              'Time': [0, 1, 2],
              'Signal1': [10, 20, 30]
          })

Test Coverage
-----------

Aim for high test coverage of the codebase:

* Run coverage reports to identify untested code
* Focus on testing complex logic and edge cases
* Include tests for error handling
* Test both positive and negative scenarios

.. code-block:: bash

   # Generate HTML coverage report
   python -m pytest --cov=. --cov-report=html
   
   # View the report in browser
   open htmlcov/index.html

Continuous Integration
--------------------

The project uses GitHub Actions for continuous integration:

* Tests run automatically on pull requests
* Code quality checks are performed
* Test failures block merging of pull requests

See ``.github/workflows/ci-cd.yml`` for the CI configuration.