"""
Test script to verify that saving preferences works correctly.
Run this from the command line to test if the preferences system is working.
"""

import os
from pathlib import Path
from user_preferences import (
    load_preferences, save_preferences, save_file_path_set, 
    get_saved_file_paths, PREFS_FILE
)

def test_preferences_file():
    """Test if preferences file is accessible and working properly"""
    print("\n--- Testing Preferences File Access ---")
    
    # Check if preferences file exists and is readable/writable
    if PREFS_FILE.exists():
        print(f"Preferences file exists at: {PREFS_FILE}")
        if os.access(PREFS_FILE, os.R_OK):
            print("File is readable")
        else:
            print("WARNING: File is not readable")
        
        if os.access(PREFS_FILE, os.W_OK):
            print("File is writable")
        else:
            print("WARNING: File is not writable")
            
        # Check parent directory permissions
        parent_dir = PREFS_FILE.parent
        print(f"Parent directory: {parent_dir}")
        if os.access(parent_dir, os.W_OK):
            print("Parent directory is writable")
        else:
            print("WARNING: Parent directory is not writable")
    else:
        print(f"Preferences file does not exist at: {PREFS_FILE}")
        
        # Check if parent directory exists and has write permissions
        parent_dir = PREFS_FILE.parent
        if parent_dir.exists():
            print(f"Parent directory exists: {parent_dir}")
            if os.access(parent_dir, os.W_OK):
                print("Parent directory is writable")
            else:
                print("WARNING: Parent directory is not writable")
        else:
            print(f"Parent directory does not exist: {parent_dir}")
            
    return PREFS_FILE.exists() and os.access(PREFS_FILE, os.W_OK)

def test_save_load_preferences():
    """Test if saving and loading preferences works properly"""
    print("\n--- Testing Save/Load Preferences ---")
    
    # Load current preferences
    prefs = load_preferences()
    print(f"Loaded preferences with keys: {list(prefs.keys())}")
    
    # Add a test entry
    test_name = "test_path_set_" + os.urandom(4).hex()
    test_paths = [f"/test/path/{i}.out" for i in range(3)]
    
    print(f"Saving test path set '{test_name}'")
    result = save_file_path_set(test_name, test_paths)
    print(f"Save result: {result}")
    
    # Reload and verify
    reloaded = load_preferences()
    saved_paths = reloaded.get("saved_file_paths", {})
    
    if test_name in saved_paths:
        print(f"Success! Test path set '{test_name}' found in reloaded preferences")
        print(f"Saved paths: {saved_paths[test_name]}")
        return True
    else:
        print(f"FAILURE: Test path set '{test_name}' not found in reloaded preferences")
        print(f"Available saved paths: {list(saved_paths.keys())}")
        return False

if __name__ == "__main__":
    print("=== Testing OpenFAST Plotter Preferences System ===")
    
    file_ok = test_preferences_file()
    if file_ok:
        save_load_ok = test_save_load_preferences()
        if save_load_ok:
            print("\n✅ All tests passed! Preferences system is working correctly.")
        else:
            print("\n❌ Save/load test failed. Preferences system is not working correctly.")
    else:
        print("\n❌ File access test failed. Please check file permissions.")
        
    # Display current saved path sets
    saved_paths = get_saved_file_paths()
    print("\nCurrently saved path sets:")
    if saved_paths:
        for name, paths in saved_paths.items():
            print(f"  - {name}: {len(paths)} paths")
    else:
        print("  (none)")
