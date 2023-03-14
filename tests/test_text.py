"""Tests for text.py."""

import pytest

import mushmallow.text


class TestWrapText:
    """Tests for `wrap_text`."""

    def test_one_short_line(self):
        """Test a short line that doesn't need wrapping."""
        text = "this is short"
        actual = mushmallow.text.wrap_text(text)

        expected = ['"this is short"']
        assert actual == expected

    def test_one_long_line(self):
        """Test a long line that needs wrapping."""
        text = "aaaaa " * 20  # 120 character string
        actual = mushmallow.text.wrap_text(text, width=60)

        expected = [
            '"aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa "',
            '"aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa"',
        ]
        assert actual == expected

    def test_one_long_line__short_width(self):
        """Test a long line that needs a lot of wrapping."""
        text = "aaaaa " * 20  # 120 character string
        actual = mushmallow.text.wrap_text(text, width=50)

        expected = [
            '"aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa "',
            '"aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa aaaaa "',
            '"aaaaa aaaaa aaaaa aaaaa"',
        ]
        assert actual == expected


class TestIndent:
    """Tests for `indent`."""

    def test_one_line(self):
        """Test indenting a single line."""
        lines = ["this is a line"]
        actual = mushmallow.text.indent(lines)

        expected = ["    this is a line"]
        assert actual == expected

    def test_multiple_lines(self):
        """Test indenting multiple lines."""
        lines = [
            "line one",
            "line two",
            "line three",
        ]
        actual = mushmallow.text.indent(lines)

        expected = [
            "    line one",
            "    line two",
            "    line three",
        ]
        assert actual == expected

    def test_multiple_indents(self):
        """Test more than one indent."""
        lines = [
            "line one",
            "line two",
        ]
        actual = mushmallow.text.indent(lines, number=3)

        expected = [
            "            line one",
            "            line two",
        ]
        assert actual == expected


class TestFormatBuiltin:
    """Tests for `format_builtin`."""

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("a string", '"a string"'),
            ('"a quoted string"', '""a quoted string""'),
        ],
    )
    def test_input_is_str(self, input_, expected):
        """Test a string input."""
        actual = mushmallow.text.format_builtin(input_)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            (1, "1"),
            ([], "[]"),
            ([1, 2, 3], "[1, 2, 3]"),
            ({}, "{}"),
            ({"a": 1}, "{'a': 1}"),
        ],
    )
    def test_input_is_anything_else(self, input_, expected):
        """Test input is anything but a string."""
        actual = mushmallow.text.format_builtin(input_)
        assert actual == expected
