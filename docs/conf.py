# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = 'Remote OpenFAST Plotter'
copyright = '2025, Mayank Chetan'
author = 'Mayank Chetan'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '../assets/wind_turbine_plot.png'
html_favicon = '../assets/favicon.ico'

# -- Options for autodoc extension -------------------------------------------
autodoc_member_order = 'bysource'

# -- Options for intersphinx extension ---------------------------------------
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True