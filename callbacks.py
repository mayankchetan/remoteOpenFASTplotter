"""
Callbacks for OpenFAST Plotter
Contains all application callbacks for interactivity

This module re-exports the register_callbacks function from the callbacks package
to maintain backward compatibility with existing imports.
"""

# Simply import and re-export the register_callbacks function
from callbacks import register_callbacks

# No need to redefine the function here since it's already defined in callbacks/__init__.py