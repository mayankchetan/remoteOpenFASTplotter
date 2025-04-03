'''
Remote OpenFAST Plotter - A DASH application to read and plot OpenFAST output files on remote computers

Features:
- Load and visualize multiple OpenFAST output files
- Interactive signal selection and plotting
- Customizable display options (overlay or separate plots)
- Direct HTML export for sharing and reporting
- Memory-efficient handling of large datasets
- Spectral (FFT) analysis with advanced configuration options
- Comprehensive HTML report generation with all plots and settings
'''

# Import Packages
import os
import sys
import argparse
import dash
import dash_bootstrap_components as dbc

# Add tools directory to sys.path for FFT module imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

# Import our application modules
from components import create_layout
from callbacks import register_callbacks
from data_manager import DATAFRAMES

# Initialize the Dash app with Bootstrap styling
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP, 
        'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css'
    ],
    suppress_callback_exceptions=True  # Allow dynamic components
)

# Set the app layout from our components module
app.layout = create_layout()

# Register all callbacks from our callbacks module
register_callbacks(app)

def run_server_with_retry(app, host='localhost', port=8050, max_retries=5):
    """
    Run the Dash server with automatic retry on port conflicts.
    
    Parameters:
    -----------
    app : dash.Dash
        The Dash application instance
    host : str
        Host to bind the server to
    port : int
        Initial port to try
    max_retries : int
        Maximum number of port increments to try
    
    """
    import socket
    import time
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"Port {port-1} is in use. Trying port {port}...")
            print(f"\nStarting Remote OpenFAST Plotter on http://{host}:{port}/")
            print("Press Ctrl+C to abort the application.")
            app.run(debug=True, host=host, port=port)
            break
        except OSError as e:
            # Socket error - port likely in use
            if "Address already in use" in str(e):
                port += 1
                time.sleep(2)  # Wait before trying the next port
            else:
                # Some other socket error, re-raise
                raise
    else:
        # We've exhausted our retries
        print(f"Could not find an available port after {max_retries} attempts.")
        print(f"Please specify a different port using the --port argument.")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Remote OpenFAST Plotter')
    parser.add_argument('--host', default='localhost', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=8050, help='Port to bind the server to')
    args = parser.parse_args()
    
    # Run the server with automatic retry
    run_server_with_retry(app, host=args.host, port=args.port)
