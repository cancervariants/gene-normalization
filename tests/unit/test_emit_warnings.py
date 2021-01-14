"""Test the emit_warnings function."""
from gene.query import Normalizer


def test_emit_warnings():
    """Test that emit_warnings works correctly."""
    expected_warnings = ['Query contains non-breaking space characters.']
    normalizer = Normalizer()

    # Test emit no warnings
    actual_warnings = normalizer.emit_warnings('spry3')
    assert actual_warnings == []

    # Test emit warnings
    actual_warnings = normalizer.emit_warnings('sp ry3')
    assert actual_warnings == actual_warnings

    actual_warnings = normalizer.emit_warnings('sp\u00A0ry3')
    assert expected_warnings == actual_warnings

    actual_warnings = normalizer.emit_warnings('sp&nbsp;ry3')
    assert expected_warnings == actual_warnings

    actual_warnings = normalizer.emit_warnings('sp\xa0ry3')
    assert expected_warnings == actual_warnings
