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
    "saved_file_paths": {},  # New field for storing saved file path sets
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
    if not PREFS_DIR.exists():
        PREFS_DIR.mkdir(parents=True, exist_ok=True)


def load_preferences():
    """Load preferences from file or create default"""
    ensure_prefs_dir()

    if not PREFS_FILE.exists():
        # Create default preferences
        with open(PREFS_FILE, 'w') as f:
            json.dump(DEFAULT_PREFERENCES, f, indent=2)
        return DEFAULT_PREFERENCES.copy()

    try:
        with open(PREFS_FILE, 'r') as f:
            prefs = json.load(f)

        # Ensure all expected sections exist
        for key, value in DEFAULT_PREFERENCES.items():
            if key not in prefs:
                prefs[key] = value

        return prefs
    except Exception as e:
        print(f"Error loading preferences: {e}")
        return DEFAULT_PREFERENCES.copy()


def save_preferences(preferences):
    """Save preferences to file"""
    ensure_prefs_dir()

    try:
        # Print contents being saved for debugging
        print(f"Saving preferences to {PREFS_FILE}")
        print(f"Saved file paths: {preferences.get('saved_file_paths', {})}")

        # Ensure file is writable
        if PREFS_FILE.exists() and not os.access(PREFS_FILE, os.W_OK):
            print(f"WARNING: Preferences file {PREFS_FILE} is not writable!")
            return False

        # Write with explicit flush and error checking
        with open(PREFS_FILE, 'w') as f:
            json.dump(preferences, f, indent=2)
            f.flush()
            os.fsync(f.fileno())  # Ensure data is written to disk

        # Verify file was updated correctly
        if PREFS_FILE.exists():
            file_size = PREFS_FILE.stat().st_size
            print(f"Preferences file saved. Size: {file_size} bytes")
            return True
        else:
            print("ERROR: Preferences file does not exist after saving!")
            return False
    except Exception as e:
        import traceback
        print(f"ERROR saving preferences: {e}")
        print(traceback.format_exc())
        return False


def update_recent_files(files, max_files=10):
    """Update the list of recently opened files"""
    preferences = load_preferences()

    # Add new files to the front of the list
    recent = preferences.get("recent_files", [])

    # Remove files that are already in the list (to avoid duplicates)
    for file in files:
        if file in recent:
            recent.remove(file)

    # Add new files at the beginning
    recent = files + recent

    # Trim to max_files
    recent = recent[:max_files]

    # Update preferences
    preferences["recent_files"] = recent
    save_preferences(preferences)

# Functions to save favorite signals


def update_favorite_signals(signals):
    """Save favorite signals"""
    preferences = load_preferences()
    preferences["favorite_signals"] = signals
    save_preferences(preferences)

# Save FFT settings


def save_fft_settings(settings):
    """Save FFT settings"""
    preferences = load_preferences()
    preferences["fft_settings"] = settings
    save_preferences(preferences)

# Save custom annotations


def save_custom_annotations(annotations):
    """Save custom annotations"""
    preferences = load_preferences()
    preferences["custom_annotations"] = annotations
    save_preferences(preferences)

# Save plot settings


def save_plot_settings(settings):
    """Save plot settings"""
    preferences = load_preferences()
    preferences["plot_settings"] = settings
    save_preferences(preferences)

# New functions for saved file paths


def save_file_path_set(name, file_paths):
    """
    Save a set of file paths with a given name

    Parameters:
    -----------
    name : str
        Name to identify the saved file path set
    file_paths : list
        List of file paths to save

    Returns:
    --------
    bool : True if successful
    """
    # Load current preferences
    preferences = load_preferences()

    # Ensure saved_file_paths exists in preferences
    if "saved_file_paths" not in preferences:
        preferences["saved_file_paths"] = {}

    # Debug information
    print(
        f"DEBUG: save_file_path_set called with name='{name}', paths={file_paths}")
    print(
        f"Current saved paths before update: {preferences.get('saved_file_paths', {})}")

    # Save the paths
    preferences["saved_file_paths"][name] = file_paths

    # Write back to file
    result = save_preferences(preferences)

    # Debug: check if successful
    if result:
        print(
            f"Successfully saved path set '{name}' with {len(file_paths)} paths")
        # Verify by reloading
        reloaded = load_preferences()
        if name in reloaded.get("saved_file_paths", {}):
            print(f"Verified: path set '{name}' is in reloaded preferences")
            print(f"Saved paths: {reloaded['saved_file_paths'][name]}")
        else:
            print(
                f"FAILURE: path set '{name}' not found in reloaded preferences!")
    else:
        print(f"Failed to save path set '{name}'")

    return result


def get_saved_file_paths():
    """
    Get all saved file path sets

    Returns:
    --------
    dict : Dictionary of saved file path sets {name: [paths]}
    """
    preferences = load_preferences()
    return preferences.get("saved_file_paths", {})


def delete_saved_file_path_set(name):
    """
    Delete a saved file path set

    Parameters:
    -----------
    name : str
        Name of the file path set to delete

    Returns:
    --------
    bool : True if successful, False if name not found
    """
    preferences = load_preferences()
    if "saved_file_paths" in preferences and name in preferences["saved_file_paths"]:
        del preferences["saved_file_paths"][name]
        return save_preferences(preferences)
    return False


def rename_saved_file_path_set(old_name, new_name):
    """
    Rename a saved file path set

    Parameters:
    -----------
    old_name : str
        Current name of the file path set
    new_name : str
        New name for the file path set

    Returns:
    --------
    bool : True if successful, False if old_name not found
    """
    preferences = load_preferences()
    if "saved_file_paths" in preferences and old_name in preferences["saved_file_paths"]:
        file_paths = preferences["saved_file_paths"][old_name]
        preferences["saved_file_paths"][new_name] = file_paths
        del preferences["saved_file_paths"][old_name]
        return save_preferences(preferences)
    return False
