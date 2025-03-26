"""
Utility script to download example OpenFAST output files for testing.

This script downloads example .outb files from the OpenFAST r-test repository
to allow users to quickly test the remoteOpenFASTplotter application.
"""

import os
import requests
import argparse
from pathlib import Path
from tqdm import tqdm

# URLs of test files from OpenFAST r-test repository
TEST_FILES = {
    "5MW_Land_BD_DLL_WTurb": "https://github.com/OpenFAST/r-test/raw/main/glue-codes/openfast/5MW_Land_BD_DLL_WTurb/5MW_Land_BD_DLL_WTurb.outb",
    "5MW_Land_DLL_WTurb": "https://github.com/OpenFAST/r-test/raw/main/glue-codes/openfast/5MW_Land_DLL_WTurb/5MW_Land_DLL_WTurb.outb"
}

def download_file(url, destination):
    """
    Download a file from a URL with progress bar
    
    Parameters:
    -----------
    url : str
        URL to download from
    destination : str
        Local path to save the file to
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    # Download with progress bar
    print(f"Downloading {os.path.basename(destination)}...")
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination, 'wb') as f, tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive chunks
                    f.write(chunk)
                    bar.update(len(chunk))
        
        print(f"Downloaded to {destination}")
        return True
    else:
        print(f"Failed to download {url}, status code: {response.status_code}")
        return False

def download_test_files(output_dir=None):
    """
    Download all test files to the specified directory
    
    Parameters:
    -----------
    output_dir : str, optional
        Directory to save files to. Defaults to ./test_files
    
    Returns:
    --------
    dict : Dictionary of {file_name: file_path}
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "test_files")
    
    output_dir = os.path.abspath(output_dir)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    downloaded_files = {}
    
    for name, url in TEST_FILES.items():
        file_name = f"{name}.outb"
        destination = os.path.join(output_dir, file_name)
        
        if download_file(url, destination):
            downloaded_files[name] = destination
    
    print(f"\nAll files downloaded to {output_dir}")
    for name, path in downloaded_files.items():
        print(f"  - {name}: {path}")
    
    return downloaded_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download OpenFAST example files for testing')
    parser.add_argument('--output', '-o', help='Directory to save files to', default=None)
    args = parser.parse_args()
    
    download_test_files(args.output)
    
    print("\nTo use these files with the plotter:")
    print("1. Start the Remote OpenFAST Plotter application")
    print("2. Copy and paste the file paths above into the application")
    print("3. Click 'Load Files' to analyze the test data")
