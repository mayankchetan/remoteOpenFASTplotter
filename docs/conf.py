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

# Make sure template paths are absolute
templates_path = [
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '_templates'))]
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
# Make sure static paths are absolute
html_static_path = [
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '_static'))]
html_logo = '../assets/wind_turbine_plot.png'
html_favicon = '../assets/favicon.ico'

# Custom footer for all pages
html_show_sphinx = False  # Hide default Sphinx footer
html_show_copyright = True

# Ensure our templates are used
html_additional_pages = {}

# Add CSS to display the footer note - Make this more explicit
html_css_files = [
    'custom.css',
]

# Function to add custom CSS files when building on ReadTheDocs


def setup(app):
    app.add_css_file('custom.css')


html_context = {
    'display_github': True,
    'github_user': 'mayankchetan',
    'github_repo': 'remoteOpenFASTplotter',
    'github_version': 'main/docs/',
    'note_footer': 'Portions of this documentation were developed with assistance from GitHub Copilot, an AI tool powered by OpenAI technology.',
}

# -- Options for autodoc extension -------------------------------------------
autodoc_member_order = 'bysource'

# -- Options for intersphinx extension ---------------------------------------
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True
