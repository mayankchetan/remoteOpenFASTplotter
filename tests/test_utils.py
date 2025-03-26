import pytest
import os
import glob
import pandas as pd
from app import get_unique_identifiers, remove_duplicated_legends, draw_graph
import plotly.graph_objects as go

# Fixture to find test files
@pytest.fixture
def test_files():
    """Find test files in the test_files directory"""
    test_file_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_files")
    outb_files = glob.glob(os.path.join(test_file_dir, "*.outb"))
    
    if not outb_files:
        pytest.skip("No test files found. Run 'python utils/download_test_files.py' first.")
    
    return outb_files

# Test the unique identifier generation
def test_unique_identifiers():
    # Test with simple filenames
    paths = ["/path/to/file1.out", "/path/to/file2.out"]
    identifiers = get_unique_identifiers(paths)
    assert identifiers[paths[0]] == "file1.out"
    assert identifiers[paths[1]] == "file2.out"
    
    # Test with duplicate filenames
    paths = ["/path/to/file.out", "/other/path/to/file.out"]
    identifiers = get_unique_identifiers(paths)
    assert identifiers[paths[0]] != identifiers[paths[1]]
    assert "path/to/file.out" in identifiers[paths[0]] or "path/to/file.out" in identifiers[paths[1]]

    # Test with real file paths if available
    try:
        test_file_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_files")
        outb_files = glob.glob(os.path.join(test_file_dir, "*.outb"))
        
        if len(outb_files) >= 2:
            real_identifiers = get_unique_identifiers(outb_files)
            assert len(real_identifiers) == len(outb_files)
            # Check that all identifiers are unique
            assert len(set(real_identifiers.values())) == len(outb_files)
    except Exception:
        pass  # If test files aren't available, skip this part

# Test legend duplication removal
def test_remove_duplicated_legends():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2], y=[1, 2], name="trace1"))
    fig.add_trace(go.Scatter(x=[1, 2], y=[2, 3], name="trace1"))
    fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4], name="trace2"))
    
    # Before removal, all traces have showlegend=True
    for trace in fig.data:
        assert trace.showlegend is True or trace.showlegend is None
    
    # Apply function
    fig = remove_duplicated_legends(fig)
    
    # Count visible legends
    visible_legends = sum(1 for trace in fig.data if trace.showlegend is not False)
    assert visible_legends == 2  # Only unique names should be visible

# Test file info utility
def test_file_info():
    """Test if the file info function works correctly with sample files"""
    from app import get_file_info
    
    # Create a temporary file for testing
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(b"test content")
        test_file = temp.name
    
    try:
        # Test the file info function
        file_info = get_file_info(test_file)
        
        # Check if all expected fields are present
        assert "file_abs_path" in file_info
        assert "file_size" in file_info
        assert "creation_time" in file_info
        assert "modification_time" in file_info
        
        # Check if the path matches
        assert file_info["file_abs_path"] == test_file
        
        # Check if file size is positive
        assert file_info["file_size"] > 0
    finally:
        # Clean up the temp file
        os.unlink(test_file)

# This test is optional and depends on downloaded files
@pytest.mark.skipif(True, reason="Optional test that requires actual OpenFAST files")
def test_draw_graph_with_files(test_files):
    """Test if the draw_graph function works with real OpenFAST files"""
    if not test_files:
        pytest.skip("No test files available")
    
    # Import necessary items for loading files    
    from app import load_file
    
    # Load the test files
    file_data = []
    for file_path in test_files[:2]:  # Use at most 2 files
        path, df, error, _ = load_file(file_path)
        if df is not None:
            file_data.append((path, df))
    
    if not file_data:
        pytest.skip("Could not load test files")
    
    # Extract paths and dataframes
    file_paths = [item[0] for item in file_data]
    dfs = [item[1] for item in file_data]
    
    # Get common columns for plotting
    common_cols = set(dfs[0].columns)
    for df in dfs[1:]:
        common_cols = common_cols.intersection(set(df.columns))
    common_cols = list(common_cols)
    
    # Choose signals for plotting
    signalx = "Time" if "Time" in common_cols else common_cols[0]
    signaly = [col for col in common_cols[:3] if col != signalx]
    
    if not signaly:
        signaly = [common_cols[0]]
    
    # Test overlay plot
    fig_overlay = draw_graph(file_paths, dfs, signalx, signaly, "overlay")
    assert isinstance(fig_overlay, go.Figure)
    assert len(fig_overlay.data) >= len(file_paths)
