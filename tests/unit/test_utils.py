"""Unit tests for utility functions in toolfront.utils."""

import pandas as pd

from toolfront.utils import deserialize_response, sanitize_url, serialize_response


class TestSerializeResponse:
    """Test cases for serialize_response function."""

    def test_serialize_dataframe_under_limit(self):
        """Test DataFrame serialization when under row limit."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        result = serialize_response(df)
        assert isinstance(result, str)
        assert "a,b" in result
        assert "1,4" in result
        assert "3,6" in result

    def test_serialize_dataframe_over_limit(self):
        """Test DataFrame truncation when over row limit."""
        # Create DataFrame with more than MAX_DATA_ROWS (1000) rows
        df = pd.DataFrame({"a": range(1500), "b": range(1500, 3000)})
        result = serialize_response(df)
        assert isinstance(result, dict)
        assert "data" in result
        assert "truncation_message" in result
        assert "Showing 100 rows of 1,500 total rows" in result["truncation_message"]

    def test_serialize_simple_types(self):
        """Test serialization of simple types."""
        assert serialize_response("hello") == "hello"
        assert serialize_response(42) == 42
        assert serialize_response(3.14) == 3.14
        assert serialize_response(True) is True
        assert serialize_response(None) is None

    def test_serialize_collections(self):
        """Test serialization of collections."""
        assert serialize_response([1, 2, 3]) == [1, 2, 3]
        assert serialize_response({"a": 1, "b": 2}) == {"a": 1, "b": 2}
        assert serialize_response({1, 2, 3}) == [1, 2, 3]  # Sets serialize to lists

    def test_serialize_large_string(self):
        """Test truncation of large JSON strings."""
        # Create a large object that serializes to > MAX_DATA_CHARS (50000)
        large_list = ["x" * 1000 for _ in range(100)]
        result = serialize_response(large_list)
        assert isinstance(result, dict)
        assert "data" in result
        assert "truncation_message" in result
        assert result["data"].endswith("...")
        assert len(result["data"]) < 50000

    def test_serialize_nested_objects(self):
        """Test serialization of nested objects."""
        nested = {"level1": {"level2": {"data": [1, 2, 3], "name": "test"}}}
        result = serialize_response(nested)
        assert result == nested


class TestDeserializeResponse:
    """Test cases for deserialize_response function."""

    def test_deserialize_empty_dict(self):
        """Test deserialization of empty dict."""
        result = deserialize_response({})
        assert result == "```json\n{}\n```"

    def test_deserialize_dict(self):
        """Test deserialization of dictionary."""
        data = {"key1": "value1", "key2": [1, 2, 3]}
        result = deserialize_response(data)
        assert "**key1:**" in result
        assert "value1" in result
        assert "**key2:**" in result
        # Check that all list elements are present (pretty-printed JSON)
        assert "1" in result and "2" in result and "3" in result

    def test_deserialize_csv_string(self):
        """Test deserialization of CSV string."""
        csv_data = "a,b,c\n1,2,3\n4,5,6"
        result = deserialize_response(csv_data)
        assert "|" in result  # Markdown table format
        assert "a" in result and "b" in result and "c" in result

    def test_deserialize_list(self):
        """Test deserialization of lists."""
        short_list = [1, 2, 3]
        result = deserialize_response(short_list)
        assert "```json" in result
        # Check that all elements are present
        assert "1" in result and "2" in result and "3" in result

        long_list = list(range(20))
        result = deserialize_response(long_list)
        assert "(showing first 10 of 20 items)" in result
        assert "..." in result


class TestSanitizeUrl:
    """Test cases for sanitize_url function."""

    def test_sanitize_url_with_password(self):
        """Test password removal from URLs."""
        url = "postgresql://user:password@localhost:5432/db"
        result = sanitize_url(url)
        assert result == "postgresql://user:***@localhost:5432/db"

    def test_sanitize_url_without_password(self):
        """Test URLs without passwords remain unchanged."""
        url = "postgresql://user@localhost:5432/db"
        result = sanitize_url(url)
        assert result == url

    def test_sanitize_url_no_auth(self):
        """Test URLs without authentication."""
        url = "postgresql://localhost:5432/db"
        result = sanitize_url(url)
        assert result == url

    def test_sanitize_file_url(self):
        """Test file URLs."""
        url = "file:///path/to/file.db"
        result = sanitize_url(url)
        assert result == url

    def test_sanitize_http_url_with_password(self):
        """Test HTTP URLs with authentication."""
        url = "https://user:secret@api.example.com/v1"
        result = sanitize_url(url)
        assert result == "https://user:***@api.example.com/v1"
