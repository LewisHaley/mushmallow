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


class TestFormatKwargs:
    """Tests for `format_kwargs`."""

    @pytest.mark.parametrize(
        "input_",
        [
            "my_func()",
            "my_func(1, bar)",
        ],
    )
    def test_no_kwargs(self, input_):
        """Test a call with no kwargs."""
        call = ast.parse(input_).body[0].value
        actual = formatting.format_kwargs(call)

        expected = []
        assert actual == expected

    def test_one_kwarg(self):
        """Test a call with one kwarg."""
        input_ = "my_func(a=1)"
        call = ast.parse(input_).body[0].value
        actual = formatting.format_kwargs(call)

        expected = [
            "a=1,",
        ]
        assert actual == expected

    def test_multiple_kwargs(self):
        """Test a call with multiple kwargs."""
        input_ = 'my_func(a="abc", b=True, func=another_func())'
        call = ast.parse(input_).body[0].value
        actual = formatting.format_kwargs(call)

        expected = [
            'a="abc",',
            "b=True,",
            "func=another_func(),",
        ]
        assert actual == expected

    def test_nested_func_calls(self):
        """Test a call with nested calls."""
        input_ = (
            "my_func("
            "func_a=another_func(a, b=2), "
            "func_b=foobar(True, a_list=[1, 2])"
            ")"
        )
        call = ast.parse(input_).body[0].value
        actual = formatting.format_kwargs(call)

        expected = [
            "func_a=another_func(a, b=2),",
            "func_b=foobar(True, a_list=[1, 2]),",
        ]
        assert actual == expected

    def test_kwargs_to_metadata(self):
        """Test kwargs are converted to metadata."""
        input_ = 'fields.Nested(many=True, required=False, example="this")'
        call = ast.parse(input_).body[0].value
        actual = formatting.format_kwargs(call, fix_kwargs_for_marshmallow_4=True)

        expected = [
            "many=True,",
            "required=False,",
            "metadata={",
            '    "example": "this",',
            "},",
        ]
        assert actual == expected

    def test_long_nonstring(self):
        """Test wrapping a long kwarg that is not a string."""
        input_ = (
            "fields.Nested("
            "fields.String(), "
            "foo=True, "
            "bar=[1, 2, 3], "
            "validate=this_is_a_long_function("
            "that_calls_other_stuff("
            "other_stuff(), more_other_stuff(an_arg=True), even_more_stuff(), "
            ")), "
            'description="a description")'
        )
        call = ast.parse(input_).body[0].value
        actual = formatting.format_kwargs(call)

        expected = [
            "foo=True,",
            "bar=[1, 2, 3],",
            "validate=this_is_a_long_function(",
            "    that_calls_other_stuff(",
            "        other_stuff(), more_other_stuff(an_arg=True), even_more_stuff()",
            "    )",
            "),",
            'description="a description",',
        ]
        assert actual == expected
