import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch

# Functions from user_preferences.py (assuming it's in the root directory)
from user_preferences import (
    load_preferences,
    save_preferences,
    save_file_path_set,
    get_saved_file_paths,
    delete_saved_file_path_set,
    rename_saved_file_path_set,
    DEFAULT_PREFERENCES
)


@pytest.fixture
def mock_prefs_file(tmp_path):
    """Fixture to mock PREFS_FILE and PREFS_DIR to use a temporary directory."""
    temp_prefs_dir = tmp_path / ".openfast_plotter"
    temp_prefs_file = temp_prefs_dir / "preferences.json"

    with patch('user_preferences.PREFS_FILE', temp_prefs_file):
        with patch('user_preferences.PREFS_DIR', temp_prefs_dir):
            # Ensure the temp directory exists
            temp_prefs_dir.mkdir(parents=True, exist_ok=True)
            yield temp_prefs_file


def test_load_default_preferences_if_file_not_exist(mock_prefs_file):
    """Test that default preferences are loaded if the preferences file does not exist."""
    prefs = load_preferences()
    assert prefs == DEFAULT_PREFERENCES
    assert mock_prefs_file.exists()  # load_preferences should create it


def test_save_and_load_preferences(mock_prefs_file):
    """Test saving and then loading preferences."""
    if mock_prefs_file.exists():  # Ensure clean state
        mock_prefs_file.unlink()
    test_data = {"test_key": "test_value", "saved_file_paths": {}}

    # Create a custom preferences dict to save
    custom_prefs = DEFAULT_PREFERENCES.copy()
    custom_prefs.update(test_data)

    assert save_preferences(custom_prefs) is True

    loaded_prefs = load_preferences()
    assert loaded_prefs["test_key"] == "test_value"
    for key in DEFAULT_PREFERENCES:
        assert key in loaded_prefs


def test_save_file_path_set(mock_prefs_file):
    """Test saving a new set of file paths."""
    if mock_prefs_file.exists():  # Ensure clean state before saving
        mock_prefs_file.unlink()
    path_set_name = "my_test_set"
    file_paths = ["/path/to/file1.out", "/path/to/file2.txt"]

    assert save_file_path_set(path_set_name, file_paths) is True

    saved_paths = get_saved_file_paths()
    assert path_set_name in saved_paths
    assert saved_paths[path_set_name] == file_paths


def test_get_saved_file_paths_empty(mock_prefs_file):
    """Test getting saved file paths when none are saved (should return default or empty)."""
    # Ensure a clean state for this specific test by removing the file if it exists.
    # The mock_prefs_file fixture provides a unique path, but this adds
    # robustness.
    if mock_prefs_file.exists():
        mock_prefs_file.unlink()

    # load_preferences() will create a default file if it doesn't exist.
    # get_saved_file_paths() calls load_preferences().
    saved_paths = get_saved_file_paths()
    assert saved_paths == {}, "Expected empty saved_file_paths from a fresh/default preferences file."


def test_get_saved_file_paths_multiple_sets(mock_prefs_file):
    """Test saving and retrieving multiple path sets."""
    if mock_prefs_file.exists():
        mock_prefs_file.unlink()
    set1_name = "sim_run_1"
    set1_paths = ["/sim/run1/data.out", "/sim/run1/log.txt"]
    set2_name = "experiment_alpha"
    set2_paths = ["/exp/alpha/results.csv"]

    assert save_file_path_set(set1_name, set1_paths) is True
    assert save_file_path_set(set2_name, set2_paths) is True

    saved_paths = get_saved_file_paths()
    assert len(saved_paths) == 2
    assert saved_paths[set1_name] == set1_paths
    assert saved_paths[set2_name] == set2_paths


def test_overwrite_existing_file_path_set(mock_prefs_file):
    """Test that saving a path set with an existing name overwrites it."""
    if mock_prefs_file.exists():
        mock_prefs_file.unlink()
    path_set_name = "dataset_main"
    initial_paths = ["/data/v1/file.out"]
    updated_paths = ["/data/v2/file_new.out", "/data/v2/another.dat"]

    assert save_file_path_set(path_set_name, initial_paths) is True
    retrieved_paths = get_saved_file_paths()
    assert retrieved_paths[path_set_name] == initial_paths

    assert save_file_path_set(path_set_name, updated_paths) is True
    retrieved_paths_updated = get_saved_file_paths()
    assert retrieved_paths_updated[path_set_name] == updated_paths

# Tests based on the logic from tests/test_callback.py
# (simulate_callback_logic)


def test_simulate_callback_save_logic(mock_prefs_file):
    """Simulate the save_current_paths callback logic for saving a path set."""
    path_set_name = "test_from_callback_sim_pytest"
    file_paths_text = "/path/to/sim_file1.out\n/path/to/sim_file2.out\n/path/to/sim_file3.out"

    # Logic from callback: split text into list of paths
    file_paths = [path.strip()
                  for path in file_paths_text.split("\n") if path.strip()]

    # This test creates a new path set, ensure clean state
    if mock_prefs_file.exists():
        mock_prefs_file.unlink()

    assert save_file_path_set(path_set_name, file_paths) is True

    # Verify saved
    saved_path_sets = get_saved_file_paths()
    assert path_set_name in saved_path_sets
    assert saved_path_sets[path_set_name] == file_paths


def test_delete_saved_file_path_set(mock_prefs_file):
    """Test deleting a saved file path set."""
    if mock_prefs_file.exists():
        mock_prefs_file.unlink()
    path_set_name = "to_be_deleted"
    file_paths = ["/delete/me.out"]

    assert save_file_path_set(path_set_name, file_paths) is True
    saved_paths = get_saved_file_paths()
    assert path_set_name in saved_paths

    assert delete_saved_file_path_set(path_set_name) is True
    deleted_paths = get_saved_file_paths()
    assert path_set_name not in deleted_paths


