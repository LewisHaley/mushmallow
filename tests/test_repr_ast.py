"""Tests for repr_ast.py."""

import ast

import pytest

from mushmallow.repr_ast import repr_ast

# pylint: disable=missing-param-doc,missing-type-doc


class TestReprAst:
    """Tests for `repr_ast`."""

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("my_var", "my_var"),
            ("my_obj.my_attr", "my_obj.my_attr"),
        ],
    )
    def test_repr_name(self, input_, expected):
        """Test ast.Name."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("1", "1"),
            ("3.14", "3.14"),
            ('"a string"', '"a string"'),
            ("True", "True"),
            ("None", "None"),
        ],
    )
    def test_repr_const(self, input_, expected):
        """Test ast.Const."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("val = 1", "val = 1"),
            ('val = "my val"', 'val = "my val"'),
            # Note: no parens because full_call_repr == False
            ("val = my_func()", "val = my_func"),
        ],
    )
    def test_repr_assign(self, input_, expected):
        """Test ast.Assign."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("[]", "[]"),
            ("[1]", "[1]"),
            ("[1, 2]", "[1, 2]"),
            ('["a", "b"]', '["a", "b"]'),
        ],
    )
    def test_repr_list(self, input_, expected):
        """Test ast.List."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("[x for x in my_iter]", "[x for x in my_iter]"),
            ("[x for x in my_obj.my_iter]", "[x for x in my_obj.my_iter]"),
            ("[x for x, y in my_iter]", "[x for x, y in my_iter]"),
            ("[(x, y) for x, y in my_iter]", "[(x, y) for x, y in my_iter]"),
            ("[i for i in range(10)]", "[i for i in range]"),
        ],
    )
    def test_repr_listcomp(self, input_, expected):
        """Test ast.List."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("{}", "{}"),
            ('{"a": 1}', '{"a": 1}'),
            ('{"a": 1, "b": 2}', '{"a": 1, "b": 2}'),
        ],
    )
    def test_repr_dict(self, input_, expected):
        """Test ast.Dict."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("my_func()", "my_func"),
            ("my_mod.my_func()", "my_mod.my_func"),
        ],
    )
    def test_repr_call__not_full(self, input_, expected):
        """Test ast.Call."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("my_func()", "my_func()"),
            ("my_mod.my_func()", "my_mod.my_func()"),
            ("my_func(a, b, c=3)", "my_func(a, b, c=3)"),
            ("my_func([a, b, c])", "my_func([a, b, c])"),
            ("outer(inner())", "outer(inner())"),
            ("outer(inner(arg, kwarg=True))", "outer(inner(arg, kwarg=True))"),
        ],
    )
    def test_repr_call__full(self, input_, expected):
        """Test ast.Call."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node, full_call_repr=True)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("a = 1", "a = 1"),
            ('a = "a"', 'a = "a"'),
            ("my_var = my_func()", "my_var = my_func()"),
        ],
    )
    def test_repr_assign__full_call(self, input_, expected):
        """Test ast.Assign."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node, full_call_repr=True)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("1 - 1", "1 - 1"),
            ('"a" + "b"', '"a" + "b"'),
            ("0 / 2", "0 / 2"),
            ("2 * 2", "2 * 2"),
            ("2 ** 2", "2 ** 2"),
            ("2 % 2", "2 % 2"),
        ],
    )
    def test_repr_binop(self, input_, expected):
        """Test ast.BinOp."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node, full_call_repr=True)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("f'this'", 'f"this"'),
            ('f"this"', 'f"this"'),
            ('f"a {b} c"', 'f"a {b} c"'),
            ('f"a {b} c {last}"', 'f"a {b} c {last}"'),
        ],
    )
    def test_repr_joinedstr(self, input_, expected):
        """Test ast.JoinedStr."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node, full_call_repr=True)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("{}", "{}"),
            ("{1}", "{1}"),
            ("{1, 2}", "{1, 2}"),
            ('{"a", "b"}', '{"a", "b"}'),
        ],
    )
    def test_repr_set(self, input_, expected):
        """Test ast.Set."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("{a for a in my_set}", "{a for a in my_set}"),
            ("{a for a in my_gen()}", "{a for a in my_gen()}"),
        ],
    )
    def test_repr_setcomp(self, input_, expected):
        """Test ast.SetComp."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node, full_call_repr=True)
        assert actual == expected

    @pytest.mark.parametrize(
        "input_, expected",
        [
            ("lambda: True", "lambda: True"),
            ("lambda x: int(x)", "lambda x: int(x)"),
        ],
    )
    def test_repr_lambda(self, input_, expected):
        """Test ast.Lambda."""
        node = ast.parse(input_).body[0]
        actual = repr_ast(node, full_call_repr=True)
        assert actual == expected
