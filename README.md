# Remote OpenFAST Plotter

A Dash web application for reading and plotting OpenFAST output files on remote computers.

[![OpenFAST Plotter CI/CD](https://github.com/mayankchetan/remoteOpenFASTplotter/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/mayankchetan/remoteOpenFASTplotter/actions/workflows/ci-cd.yml)
[![Documentation Status](https://readthedocs.org/projects/remoteopenfastplotter/badge/?version=latest)](https://remoteopenfastplotter.readthedocs.io/en/latest/?badge=latest)

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

## Quick Start

### Installation

#### Using Conda (Recommended)

```bash
# Clone the repository
git clone https://github.com/mayankchetan/remoteOpenFASTplotter.git
cd remoteOpenFASTplotter

# Create and activate the conda environment
conda env create -f environment.yaml
conda activate remoteopenfast
```

#### Using pip

```bash
# Clone the repository
git clone https://github.com/mayankchetan/remoteOpenFASTplotter.git
cd remoteOpenFASTplotter

# Install dependencies
pip install -r requirements.txt
```

#### Using Docker

```bash
# Build the Docker image
docker build -t openfast-plotter .

# Run the container
docker run -p 8050:8050 openfast-plotter
```

### Basic Usage

1. Start the application:
   ```bash
   python app.py
   ```
2. Open a web browser and navigate to `http://localhost:8050`
3. Load OpenFAST output files and start exploring your data

For example files to test with:
```bash
python utils/download_test_files.py
```

## Documentation

Comprehensive documentation is available on ReadTheDocs:
[https://remoteopenfastplotter.readthedocs.io/en/latest/](https://remoteopenfastplotter.readthedocs.io/en/latest/?badge=latest)

The documentation includes:
- Detailed installation instructions
- User guides with examples
- API reference
- Developer documentation
- FFT analysis tutorials
- Phase analysis guides

## Project Structure

The application is organized with a modular architecture:

- `app.py` - Main entry point and server configuration
- `data_manager.py` - Data loading and storage functionality
- `utils.py` - Utility functions for plotting and data processing
- `components.py` - UI components and layout definitions
- `callbacks/` - Interactive callback functions organized by feature
- `tools/` - Specialized modules (e.g., FFT analysis, phase analysis)

## Development

### Running Tests

```bash
# Download test files if you haven't already
python utils/download_test_files.py

# Run all tests
python -m pytest

# Run tests with coverage report
python -m pytest --cov=. --cov-report=term
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Submit a pull request

See the [Development Guide](https://remoteopenfastplotter.readthedocs.io/en/latest/development/index.html) in the documentation for more details.

## Inspiration

This tool is inspired by:
- [pyDatView](https://github.com/ebranlard/pyDatView) - Python tool for plotting data from various file formats
- [WEIS visualization tools](https://github.com/WISDEM/WEIS) - Wind Energy with Integrated Servo-control
- [OpenFAST](https://github.com/OpenFAST/openfast) - Open-source wind turbine simulation tool

## License

This software is distributed under the Apache License, Version 2.0.

For license details, see the [LICENSE](LICENSE) file.

