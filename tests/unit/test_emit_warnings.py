"""Test the emit_warnings function."""
from gene.database import create_db
from gene.query import QueryHandler


def test_emit_warnings():
    """Test that emit_warnings works correctly."""
    expected_warnings = [
        {
            "non_breaking_space_characters": "Query contains non-breaking space characters"
        }
    ]
    db = create_db()
    query_handler = QueryHandler(db)

    # Test emit no warnings
    actual_warnings = query_handler._parse_query_input("spry3")
    assert actual_warnings == []

    # Test emit warnings
    actual_warnings = query_handler._parse_query_input("sp ry3")
    assert actual_warnings == actual_warnings

    actual_warnings = query_handler._parse_query_input("sp\u00A0ry3")
    assert expected_warnings == actual_warnings

    actual_warnings = query_handler._parse_query_input("sp&nbsp;ry3")
    assert expected_warnings == actual_warnings

    actual_warnings = query_handler._parse_query_input("sp\xa0ry3")
    assert expected_warnings == actual_warnings
