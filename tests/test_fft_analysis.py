"""
Tests for the FFT analysis module
"""
import os
import sys
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

# Try to import FFT module
try:
    from tools.fft_analysis import compute_fft, perform_fft, perform_welch, perform_binning, FFTResult
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from tools.fft_analysis import compute_fft, perform_fft, perform_welch, perform_binning, FFTResult
    except ImportError:
        pytest.skip("FFT analysis module not available")

class TestFFTAnalysis:
    """Test suite for FFT analysis tools"""
    
    @pytest.fixture
    def sine_wave_df(self):
        """Create a test DataFrame with a sine wave signal"""
        fs = 1000  # Hz
        T = 1.0    # seconds
        t = np.linspace(0, T, int(T * fs), endpoint=False)
        
        # Create a signal with multiple frequency components
        f1, f2, f3 = 10.0, 50.0, 120.0  # Hz
        signal = (
            np.sin(2 * np.pi * f1 * t) +      # 10 Hz component
            0.5 * np.sin(2 * np.pi * f2 * t) + # 50 Hz component
            0.2 * np.sin(2 * np.pi * f3 * t)   # 120 Hz component
        )
        
        return pd.DataFrame({"Time": t, "Signal": signal})
    
    def test_fft_result_class(self):
        """Test the FFTResult class"""
        # Create a sample FFTResult
        freq = np.array([0, 1, 2])
        amplitude = np.array([0, 1, 0])
        result = FFTResult(freq, amplitude, 1.0, 2.0, {"key": "value"})
        
        # Check attributes
        assert np.array_equal(result.freq, freq)
        assert np.array_equal(result.amplitude, amplitude)
        assert result.df == 1.0
        assert result.fmax == 2.0
        assert result.info == {"key": "value"}
    
    def test_perform_fft(self, sine_wave_df):
        """Test the perform_fft function"""
        df = sine_wave_df
        t = df["Time"].values
        y = df["Signal"].values
        
        # Run FFT
        result = perform_fft(t, y, detrend=False)
        
        # Check that result is a FFTResult
        assert isinstance(result, FFTResult)
        
        # Check frequency resolution
        dt = t[1] - t[0]
        expected_df = 1.0 / (len(t) * dt)
        assert np.isclose(result.df, expected_df, rtol=1e-10)
        
        # Check that the peaks are at the expected frequencies
        peaks = []
        for i in range(1, len(result.freq) - 1):
            if (result.amplitude[i] > result.amplitude[i-1] and 
                result.amplitude[i] > result.amplitude[i+1] and
                result.amplitude[i] > 0.1):  # Threshold to ignore noise
                peaks.append(result.freq[i])
        
        # We should find peaks close to our input frequencies
        assert any(np.isclose(p, 10.0, atol=2.0) for p in peaks), f"No peak found near 10 Hz, peaks: {peaks}"
        assert any(np.isclose(p, 50.0, atol=2.0) for p in peaks), f"No peak found near 50 Hz, peaks: {peaks}"
        assert any(np.isclose(p, 120.0, atol=2.0) for p in peaks), f"No peak found near 120 Hz, peaks: {peaks}"
    
    def test_perform_welch(self, sine_wave_df):
        """Test the perform_welch function"""
        df = sine_wave_df
        t = df["Time"].values
        y = df["Signal"].values
        
        # Run Welch method
        result = perform_welch(t, y, nperseg=256, window='hamming', detrend=False)
        
        # Check result type
        assert isinstance(result, FFTResult)
        
        # Check that main peaks are still visible
        # Note: Welch method smooths the spectrum, so peaks might be less pronounced
        peaks = []
        for i in range(1, len(result.freq) - 1):
            if (result.amplitude[i] > result.amplitude[i-1] and 
                result.amplitude[i] > result.amplitude[i+1] and
                result.amplitude[i] > 0.05):  # Lower threshold for Welch
                peaks.append(result.freq[i])
        
        # We should still identify the main frequency components
        assert any(np.isclose(p, 10.0, atol=5.0) for p in peaks), f"No peak found near 10 Hz in Welch, peaks: {peaks}"
        assert any(np.isclose(p, 50.0, atol=5.0) for p in peaks), f"No peak found near 50 Hz in Welch, peaks: {peaks}"
    
    def test_compute_fft_with_time_range(self, sine_wave_df):
        """Test compute_fft with time range filtering"""
        df = sine_wave_df
        
        # Run FFT with the full range
        result_full = compute_fft(df, "Signal", time_col="Time")
        
        # Run FFT with a limited time range
        result_limited = compute_fft(df, "Signal", time_col="Time", 
                                    start_time=0.2, end_time=0.8)
        
        # Check that results are different
        assert len(result_limited.freq) <= len(result_full.freq)
        
        # But still contain the expected frequency peaks
        peaks_limited = []
        for i in range(1, len(result_limited.freq) - 1):
            if (result_limited.amplitude[i] > result_limited.amplitude[i-1] and 
                result_limited.amplitude[i] > result_limited.amplitude[i+1] and
                result_limited.amplitude[i] > 0.1):
                peaks_limited.append(result_limited.freq[i])
        
        # Should still find the main frequency components
        assert any(np.isclose(p, 10.0, atol=2.0) for p in peaks_limited)
    
    def test_compute_fft_with_all_averaging_methods(self, sine_wave_df):
        """Test compute_fft with different averaging methods"""
        df = sine_wave_df
        
        # Test with all averaging methods
        result_none = compute_fft(df, "Signal", averaging="None")
        result_welch = compute_fft(df, "Signal", averaging="Welch")
        result_binning = compute_fft(df, "Signal", averaging="Binning")
        
        # Check that they all produced results
        assert isinstance(result_none, FFTResult)
        assert isinstance(result_welch, FFTResult)
        assert isinstance(result_binning, FFTResult)
        
        # Verify that the primary peaks are still identifiable in all methods
        def has_peak_near(result, target_freq, tolerance=5.0):
            for i in range(1, len(result.freq) - 1):
                if (np.isclose(result.freq[i], target_freq, atol=tolerance) and
                    result.amplitude[i] > 0.05):
                    return True
            return False
        
        assert has_peak_near(result_none, 10.0)
        assert has_peak_near(result_welch, 10.0)
        
        # Binning is more approximate due to logarithmic bins
        if len(result_binning.freq) > 5:  # Skip if too few bins
            assert has_peak_near(result_binning, 10.0, tolerance=10.0)
