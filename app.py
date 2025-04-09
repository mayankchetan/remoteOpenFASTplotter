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
import time
import argparse
import dash
import dash_bootstrap_components as dbc

# Add tools directory to sys.path for FFT module imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

# Import our application modules
from components import create_layout
from callbacks import register_callbacks
from data_manager import DATAFRAMES

# Ensure assets directory exists
assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(assets_dir, exist_ok=True)

# Initialize the Dash app with Bootstrap styling
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP, 
        'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css'
    ],
    suppress_callback_exceptions=True,  # Allow dynamic components
    title="Remote OpenFAST Plotter",  # Set the webpage title
    assets_folder=assets_dir,  # Tell Dash where to find static assets
)

# Add custom CSS for fade-out effect
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}  <!-- Dash automatically includes the favicon -->
        {%css%}
        <style>
            /* Custom CSS for the fade-out effect */
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
            
            .fade-out {
                animation: fadeOut 2s forwards;
                animation-delay: 1s;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Set the app layout from our components module
app.layout = create_layout()

# Register all callbacks from our modular callbacks package
register_callbacks(app)

def run_server_with_retry(app, host='localhost', port=8050, max_retries=5):
    """
    Run the Dash server with automatic retry on port conflict.
    Will try incrementing the port number until it finds an available one.
    
    Parameters:
    -----------
    app : dash.Dash
        The Dash app instance
    host : str
        The hostname to bind to
    port : int
        The port to bind to
    max_retries : int
        Maximum number of times to retry on a different port
    """
    for i in range(max_retries):
        try:
            current_port = port + i
            print(f"Starting server on {host}:{current_port}")
            app.run(host=host, port=current_port, debug=True)
            break
        except OSError as e:
            if "Address already in use" in str(e) and i < max_retries - 1:
                print(f"Port {current_port} is in use, trying {current_port + 1}...")
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