def test_delete_non_existent_file_path_set(mock_prefs_file):
    """Test deleting a non-existent file path set returns False."""
    if mock_prefs_file.exists():  # Ensure clean state for this check as it asserts no set exists
        mock_prefs_file.unlink()
    assert delete_saved_file_path_set("non_existent_set") is False


def test_rename_saved_file_path_set(mock_prefs_file):
    """Test renaming a saved file path set."""
    if mock_prefs_file.exists():
        mock_prefs_file.unlink()
    old_name = "original_name"
    new_name = "renamed_name"
    file_paths = ["/rename/test.out"]

    assert save_file_path_set(old_name, file_paths) is True
    saved_paths_before_rename = get_saved_file_paths()
    assert old_name in saved_paths_before_rename
    assert new_name not in saved_paths_before_rename

    assert rename_saved_file_path_set(old_name, new_name) is True
    saved_paths_after_rename = get_saved_file_paths()
    assert new_name in saved_paths_after_rename
    assert saved_paths_after_rename[new_name] == file_paths
    assert old_name not in saved_paths_after_rename


def test_rename_non_existent_file_path_set(mock_prefs_file):
    """Test renaming a non-existent file path set returns False."""
    assert rename_saved_file_path_set(
        "non_existent_old", "new_name_fail") is False


# This test uses tmp_path directly for its PREFS_FILE, not mock_prefs_file
def test_save_preferences_handles_io_errors(tmp_path):
    """Test that save_preferences returns False if file cannot be written."""
    # Use a read-only directory for PREFS_FILE to simulate an IO error
    read_only_dir = tmp_path / "read_only_dir"
    read_only_dir.mkdir()
    os.chmod(read_only_dir, 0o555)  # Read and execute only

    bad_prefs_file = read_only_dir / "prefs.json"

    with patch('user_preferences.PREFS_FILE', bad_prefs_file):
        with patch('user_preferences.PREFS_DIR', read_only_dir):
            # Ensure the directory exists (though it's read-only)
            # load_preferences() might fail or return defaults, which is fine for this test setup
            # The main point is to test save_preferences' error handling
            if not bad_prefs_file.exists():  # Create a dummy file if load_preferences doesn't
                try:
                    with open(bad_prefs_file, 'w') as f:
                        json.dump(DEFAULT_PREFERENCES, f)
                except IOError:
                    # This is expected if directory is truly read-only for the
                    # user
                    pass

            prefs_to_save = DEFAULT_PREFERENCES.copy()
            prefs_to_save["new_key"] = "new_value"

            # Temporarily make the file writable for the initial save by load_preferences if it creates it
            # then make it unwritable for the save_preferences call
            if bad_prefs_file.exists():
                os.chmod(bad_prefs_file, 0o666)  # Make writable
                save_preferences(DEFAULT_PREFERENCES)  # Ensure it exists
                os.chmod(bad_prefs_file, 0o444)  # Make read-only

            assert save_preferences(prefs_to_save) is False

    # Cleanup: restore permissions to allow deletion by tmp_path
    os.chmod(read_only_dir, 0o777)
    if bad_prefs_file.exists():
        os.chmod(bad_prefs_file, 0o777)


def test_load_preferences_handles_corrupted_json(mock_prefs_file):
    """Test that load_preferences returns default if JSON is corrupted."""
    with open(mock_prefs_file, 'w') as f:
        f.write("this is not json")

    prefs = load_preferences()
    assert prefs == DEFAULT_PREFERENCES

    # As per current load_preferences implementation, it returns defaults in memory
    # but does NOT overwrite the corrupted file. So, we check if the file still exists
    # and contains the corrupted content.
    assert mock_prefs_file.exists()
    with open(mock_prefs_file, 'r') as f:
        corrupted_content = f.read()
    assert corrupted_content == "this is not json"

    # If the design was to overwrite, the following would be tested instead:
    # with open(mock_prefs_file, 'r') as f:
    #     content = json.load(f) # This would fail if not overwritten
    # assert content == DEFAULT_PREFERENCES


def test_ensure_prefs_dir_called(mock_prefs_file):
    """Test that ensure_prefs_dir is called by load_preferences and save_preferences."""
    # mock_prefs_file itself sets up a temp dir via PREFS_DIR patch
    # We just need to ensure that the directory that PREFS_DIR points to is
    # created.

    # Scenario 1: File and directory don't exist
    if mock_prefs_file.exists():
        mock_prefs_file.unlink()
    if mock_prefs_file.parent.exists():
        # Remove the .openfast_plotter temp sub-directory to test its creation
        # This is a bit tricky as tmp_path is the parent of .openfast_plotter
        os.rmdir(mock_prefs_file.parent)

    assert not mock_prefs_file.parent.exists()
    load_preferences()  # Should call ensure_prefs_dir and create it
    assert mock_prefs_file.parent.exists()
    assert mock_prefs_file.exists()  # And the file itself

    # Scenario 2: Directory exists, file doesn't (covered by
    # test_load_default_preferences_if_file_not_exist)

    # Scenario 3: Saving also ensures directory
    if mock_prefs_file.exists():
        mock_prefs_file.unlink()
    if mock_prefs_file.parent.exists():
        os.rmdir(mock_prefs_file.parent)  # remove .openfast_plotter again

    assert not mock_prefs_file.parent.exists()
    # Should call ensure_prefs_dir
    save_preferences(DEFAULT_PREFERENCES.copy())
    assert mock_prefs_file.parent.exists()
    assert mock_prefs_file.exists()
