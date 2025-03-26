"""
Simple test file that doesn't depend on importing the app module.
This is useful for verifying that the test setup works correctly.
"""

def test_minimal():
    """A minimal test that always passes"""
    assert True

def test_math():
    """Test basic math operations"""
    assert 2 + 2 == 4
    assert 10 - 5 == 5
    assert 3 * 4 == 12
    assert 10 / 2 == 5
