"""
FFT Analysis tools for Remote OpenFAST Plotter
Based on scipy's spectral analysis capabilities
"""

import numpy as np
import pandas as pd 
from scipy import signal
import scipy.fft as fft

class FFTResult:
    """Class to store FFT computation results and parameters"""
    def __init__(self, freq, amplitude, df, fmax, info=None):
        self.freq = freq
        self.amplitude = amplitude
        self.df = df
        self.fmax = fmax
        self.info = info or {}

def perform_fft(t, y, detrend=False):
    """
    Simple FFT calculation (no windowing or averaging)
    
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
    FFTResult object containing frequency and amplitude arrays
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
    
    # Calculate amplitude (normalized)
    amplitude = np.abs(yf) * 2.0 / n
    
    # Create result object
    result = FFTResult(
        freq=freq,
        amplitude=amplitude,
        df=freq[1] - freq[0] if len(freq) > 1 else 0,
        fmax=freq[-1] if len(freq) > 0 else 0
    )
    
    return result

def perform_welch(t, y, nperseg=None, window='hamming', detrend=False, scaling='density'):
    """
    Welch's method for spectral density estimation
    
    Parameters:
    -----------
    t : array_like
        Time values
    y : array_like
        Signal values
    nperseg : int, optional
        Length of each segment
    window : str
        Window function to use (hamming, hann, boxcar)
    detrend : bool
        Whether to remove linear trend from signal
    scaling : str
        'density' or 'spectrum' scaling
    
    Returns:
    --------
    FFTResult object containing frequency and PSD/amplitude arrays
    """
    # Ensure inputs are numpy arrays
    t = np.asarray(t)
    y = np.asarray(y)
    
    # Calculate sampling frequency
    dt = np.median(np.diff(t))
    fs = 1.0 / dt
    
    # Determine segment size if not specified
    if nperseg is None:
        nperseg = min(256, len(y))
    
    # Get array form of window
    if window == 'hamming':
        win = signal.windows.hamming(nperseg)
    elif window == 'hann':
        win = signal.windows.hann(nperseg)
    elif window == 'rectangular':
        win = signal.windows.boxcar(nperseg)
    else:
        win = signal.get_window(window, nperseg)
    
    # Compute Welch's periodogram
    freq, pxx = signal.welch(y, fs=fs, window=win, nperseg=nperseg,
                            detrend='linear' if detrend else False,
                            scaling=scaling)
    
    # Convert to amplitude for 'density' scaling
    if scaling == 'density':
        amplitude = np.sqrt(pxx)
    else:
        amplitude = pxx
    
    # Create result object
    result = FFTResult(
        freq=freq,
        amplitude=amplitude,
        df=freq[1] - freq[0] if len(freq) > 1 else 0,
        fmax=freq[-1] if len(freq) > 0 else 0,
        info={'nperseg': nperseg, 'window': window}
    )
    
    return result

def perform_binning(freq, psd, bins_per_decade=10):
    """
    Perform logarithmic binning of frequency data
    
    Parameters:
    -----------
    freq : array_like
        Frequency values
    psd : array_like
        Power spectral density values
    bins_per_decade : int
        Number of bins per decade
    
    Returns:
    --------
    tuple of (binned_freq, binned_psd)
    """
    # Ensure inputs are numpy arrays
    freq = np.asarray(freq)
    psd = np.asarray(psd)
    
    # Handle empty arrays
    if len(freq) == 0 or len(psd) == 0:
        return np.array([]), np.array([])
    
    # Skip zero frequency if present
    if freq[0] == 0:
        f0 = freq[0]
        p0 = psd[0]
        freq = freq[1:]
        psd = psd[1:]
    else:
        f0 = None
    
    # Safeguard against empty arrays after removing zero
    if len(freq) == 0:
        return np.array([]), np.array([])
    
    # Create logarithmic bins
    log_f_min = np.log10(np.min(freq))
    log_f_max = np.log10(np.max(freq))
    num_decades = log_f_max - log_f_min
    num_bins = int(np.ceil(num_decades * bins_per_decade))
    
    # Ensure at least one bin
    if num_bins < 1:
        num_bins = 1
    
    log_bins = np.linspace(log_f_min, log_f_max, num_bins + 1)
    bin_centers = 0.5 * (log_bins[1:] + log_bins[:-1])
    
    # Convert to linear frequency
    bin_edges = 10**log_bins
    binned_freq = 10**bin_centers
    
    # Bin the PSD values
    binned_psd = np.zeros_like(binned_freq)
    bin_counts = np.zeros_like(binned_freq)
    
    for i, (left, right) in enumerate(zip(bin_edges[:-1], bin_edges[1:])):
        mask = (freq >= left) & (freq < right)
        if np.any(mask):
            binned_psd[i] = np.mean(psd[mask])
            bin_counts[i] = np.sum(mask)
    
    # Add zero frequency back if it was present
    if f0 is not None:
        binned_freq = np.concatenate(([f0], binned_freq))
        binned_psd = np.concatenate(([p0], binned_psd))
        # Also extend the bin_counts array to match
        bin_counts = np.concatenate(([1], bin_counts))
    
    # Remove empty bins
    valid = bin_counts > 0
    binned_freq = binned_freq[valid]
    binned_psd = binned_psd[valid]
    
    return binned_freq, binned_psd

def compute_fft(df, signal, time_col="Time", start_time=None, end_time=None,
               averaging="None", windowing="hamming", detrend=False,
               n_exp=None, bins_per_decade=10):
    """
    Compute FFT of a signal in a DataFrame
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing the signal data
    signal : str
        Name of the signal column to analyze
    time_col : str
        Name of the time column
    start_time, end_time : float, optional
        Start and end times for analysis window
    averaging : str
        "None", "Welch", or "Binning"
    windowing : str
        "hamming", "hann", or "rectangular"
    detrend : bool
        Whether to remove linear trend from signal
    n_exp : int or None
        Exponent for 2^n points in FFT calculation
    bins_per_decade : int
        For binning averaging, number of bins per decade
    
    Returns:
    --------
    FFTResult object with frequency and amplitude data
    """
    # Filter by time range if specified
    if start_time is not None or end_time is not None:
        mask = pd.Series(True, index=df.index)
        if start_time is not None:
            mask = mask & (df[time_col] >= start_time)
        if end_time is not None:
            mask = mask & (df[time_col] <= end_time)
        data = df[mask]
    else:
        data = df
    
    # Extract time and signal data
    t = data[time_col].values
    y = data[signal].values
    
    # Remove NaN values if any
    valid = ~np.isnan(y) & ~np.isnan(t)
    t = t[valid]
    y = y[valid]
    
    if len(t) < 2:
        raise ValueError("Not enough valid data points for FFT analysis")
    
    # If n_exp is specified, use 2^n points
    if n_exp is not None:
        n_points = min(2**n_exp, len(y))
        t = t[:n_points]
        y = y[:n_points]
    
    # Choose FFT method based on averaging parameter
    if averaging.lower() == "none":
        result = perform_fft(t, y, detrend=detrend)
    elif averaging.lower() == "welch":
        nperseg = min(2**(n_exp or 8), len(y)//2)
        result = perform_welch(t, y, nperseg=nperseg, window=windowing, detrend=detrend)
    elif averaging.lower() == "binning":
        # First compute standard FFT
        fft_result = perform_fft(t, y, detrend=detrend)
        # Then apply logarithmic binning
        binned_freq, binned_amp = perform_binning(
            fft_result.freq, fft_result.amplitude**2, bins_per_decade)
        # Convert back to amplitude
        result = FFTResult(
            freq=binned_freq,
            amplitude=np.sqrt(binned_amp),
            df=np.nan,  # Not applicable for irregular bins
            fmax=binned_freq[-1],
            info={'binning': bins_per_decade}
        )
    else:
        raise ValueError(f"Unknown averaging method: {averaging}")
    
    # Add extra info
    result.info.update({
        'signal': signal,
        'windowing': windowing,
        'detrend': detrend,
        'n_points': len(y),
        'averaging': averaging,
        'dt': np.median(np.diff(t)),
        'fs': 1.0 / np.median(np.diff(t))
    })
    
    return result
