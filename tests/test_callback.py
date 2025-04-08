"""
Test utility for direct testing of the save_file_path_set function and the callback.
Run this script independently to check if the callback logic works correctly.
"""

import os
from user_preferences import (save_file_path_set, get_saved_file_paths, 
                             load_preferences, save_preferences)
from dash import html

def simulate_callback_logic():
    """Simulate the save_current_paths callback logic directly"""
    print("\n=== Testing Callback Logic ===")
    
    # Simulate inputs
    path_set_name = "test_from_callback_sim"
    file_paths_text = "/path/to/file1.out\n/path/to/file2.out\n/path/to/file3.out"
    
    # Split the text into a list of file paths (as done in callback)
    file_paths = [path.strip() for path in file_paths_text.split("\n") if path.strip()]
    print(f"Parsed {len(file_paths)} file paths")
    
    # Save the file paths
    print(f"Calling save_file_path_set with name='{path_set_name}' and {len(file_paths)} paths")
    success = save_file_path_set(path_set_name, file_paths)
    print(f"save_file_path_set returned {success}")
    
    # Update the dropdown options (as done in callback)
    saved_paths = get_saved_file_paths()
    print(f"After save, get_saved_file_paths returned {len(saved_paths)} entries: {list(saved_paths.keys())}")
    options = [{"label": name, "value": name} for name in saved_paths.keys()]
    
    # Check if our test set was saved
    if path_set_name in saved_paths:
        print(f"✅ Success! Found '{path_set_name}' in saved paths")
        print(f"Saved paths: {saved_paths[path_set_name]}")
    else:
        print(f"❌ Failed! '{path_set_name}' not found in saved paths")
    
    return success

def check_file_permissions():
    """Check file permissions on the preferences file"""
    print("\n=== Checking File Permissions ===")
    prefs_file = os.path.expanduser("~/.openfast_plotter/preferences.json")
    prefs_dir = os.path.dirname(prefs_file)
    
    # Check directory
    print(f"Preferences directory: {prefs_dir}")
    if os.path.exists(prefs_dir):
        print("✅ Directory exists")
        if os.access(prefs_dir, os.W_OK):
            print("✅ Directory is writable")
        else:
            print("❌ Directory is NOT writable")
    else:
        print("❌ Directory does NOT exist")
        
    # Check file
    print(f"\nPreferences file: {prefs_file}")
    if os.path.exists(prefs_file):
        print("✅ File exists")
        if os.access(prefs_file, os.R_OK):
            print("✅ File is readable")
        else:
            print("❌ File is NOT readable")
            
        if os.access(prefs_file, os.W_OK):
            print("✅ File is writable")
        else:
            print("❌ File is NOT writable")
            
        # Check file size
        file_size = os.path.getsize(prefs_file)
        print(f"File size: {file_size} bytes")
    else:
        print("❌ File does NOT exist")
    
    return os.path.exists(prefs_file) and os.access(prefs_file, os.W_OK)

if __name__ == "__main__":
    print("=== OpenFAST Plotter Callback Test ===")
    
    # Check file permissions
    permissions_ok = check_file_permissions()
    
    if permissions_ok:
        # Try the callback logic
        callback_result = simulate_callback_logic()
        
        if callback_result:
            print("\n✅ SUCCESS: The callback logic works correctly!")
            print("If the app still doesn't save paths, the issue might be with the UI components or callback connections.")
        else:
            print("\n❌ FAILURE: The callback logic failed.")
            print("Check the error messages above for details.")
    else:
        print("\n❌ FAILURE: File permission issues detected.")
        print("Fix the file permissions before continuing.")
