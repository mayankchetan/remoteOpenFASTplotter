============
Installation
============

This guide covers how to install and set up the Remote OpenFAST Plotter application.

Prerequisites
------------

Before installing, ensure you have:

* Python 3.11 or higher
* pip or conda package manager
* Git (for cloning the repository)
* A modern web browser (Chrome, Firefox, Edge, or Safari)

Installation Methods
------------------

There are several ways to install Remote OpenFAST Plotter:

Using pip
~~~~~~~~~

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/mayankchetan/remoteOpenFASTplotter.git
      cd remoteOpenFASTplotter

2. Install dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

Using conda
~~~~~~~~~~

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/mayankchetan/remoteOpenFASTplotter.git
      cd remoteOpenFASTplotter

2. Create and activate a conda environment:

   .. code-block:: bash

      conda env create -f environment.yaml
      conda activate remoteopenfast

Using Docker
~~~~~~~~~~~

For containerized deployment:

1. Build the Docker image:

   .. code-block:: bash

      docker build -t openfast-plotter .

2. Run the container:

   .. code-block:: bash

      docker run -p 8050:8050 openfast-plotter

Starting the Application
----------------------

Once installed, you can start the application by running:

.. code-block:: bash

   python app.py

This will start the application server on localhost port 8050. Access it by opening a web browser and navigating to:

.. code-block:: text

   http://localhost:8050

Command Line Options
------------------

The application supports several command line options:

.. code-block:: bash

   python app.py --host 0.0.0.0 --port 8051

Common options include:

* ``--host``: Specify the host interface (default: 127.0.0.1)
* ``--port``: Specify the port (default: 8050)
* ``--debug``: Enable debug mode (default: True)

For remote access, use ``--host 0.0.0.0`` to bind to all network interfaces.

Downloading Test Files
--------------------

For testing, you can download sample OpenFAST output files:

.. code-block:: bash

   python utils/download_test_files.py

Troubleshooting
-------------

Common Issues
~~~~~~~~~~~~

1. **Port Already in Use**:

   If port 8050 is already in use, specify a different port:

   .. code-block:: bash

      python app.py --port 8051

2. **Missing Dependencies**:

   If you encounter import errors, ensure all dependencies are installed:

   .. code-block:: bash

      pip install -r requirements.txt

3. **File Permission Issues**:

   Ensure you have read access to the OpenFAST files you're trying to load.