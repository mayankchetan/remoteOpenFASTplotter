"""
Script to regenerate a favicon for the OpenFAST Plotter application.
This script takes an input image and resizes it to create a favicon.ico file.
"""

import os
from PIL import Image

def regenerate_favicon(input_image_path, output_favicon_path):
    """
    Regenerate a favicon from an input image.
    
    Parameters:
    -----------
    input_image_path : str
        Path to the input image file (e.g., PNG or JPEG).
    output_favicon_path : str
        Path to save the output favicon.ico file.
    """
    # Open the input image
    img = Image.open(input_image_path)
    
    # Ensure the image has an alpha channel (RGBA)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    # Resize the image to standard favicon sizes
    favicon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    img.save(output_favicon_path, format="ICO", sizes=favicon_sizes)
    
    print(f"Favicon regenerated and saved at {output_favicon_path}")

if __name__ == "__main__":
    # Path to the input image (replace with the path to your provided image)
    input_image = os.path.join(os.path.dirname(__file__), "wind_turbine_plot.png")
    
    # Path to save the output favicon
    output_favicon = os.path.join(os.path.dirname(__file__), "favicon.ico")
    
    # Regenerate the favicon
    regenerate_favicon(input_image, output_favicon)
