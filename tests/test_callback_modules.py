"""
Tests for the modular callback organization
"""

import os
import sys
import unittest
import importlib
from unittest.mock import MagicMock, patch

# Ensure parent directory is in path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from callbacks import register_callbacks


class TestCallbackModules(unittest.TestCase):
    """Test cases for modular callback structure"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_app = MagicMock()
    
    def test_register_callbacks(self):
        """Test if all module callbacks are registered properly"""
        # Create a patch for each register function to track calls
        with patch('callbacks.register_ui_callbacks') as mock_ui, \
             patch('callbacks.register_file_callbacks') as mock_file, \
             patch('callbacks.register_signal_callbacks') as mock_signal, \
             patch('callbacks.register_time_domain_callbacks') as mock_time, \
             patch('callbacks.register_fft_callbacks') as mock_fft, \
             patch('callbacks.register_annotation_callbacks') as mock_anno, \
             patch('callbacks.register_export_callbacks') as mock_export, \
             patch('callbacks.register_path_management_callbacks') as mock_path, \
             patch('callbacks.register_preference_callbacks') as mock_pref:
            
            # Call the main register function
            register_callbacks(self.mock_app)
            
            # Assert each module's register function was called with the app
            mock_ui.assert_called_once_with(self.mock_app)
            mock_file.assert_called_once_with(self.mock_app)
            mock_signal.assert_called_once_with(self.mock_app)
            mock_time.assert_called_once_with(self.mock_app)
            mock_fft.assert_called_once_with(self.mock_app)
            mock_anno.assert_called_once_with(self.mock_app)
            mock_export.assert_called_once_with(self.mock_app)
            mock_path.assert_called_once_with(self.mock_app)
            mock_pref.assert_called_once_with(self.mock_app)
    
    def test_module_imports(self):
        """Test if all callback modules can be imported"""
        callback_modules = [
            'callbacks.ui_callbacks',
            'callbacks.file_callbacks',
            'callbacks.signal_callbacks',
            'callbacks.time_domain_callbacks',
            'callbacks.fft_callbacks',
            'callbacks.annotation_callbacks',
            'callbacks.export_callbacks',
            'callbacks.path_management_callbacks',
            'callbacks.preference_callbacks'
        ]
        
        for module_name in callback_modules:
            try:
                module = importlib.import_module(module_name)
                # Check if the module has the register function
                self.assertTrue(hasattr(module, f"register_{module_name.split('.')[-1]}"))
            except ImportError as e:
                self.fail(f"Failed to import {module_name}: {e}")


if __name__ == "__main__":
    unittest.main()
