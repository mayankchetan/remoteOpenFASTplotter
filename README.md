# Remote OpenFAST Plotter

A Dash web application for reading and plotting OpenFAST output files on remote computers.

[![OpenFAST Plotter CI/CD](https://github.com/mayankchetan/remoteOpenFASTplotter/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/mayankchetan/remoteOpenFASTplotter/actions/workflows/ci-cd.yml)

## Features

- **Fast Data Loading**: Efficiently loads OpenFAST output files using parallel processing
- **Interactive Plotting**: Dynamic plot generation based on selected signals
- **Flexible Visualization**: Plot multiple signals across multiple files
- **Comparison Mode**: Overlay plots from different files for easy comparison
- **Memory Efficiency**: Uses server-side DataFrame storage for improved performance with large datasets
- **Direct Export**: Export plots as standalone HTML files for sharing and reporting
- **FFT Analysis**: Frequency analysis with configurable parameters
- **Frequency Annotations**: Mark and label important frequencies in FFT plots
- **User-Friendly Interface**: Simple and intuitive UI with tooltips and visual feedback
- **File Path Management**: Save and reuse sets of OpenFAST file paths for quick access

## Installation

### Using Conda (Recommended)

1. Clone the repository
2. Create and activate the conda environment:
   ```
   conda env create -f environment.yaml
   conda activate remoteopenfast
   ```

### Using pip

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```
   python app.py
   ```
2. Open a web browser and navigate to `http://localhost:8050` (or the remote server's IP address and port)
3. Load OpenFAST output files:
   - Paste file paths in the textarea (one per line)
   - Click "Load Files" to process the data
   - View status messages and file indicators
   - Save frequently used file paths by entering a name and clicking "Save"
   - Load saved file path sets using the dropdown and "Load" button

4. Configure plots:
   - Select signals for Y axes (multiple signals supported)
   - Select signal for X axis (default is Time)
   - Choose display option (Overlay Files or Separate Files)
   - Click "Update Plot" to generate visualizations

5. Perform FFT Analysis:
   - Switch to the FFT Analysis tab
   - Configure FFT parameters (averaging method, windowing, etc.)
   - Add frequency annotations to mark important resonances or harmonics
   - Click "Calculate FFT" to generate FFT plots

6. Export and share:
   - Click "Export Plot as HTML" to download a standalone HTML file
   - Click "Export FFT as HTML" to download FFT results
   - Share the HTML files with others (no software needed to view)

## Testing with Example Files

For quick testing and demonstration, you can download example OpenFAST output files:

```bash
# Download test files to the test_files directory
python utils/download_test_files.py

# Optionally specify a different output directory
python utils/download_test_files.py --output /path/to/your/directory
```

This will download sample `.outb` files from the OpenFAST r-test repository and print their paths, which you can then copy and paste into the application.

## Project Structure

The application is organized with a modular architecture:

- `app.py` - Main entry point and server configuration
- `data_manager.py` - Data loading and storage functionality
- `utils.py` - Utility functions for plotting and data processing
- `components.py` - UI components and layout definitions
- `callbacks.py` - All interactive callback functions
- `tools/` - Specialized modules (e.g., FFT analysis)

For more information about the architecture, see [Architecture Documentation](docs/architecture.md).

## Running Tests Locally

To run the test suite locally:

1. Make sure you have the testing dependencies installed:
   ```bash
   pip install pytest pytest-cov flake8
   ```

2. Run the tests:
   ```bash
   # Run all tests
   python -m pytest
   
   # Run specific test file
   python -m pytest tests/test_utils.py
   
   # Run tests with coverage report
   python -m pytest --cov=. --cov-report=term
   ```

3. For faster feedback during development, you can run a specific test function:
   ```bash
   python -m pytest tests/test_utils.py::test_unique_identifiers -v
   
   # Run tests matching a pattern
   python -m pytest -k "fft"
   ```

Make sure to download the test files before running tests that depend on them:
```bash
python utils/download_test_files.py
```

## Docker Support

You can also run the application using Docker:

```bash
# Build the Docker image
docker build -t openfast-plotter .

# Run the container
docker run -p 8050:8050 openfast-plotter
```

## Requirements

- Python>=3.11
- Dash
- Dash Bootstrap Components
- Pandas
- Plotly
- NumPy
- OpenFAST I/O tools

## Development

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Submit a pull request

### Running in Debug Mode

```
python app.py
```

The app runs in debug mode by default, providing detailed error messages and auto-reloading when code changes.

## Inspiration

This tool is inspired by:
- [pyDatView](https://github.com/ebranlard/pyDatView) - Python tool for plotting data from various file formats
- [WEIS visualization tools](https://github.com/WISDEM/WEIS) - Wind Energy with Integrated Servo-control
- [OpenFAST](https://github.com/OpenFAST/openfast) - Open-source wind turbine simulation tool

## License

This software is distributed under the Apache License, Version 2.0.

For license details, see the [LICENSE](LICENSE) file.

