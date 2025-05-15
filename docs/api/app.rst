==========
Application
==========

The ``app.py`` module is the main entry point for the Remote OpenFAST Plotter application.

App Overview
-----------

The application is built using the Dash framework, which provides a reactive web interface for Python. The ``app.py`` module is responsible for:

* Initializing the Dash application
* Creating the server configuration
* Loading the user interface components
* Registering all callback functions
* Starting the web server

Key Components
-------------

Application Initialization
~~~~~~~~~~~~~~~~~~~~~~~~~

The Dash application is initialized with necessary configuration:

.. code-block:: python

    app = dash.Dash(
        __name__, 
        external_stylesheets=[
            dbc.themes.BOOTSTRAP, 
            dbc.icons.BOOTSTRAP,
            "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
        ],
        external_scripts=[
            "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML",
        ],
    )

    app.title = "OpenFAST Plotter"
    app.config.suppress_callback_exceptions = True

Server Configuration
~~~~~~~~~~~~~~~~~~~

The server is configured with appropriate settings:

.. code-block:: python

    server = app.server  # Expose the server variable for production
    
    # Add custom response headers for security
    @server.after_request
    def apply_security_headers(response):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

Layout Setup
~~~~~~~~~~~

The application layout is loaded from the components module:

.. code-block:: python

    # Set the application layout from components
    app.layout = create_layout()

Callbacks Registration
~~~~~~~~~~~~~~~~~~~~~

All interactive callbacks are registered using a modular approach:

.. code-block:: python

    # Register all callbacks
    register_callbacks(app)

The ``register_callbacks`` function is imported from the ``callbacks`` module and registers all callback functions that enable the application's interactivity.

Main Function
------------

The main function initializes the application and starts the server:

.. code-block:: python

    def main():
        """Run the application server."""
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Start the OpenFAST Plotter server')
        parser.add_argument('--host', type=str, default='127.0.0.1',
                            help='Host address (default: 127.0.0.1)')
        parser.add_argument('--port', type=int, default=8050,
                            help='Port to run the server on (default: 8050)')
        parser.add_argument('--debug', type=bool, default=True,
                            help='Run in debug mode (default: True)')
        args = parser.parse_args()
        
        # Start the server with automatic port retry
        max_retries = 5
        for retry in range(max_retries):
            try:
                app.run(host=args.host, port=args.port, debug=args.debug)
                break
            except OSError as e:
                if 'Address already in use' in str(e) and retry < max_retries - 1:
                    print(f"Port {args.port} is in use, trying port {args.port + 1}")
                    args.port += 1
                    continue
                raise

Command Line Arguments
--------------------

The application accepts several command line arguments:

* ``--host``: The host interface to bind to (default: 127.0.0.1)
* ``--port``: The port to run the server on (default: 8050)
* ``--debug``: Whether to run in debug mode (default: True)

For example:

.. code-block:: bash

   python app.py --host 0.0.0.0 --port 8051

Port Retry Logic
--------------

The application includes automatic port retry logic to handle cases where the default port is already in use:

1. The server attempts to start on the specified port
2. If that port is in use, it increments the port number and tries again
3. This process repeats up to a maximum number of retries

This feature enables the application to automatically find an available port when the default port is occupied.