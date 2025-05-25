import pytest
from tools.signal_selection import get_signals


def test_get_signals_empty_list():
    """Test get_signals with an empty list."""
    assert get_signals([]) == [], "Expected no signals when input is empty"


def test_get_signals_valid_names():
    """Test get_signals with a list of valid signal names."""
    valid_signals = ["WindSpeed", "RotorSpeed", "GeneratorSpeed"]
    # Current get_signals just returns the list if it passes basic validation
    assert get_signals(valid_signals) == valid_signals


def test_get_signals_with_spaces_and_special_chars():
    """Test get_signals with names containing spaces and special characters."""
    signals_with_patterns = [
        "Signal With Spaces",
        "Signal@Special#Chars",
        "NormalSignal123"]
    # Current get_signals should allow these as they are strings and not
    # "InvalidSignal"
    assert get_signals(signals_with_patterns) == signals_with_patterns


def test_get_signals_all_invalid_names_trigger_error():
    """Test get_signals with only 'InvalidSignal' names, expecting a ValueError."""
    with pytest.raises(ValueError, match="Invalid signal names provided"):
        get_signals(["InvalidSignal"])

    # Test with multiple "InvalidSignal" entries
    with pytest.raises(ValueError, match="Invalid signal names provided"):
        get_signals(["InvalidSignal", "InvalidSignal"])


def test_get_signals_mixed_valid_and_invalid_names_trigger_error():
    """
    Test get_signals with a mix of valid signal names and 'InvalidSignal'.
    The current function is expected to raise an error if any signal is "InvalidSignal".
    """
    mixed_signals = ["WindSpeed", "InvalidSignal", "RotorSpeed"]
    with pytest.raises(ValueError, match="Invalid signal names provided"):
        get_signals(mixed_signals)


def test_get_signals_non_string_name_triggers_error():
    """Test get_signals with a non-string element in the list."""
    non_string_signals = ["WindSpeed", 123, "RotorSpeed"]
    with pytest.raises(ValueError, match="Invalid signal names provided"):
        get_signals(non_string_signals)


def test_get_signals_list_with_none_triggers_error():
    """Test get_signals with a list containing None."""
    signals_with_none = ["WindSpeed", None, "RotorSpeed"]
    with pytest.raises(ValueError, match="Invalid signal names provided"):
        get_signals(signals_with_none)

# The following tests would be relevant if get_signals was designed to filter
# from a list of available signals (e.g., DataFrame columns).
# For now, they are commented out as the function's scope is different.

# def test_get_signals_filters_non_existing(sample_df_columns):
#     """Test that get_signals filters out names not in the provided available_signals."""
#     requested_signals = ["WindSpeed", "NonExistingSignal", "RotorSpeed"]
#     expected_signals = ["WindSpeed", "RotorSpeed"]
#     # This would require get_signals to accept an 'available_signals' argument
#     # assert get_signals(requested_signals, available_signals=sample_df_columns) == expected_signals

# def test_get_signals_case_sensitivity(sample_df_columns):
#     """Test case sensitivity if that's a feature of signal selection."""
#     requested_signals = ["windspeed", "RotorSpeed"] # Assuming "windspeed" is wrong case
#     # Depending on implementation (case-sensitive or -insensitive matching)
#     # expected_signals_sensitive = ["RotorSpeed"]
#     # expected_signals_insensitive = ["WindSpeed", "RotorSpeed"]
#     # assert get_signals(requested_signals, available_signals=sample_df_columns) == expected_signals_sensitive
#     pass # Placeholder for now
