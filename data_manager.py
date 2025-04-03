"""
Data management module for OpenFAST Plotter
Contains functions for loading and managing OpenFAST output files
"""

import os
import time
import concurrent.futures
from openfast_io.FAST_output_reader import FASTOutputFile

# Global variable to store DataFrames in Python memory
# This avoids JSON serialization/deserialization overhead
DATAFRAMES = {}

def load_file(file_path):
    """
    Load a single OpenFAST file
    
    Parameters:
    -----------
    file_path : str
        Path to OpenFAST output file
        
    Returns:
    --------
    tuple : (file_path, dataframe or None, error_message or None, elapsed_time)
    """
    try:
        start_time = time.time()
        tempObj = FASTOutputFile(file_path)
        df = tempObj.toDataFrame()
        elapsed = time.time() - start_time
        return (file_path, df, None, elapsed)
    except Exception as e:
        return (file_path, None, str(e), 0)

def store_dataframes(file_paths, max_workers=None):
    """
    Read OpenFAST output files and store them as dataframes using parallel processing
    
    Parameters:
    -----------
    file_paths : list of str
        List of paths to OpenFAST output files
    max_workers : int, optional
        Maximum number of worker threads
        
    Returns:
    --------
    tuple : (Dictionary of dataframes {file_path: dataframe}, list of failed files, dict of load times)
    """
    dfs = {}
    failed = []
    times = {}
    
    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all file loading tasks
        future_to_file = {executor.submit(load_file, file): file for file in file_paths}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            file_path, df, error, elapsed = future.result()
            if df is not None:
                dfs[file_path] = df
                times[file_path] = elapsed
            else:
                failed.append((file_path, error))
    
    return dfs, failed, times

def get_file_info(file_path):
    """
    Get file information such as size, creation time, and modification time.
    
    Parameters:
    -----------
    file_path : str
        Path to file
        
    Returns:
    --------
    dict : Dictionary of file information
    """
    try:
        file_stats = os.stat(file_path)
        file_info = {
            'file_abs_path': file_path,
            'file_size': file_stats.st_size / (1024 * 1024),  # Store in MB without rounding initially
            'creation_time': file_stats.st_ctime,
            'modification_time': file_stats.st_mtime
        }
        return file_info
    except Exception as e:
        print(f"Error getting file info for {file_path}: {e}")
        return {
            'file_abs_path': file_path,
            'file_size': 0,
            'creation_time': 0,
            'modification_time': 0
        }
