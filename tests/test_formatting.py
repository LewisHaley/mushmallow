"""Tests for formatting.py."""

import ast

import pytest

from mushmallow import formatting

# pylint: disable=missing-param-doc,missing-type-doc


class TestFormatMetadata:
    """Tests for `format_metadata`."""

    def test_empty(self):
        """Test empty metadata."""
        metadata = {}
        actual = formatting.format_metadata(metadata)

        expected = ["metadata={},"]
        assert actual == expected

    def test_single_entry(self):
        """Test metadata with a single entry."""
        metadata = {
            "my_field": '"my value"',
        }
        actual = formatting.format_metadata(metadata)

        expected = ["metadata={", '    "my_field": "my value",', "},"]
        assert actual == expected


class TestMaybeWrapLine:
    """Tests for `maybe_wrap_line`."""

    def test_basic(self):
        """Basic case when nothing should be wrapped."""
        actual = formatting.maybe_wrap_line(
            '"my_field"',
            ": ",
            "True",
            "()",
        )

        expected = [
            '"my_field": True,',
        ]
        assert actual == expected

    def test_short_string__like_a_dict(self):
        """Test that a short string isn't wrapped (context: dict)."""
        actual = formatting.maybe_wrap_line(
            '"my_field"',
            ": ",
            '"this is a short string"',
            "()",
        )

        expected = [
            '"my_field": "this is a short string",',
        ]
        assert actual == expected

    def test_short_string__like_a_keyword(self):
        """Test that a short string isn't wrapped (context: keyword)."""
        actual = formatting.maybe_wrap_line(
            "my_field",
            "=",
            '"this is a short string"',
            "()",
        )

        expected = [
            'my_field="this is a short string",',
        ]
        assert actual == expected

    def test_long_string__like_a_dict(self):
        """Test that a long string is wrapped (context: dict)."""
        actual = formatting.maybe_wrap_line(
            '"my_field"',
            ": ",
            '"this is a very long string that needs wrapping"',
            "()",
            width=50,
        )

        expected = [
            '"my_field": (',
            '    "this is a very long string that needs wrapping"',
            "),",
        ]
        assert actual == expected

    def test_long_string__like_a_keyword(self):
        """Test that a long string is wrapped (context: keyword)."""
        actual = formatting.maybe_wrap_line(
            "my_field",
            "=",
            '"this is a very long string that needs wrapping"',
            "()",
            width=50,
        )

        expected = [
            "my_field=(",
            '    "this is a very long string that needs wrapping"',
            "),",
        ]
        assert actual == expected

    def test_very_long_string__like_a_dict(self):
        """Test that a long string is wrapped (context: dict)."""
        actual = formatting.maybe_wrap_line(
            '"my_field"',
            ": ",
            f"\"this is a v{'e'.join('' for _ in range(40))}ry long string "
            f'that needs wrapping"',
            "()",
            width=50,
        )

        expected = [
            '"my_field": (',
            '    "this is a "',
            '    "veeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeery long "',
            '    "string that needs wrapping"',
            "),",
        ]
        assert actual == expected

    def test_very_long_string__like_a_keyword(self):
        """Test that a long string is wrapped (context: keyword)."""
        actual = formatting.maybe_wrap_line(
            "my_field",
            "=",
            f"\"this is a v{'e'.join('' for _ in range(40))}ry long string "
            f'that needs wrapping"',
            "()",
            width=50,
        )

        expected = [
            "my_field=(",
            '    "this is a "',
            '    "veeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeery long "',
            '    "string that needs wrapping"',
            "),",
        ]
        assert actual == expected


class TestFormatArgs:
    """Tests for `format_args`."""

    @pytest.mark.parametrize(
        "input_",
        [
            "my_func()",
            "my_func(var=1, foo=bar)",
        ],
    )
    def test_no_args(self, input_):
        """Test a call with no args."""
        call = ast.parse(input_).body[0].value
        actual = formatting.format_args(call)

        expected = []
        assert actual == expected

    def test_one_arg(self):
        """Test a call with one arg."""
        input_ = "my_func(a)"
        call = ast.parse(input_).body[0].value
        actual = formatting.format_args(call)

        expected = [
            "a,",
        ]
        assert actual == expected

    def test_multiple_args(self):
        """Test a call with multiple args."""
        input_ = "my_func(a, 1, True, another_func())"
        call = ast.parse(input_).body[0].value
        actual = formatting.format_args(call)

        expected = [
            "a,",
            "1,",
            "True,",
            "another_func(),",
        ]
        assert actual == expected

    def test_nested_func_calls(self):
        """Test a call with nested calls."""
        input_ = "my_func(another_func(a, b), foobar(True, [1, 2]))"
        call = ast.parse(input_).body[0].value
        actual = formatting.format_args(call)

        expected = [
            "another_func(a, b),",
            "foobar(True, [1, 2]),",
        ]
        assert actual == expected
