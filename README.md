# Remote OpenFAST Plotter

A Dash web application for reading and plotting OpenFAST output files on remote computers.

## Features

- **Fast Data Loading**: Efficiently loads OpenFAST output files using parallel processing
- **Interactive Plotting**: Dynamic plot generation based on selected signals
- **Flexible Visualization**: Plot multiple signals across multiple files
- **Comparison Mode**: Overlay plots from different files for easy comparison
- **Memory Efficiency**: Uses server-side DataFrame storage for improved performance with large datasets
- **Direct Export**: Export plots as standalone HTML files for sharing and reporting
- **User-Friendly Interface**: Simple and intuitive UI with tooltips and visual feedback

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

4. Configure plots:
   - Select signals for Y axes (multiple signals supported)
   - Select signal for X axis (default is Time)
   - Choose display option (Overlay Files or Separate Files)
   - Click "Update Plot" to generate visualizations

5. Export and share:
   - Click "Export Plot as HTML" to download a standalone HTML file
   - Share the HTML file with others (no software needed to view)

## Advanced Features

### Intelligent File Labels
The application automatically creates unique identifiers for files by analyzing path differences, making it easy to distinguish between similar files.

### Performance Optimization
- Parallel file loading for faster startup with multiple files
- Server-side DataFrame storage avoids serialization/deserialization overhead
- Efficient plotting with minimal data transformations

### Error Handling
- Detailed error reporting for file loading issues
- Clear visual feedback during processing
- Tooltips with full file paths and metadata

## File Structure

```
remoteOpenFASTplotter/
├── app.py                 # Main application file
├── requirements.txt       # pip dependencies
├── environment.yaml       # Conda environment specification
├── openfast_io/           # OpenFAST file readers
└── exports/               # Default directory for exported files
```

## Requirements

- Python 3.7+
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

[MIT License](LICENSE)
