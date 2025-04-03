"""
User Preferences Manager for OpenFAST Plotter
Handles saving and loading of user preferences to/from a JSON file in the user's home directory
"""

import os
import json
from pathlib import Path

# Define the preferences file location in the user's home directory
PREFS_DIR = Path.home() / ".openfast_plotter"
PREFS_FILE = PREFS_DIR / "preferences.json"

# Default preferences
DEFAULT_PREFERENCES = {
    "recent_files": [],
    "favorite_signals": [],
    "custom_annotations": [],
    "fft_settings": {
        "averaging": "Welch",
        "windowing": "hamming",
        "n_exp": 15,
        "detrend": True,
        "xscale": "linear", 
        "plot_style": "overlay",
        "x_limit": 5
    },
    "plot_settings": {
        "plot_option": "overlay"
    }
}

def ensure_prefs_dir():
    """Ensure preferences directory exists"""
    PREFS_DIR.mkdir(exist_ok=True)

def load_preferences():
    """
    Load user preferences from the preferences file
    
    Returns:
    --------
    dict
        User preferences dictionary
    """
    ensure_prefs_dir()
    
    if not PREFS_FILE.exists():
        # Create default preferences if file doesn't exist
        save_preferences(DEFAULT_PREFERENCES)
        return DEFAULT_PREFERENCES.copy()
    
    try:
        with open(PREFS_FILE, 'r') as f:
            prefs = json.load(f)
            # Ensure all default keys are present
            for key, value in DEFAULT_PREFERENCES.items():
                if key not in prefs:
                    prefs[key] = value
                elif isinstance(value, dict) and key in prefs:
                    # Ensure nested settings have all keys
                    for subkey, subvalue in value.items():
                        if subkey not in prefs[key]:
                            prefs[key][subkey] = subvalue
            return prefs
    except (IOError, json.JSONDecodeError):
        # Return defaults if file can't be read
        return DEFAULT_PREFERENCES.copy()

def save_preferences(preferences):
    """
    Save user preferences to the preferences file
    
    Parameters:
    -----------
    preferences : dict
        User preferences dictionary to save
    """
    ensure_prefs_dir()
    try:
        with open(PREFS_FILE, 'w') as f:
            json.dump(preferences, f, indent=2)
    except IOError:
        print(f"Warning: Could not save preferences to {PREFS_FILE}")

def update_recent_files(files, max_files=10):
    """
    Update the list of recent files in the preferences
    
    Parameters:
    -----------
    files : list
        List of file paths to add
    max_files : int
        Maximum number of recent files to keep
    """
    prefs = load_preferences()
    
    # Get current recent files
    recent_files = prefs.get("recent_files", [])
    
    # Add new files, avoiding duplicates
    for file in files:
        if file in recent_files:
            # Move to the front if already exists
            recent_files.remove(file)
        recent_files.insert(0, file)
    
    # Trim to max length
    prefs["recent_files"] = recent_files[:max_files]
    save_preferences(prefs)
    return prefs["recent_files"]

def update_favorite_signals(signals):
    """
    Update favorite signals in the preferences
    
    Parameters:
    -----------
    signals : list
        List of signal names to save as favorites
    """
    prefs = load_preferences()
    prefs["favorite_signals"] = signals
    save_preferences(prefs)
    return prefs["favorite_signals"]

def save_fft_settings(settings):
    """
    Save FFT analysis settings to preferences
    
    Parameters:
    -----------
    settings : dict
        Dictionary of FFT settings
    """
    prefs = load_preferences()
    prefs["fft_settings"].update(settings)
    save_preferences(prefs)
    return prefs["fft_settings"]

def save_custom_annotations(annotations):
    """
    Save custom frequency annotations to preferences
    
    Parameters:
    -----------
    annotations : list
        List of annotation objects (dicts with 'freq' and 'label' keys)
    """
    prefs = load_preferences()
    prefs["custom_annotations"] = annotations
    save_preferences(prefs)
    return prefs["custom_annotations"]

def save_plot_settings(settings):
    """
    Save plot settings to preferences
    
    Parameters:
    -----------
    settings : dict
        Dictionary of plot settings
    """
    prefs = load_preferences()
    prefs["plot_settings"].update(settings)
    save_preferences(prefs)
    return prefs["plot_settings"]
