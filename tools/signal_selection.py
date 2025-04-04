"""
Module for signal selection logic.
"""

def get_signals(signal_names):
    """Validate and return a list of signals."""
    if not signal_names:
        return []
    if any(not isinstance(name, str) or name == "InvalidSignal" for name in signal_names):
        raise ValueError("Invalid signal names provided")
    return signal_names
