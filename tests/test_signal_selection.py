import pytest
from tools.signal_selection import get_signals

def test_signal_selection_edge_cases():
    """Test signal selection with edge cases."""
    # No signals available
    signals = get_signals([])
    assert signals == [], "Expected no signals when input is empty"

    # Invalid signal names
    with pytest.raises(ValueError, match="Invalid signal names provided"):
        get_signals(["InvalidSignal"])
