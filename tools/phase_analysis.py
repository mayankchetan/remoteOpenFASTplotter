"""
Phase and Magnitude Analysis tools for Remote OpenFAST Plotter
Similar to FFT module but with phase information and peak selection
"""

import numpy as np
import pandas as pd
from scipy import signal
import scipy.fft as fft

class PhaseFFTResult:
    """Class to store FFT computation results with phase information"""
    def __init__(self, freq, magnitude, phase, df, fmax, info=None):
        self.freq = freq
        self.magnitude = magnitude
        self.phase = phase
        self.df = df
        self.fmax = fmax
        self.info = info or {}

def perform_phase_fft(t, y, detrend=False):
    """
    FFT calculation that returns both magnitude and phase
    
    Parameters:
    -----------
    t : array_like
        Time values
    y : array_like
        Signal values
    detrend : bool
        Whether to remove linear trend from signal
    
    Returns:
    --------
    PhaseFFTResult object containing frequency, magnitude, and phase arrays
    """
    # Ensure inputs are numpy arrays
    t = np.asarray(t)
    y = np.asarray(y)
    
    # Calculate sampling frequency and time step
    dt = np.median(np.diff(t))
    fs = 1.0 / dt
    
    # Apply detrending if requested
    if detrend:
        y = signal.detrend(y)
    
    # Perform FFT
    n = len(y)
    yf = fft.rfft(y)
    freq = fft.rfftfreq(n, dt)
    
    # Calculate magnitude (normalized)
    magnitude = np.abs(yf) * 2.0 / n
    
    # Calculate phase and unwrap it
    phase = np.unwrap(np.angle(yf))
    
    # Create result object
    result = PhaseFFTResult(
        freq=freq,
        magnitude=magnitude,
        phase=phase,
        df=freq[1] - freq[0] if len(freq) > 1 else 0,
        fmax=freq[-1] if len(freq) > 0 else 0
    )
    
    return result

def compute_phase_fft(data, signal_col, time_col="Time", start_time=None, end_time=None, n_exp=None, detrend=False):
    """
    Compute FFT with phase information for a given signal.
    
    Parameters:
    -----------
    data : DataFrame
        Input DataFrame with time and signal columns
    signal_col : str
        Name of the signal column
    time_col : str
        Name of the time column
    start_time, end_time : float, optional
        Time range for analysis
    n_exp : int, optional
        If provided, use 2^n_exp points for FFT
    detrend : bool
        Whether to remove linear trend from signal
    
    Returns:
    --------
    PhaseFFTResult object with frequency, magnitude, and phase
    """
    # Check if the DataFrame is empty
    if data.empty:
        raise ValueError("Input DataFrame is empty")

    # Check if the required columns exist
    missing_columns = [col for col in [time_col, signal_col] if col not in data.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {', '.join(missing_columns)}")
        
    # Check if data is numeric
    if not np.issubdtype(data[time_col].dtype, np.number) or not np.issubdtype(data[signal_col].dtype, np.number):
        raise TypeError("Non-numeric data found in columns")

    # Filter by time range if specified
    if start_time is not None or end_time is not None:
        mask = pd.Series(True, index=data.index)
        if start_time is not None:
            mask = mask & (data[time_col] >= start_time)
        if end_time is not None:
            mask = mask & (data[time_col] <= end_time)
        data = data[mask]
    
    # Extract time and signal data
    t = data[time_col].values
    y = data[signal_col].values
    
    # Remove NaN values if any
    valid = ~np.isnan(y) & ~np.isnan(t)
    t = t[valid]
    y = y[valid]
    
    if len(t) < 2:
        raise ValueError("Not enough valid data points for phase FFT analysis")
    
    # If n_exp is specified, use 2^n points
    if n_exp is not None:
        n_points = min(2**n_exp, len(y))
        t = t[:n_points]
        y = y[:n_points]
    
    # Perform FFT with phase information
    result = perform_phase_fft(t, y, detrend=detrend)
    
    # Add extra info
    result.info.update({
        'signal': signal_col,
        'detrend': detrend,
        'n_points': len(y),
        'dt': np.median(np.diff(t)),
        'fs': 1.0 / np.median(np.diff(t))
    })
    
    return result

def find_peaks(freq, magnitude, prominence=0.1, width=None, height=None, threshold=None):
    """
    Find peaks in the magnitude spectrum
    
    Parameters:
    -----------
    freq : array_like
        Frequency values
    magnitude : array_like
        Magnitude values
    prominence, width, height, threshold : 
        Parameters for scipy.signal.find_peaks
    
    Returns:
    --------
    dict with peak indices, frequencies, magnitudes, and properties
    """
    # Ensure valid inputs
    if len(freq) != len(magnitude):
        raise ValueError("Frequency and magnitude arrays must have the same length")
    
    if len(freq) == 0:
        return {
            'indices': np.array([]),
            'frequencies': np.array([]),
            'magnitudes': np.array([]),
            'properties': {}
        }
    
    # Find peaks
    peaks, properties = signal.find_peaks(
        magnitude, 
        prominence=prominence, 
        width=width, 
        height=height,
        threshold=threshold
    )
    
    # Extract peak information
    peak_freqs = freq[peaks]
    peak_mags = magnitude[peaks]
    
    return {
        'indices': peaks,
        'frequencies': peak_freqs,
        'magnitudes': peak_mags,
        'properties': properties
    }