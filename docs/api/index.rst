=================
API Documentation
=================

This section provides documentation for the internal API of the Remote OpenFAST Plotter application.

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   app
   data_manager
   components
   utils
   html_exporter
   user_preferences
   callbacks
   tools

Core Modules
-----------

The application is organized around several core modules, each responsible for specific functionality:

app
~~~

The main application entry point:

* Initializes the Dash application
* Sets up server configuration
* Registers callbacks
* Handles command line arguments

data_manager
~~~~~~~~~~~

Data loading and management module:

* Parallel loading of OpenFAST files
* In-memory dataframe storage
* File information management

components
~~~~~~~~~

UI layout and components:

* Application layout definition
* Tab structure
* UI components for each function

utils
~~~~

Utility functions:

* Plot generation
* File path handling
* UI helper functions

Specialized Modules
-----------------

html_exporter
~~~~~~~~~~~

Handles the export of plots to standalone HTML:

* Adds metadata to exports
* Creates self-contained HTML
* Manages export styling

user_preferences
~~~~~~~~~~~~~

Manages user settings:

* Saving and loading preferences
* File path sets
* UI configuration

Callback Organization
------------------

The application's interactivity is managed through callbacks organized by function:

* File loading and management
* Signal selection
* Time domain plotting
* FFT analysis
* Phase analysis
* Export functionality
* Path management
* Preference handling

Tools Package
-----------

Specialized analysis tools:

* FFT analysis
* Phase analysis
* Signal selection helpers