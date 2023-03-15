"""Tests for core.py."""

import pytest

from mushmallow import core


class TestFormatField:
    """Tests for `format_field`."""

    def test_empty_field(self):
        """Test empty field."""
        input_ = "my_field = fields.String()"
        actual = core.format_field(input_)
        expected = ["my_field = fields.String()"]
        assert actual == expected

    def test_minimal(self):
        """Test minimal field."""
        input_ = "my_field = fields.String(required=True)"
        actual = core.format_field(input_)
        expected = [
            "my_field = fields.String(",
            "    required=True,",
            ")",
        ]
        assert actual == expected

    def test_quotes_are_normalised(self):
        """Test single-quoted-strings become double-quoted."""
        input_ = "my_field = fields.Boolean(description='foo')"
        actual = core.format_field(input_)
        expected = [
            "my_field = fields.Boolean(",
            '    description="foo",',
            ")",
        ]
        assert actual == expected

    def test_leading_indent_preserved(self):
        """Test that any leading indent is preserved."""
        input_ = "    my_field = fields.Integer()"
        actual = core.format_field(input_)
        expected = [
            "    my_field = fields.Integer()",
        ]
        assert actual == expected

    def test_closing_paren_aligns_with_indent(self):
        """Test that any leading indent is preserved."""
        input_ = "    my_field = fields.Integer(allow_none=True)"
        actual = core.format_field(input_)
        expected = [
            "    my_field = fields.Integer(",
            "        allow_none=True,",
            "    )",
        ]
        assert actual == expected

    @pytest.mark.xfail(reason="The nested dict is not repr'd as expected")
    def test_nested_dict_in_metadata(self):
        """Test a nested dict in a metadata."""
        input_ = "my_field = fields.Field(metadata={'a': {'b': {'c': 3}}})"
        actual = core.format_field(input_)
        expected = [
            "my_field = fields.Field(",
            "    metadata={",
            '        "a": {"b": {"c": 3}},',
            "    },",
            ")",
        ]
        assert actual == expected


class TestFixKwargsForMarshmallow4:
    """Test fix `format_field` with `fix_kwargs_for_marshmallow_4=True`."""

    def test_empty(self):
        """Test empty field."""
        input_ = "my_field = fields.String()"
        actual = core.format_field(input_, fix_kwargs_for_marshmallow_4=True)
        expected = ["my_field = fields.String()"]
        assert actual == expected

    def test_minimal(self):
        """Test minimal field."""
        input_ = "my_field = fields.String(required=True)"
        actual = core.format_field(input_, fix_kwargs_for_marshmallow_4=True)
        expected = [
            "my_field = fields.String(",
            "    required=True,",
            ")",
        ]
        assert actual == expected

    def test_moved_to_new_metadata(self):
        """A kwarg is moved to metadata, that didn't previously exist."""
        input_ = "my_field = fields.List(many=True)"
        actual = core.format_field(input_, fix_kwargs_for_marshmallow_4=True)
        expected = [
            "my_field = fields.List(",
            "    metadata={",
            '        "many": True,',
            "    },",
            ")",
        ]
        assert actual == expected

    def test_mixed_moved_to_new_metadata(self):
        """Mixed kwargs moved to metadata, that didn't previously exist."""
        input_ = "my_field = fields.List(required=True, many=True)"
        actual = core.format_field(input_, fix_kwargs_for_marshmallow_4=True)
        expected = [
            "my_field = fields.List(",
            "    required=True,",
            "    metadata={",
            '        "many": True,',
            "    },",
            ")",
        ]
        assert actual == expected

    def test_moved_to_existing_metadata(self):
        """A kwarg is moved to metadata, that didn't previously exist."""
        input_ = "my_field = fields.List(many=True,metadata={'example': [1, 2, 3]})"
        actual = core.format_field(input_, fix_kwargs_for_marshmallow_4=True)
        expected = [
            "my_field = fields.List(",
            "    metadata={",
            '        "example": [1, 2, 3],',
            '        "many": True,',
            "    },",
            ")",
        ]
        assert actual == expected

    def test_duplicated_in_metadata(self):
        """Test when a kwarg duplicates a metadata key."""
        input_ = 'my_field = fields.String(example="abc",metadata={"example": "xyz"})'
        actual = core.format_field(input_, fix_kwargs_for_marshmallow_4=True)
        # Note that the kwarg takes priority
        expected = [
            "my_field = fields.String(",
            "    metadata={",
            '        "example": "abc",',
            "    },",
            ")",
        ]
        assert actual == expected


class TestFormatMarshmallow:
    """Tests for `format_marshmallow`."""

    def test_basic(self):
        """Basic test."""
        input_ = [
            "class MySchema(Schema):",
            "    val_1 = fields.String()",
            "    val_2 = fields.Boolean()",
        ]
        actual = core.format_marshmallow(input_)
        expected = [
            "class MySchema(Schema):",
            "    val_1 = fields.String()",
            "    val_2 = fields.Boolean()",
        ]
        assert actual == expected

    def test_basic_with_multiple_schemas(self):
        """Basic test featuring multiple schemas."""
        input_ = [
            "class ASchema(Schema):",
            "    val_1 = fields.String()",
            "    val_2 = fields.Boolean()",
            "",
            "class AnotherSchema(Schema)",
            "    a_list = fields.List()",
        ]
        actual = core.format_marshmallow(input_)
        expected = [
            "class ASchema(Schema):",
            "    val_1 = fields.String()",
            "    val_2 = fields.Boolean()",
            "",
            "class AnotherSchema(Schema)",
            "    a_list = fields.List()",
        ]
        assert actual == expected

    def test_complex_schema__no_change(self):
        """Format a complex schema that requires no changes."""
        input_ = [
            "class ASchema(Schema):",
            "    val_1 = fields.String(",
            "        required=True,",
            "    )",
            "    val_2 = fields.Boolean(",
            "        allow_none=True,",
            "    )",
        ]
        actual = core.format_marshmallow(input_)
        expected = [
            "class ASchema(Schema):",
            "    val_1 = fields.String(",
            "        required=True,",
            "    )",
            "    val_2 = fields.Boolean(",
            "        allow_none=True,",
            "    )",
        ]
        assert actual == expected

    def test_non_schema_classes_are_ignored(self):
        """Test that non-schema classes are not affected."""
        input_ = [
            "class ASchema(Skooma):",
            "    val_1 = fields.String(required=True)",
        ]
        actual = core.format_marshmallow(input_)
        expected = [
            "class ASchema(Skooma):",
            "    val_1 = fields.String(required=True)",
        ]
        assert actual == expected

    def test_other_code_is_left_alone(self):
        """Test that regular, non-schema code is not modified."""
        input_ = [
            "def my_func(a):",
            "    return a",
            "",
            "class MyClass:",
            "    def __init__(self):",
            "        pass",
            "",
            "",
            "foobar = 1",
            "qux = my_func(foobar)",
        ]
        actual = core.format_marshmallow(input_)
        expected = [
            "def my_func(a):",
            "    return a",
            "",
            "class MyClass:",
            "    def __init__(self):",
            "        pass",
            "",
            "",
            "foobar = 1",
            "qux = my_func(foobar)",
        ]
        assert actual == expected

    def test_fields_outside_a_schema_are_ignored(self):
        """Test that only fields inside a schema are modified."""
        input_ = [
            "class MySchema(Schema):",
            "    foo = fields.Nested(AnotherSchema(), many=True)",
            "",
            "",
            "the_field = fields.Boolean(required=False)",
            "another_field = fields.String(validate=validator_func)",
        ]
        actual = core.format_marshmallow(input_)
        expected = [
            "class MySchema(Schema):",
            "    foo = fields.Nested(",
            "        AnotherSchema(),",
            "        many=True,",
            "    )",
            "",
            "",
            "the_field = fields.Boolean(required=False)",
            "another_field = fields.String(validate=validator_func)",
        ]
        assert actual == expected

    def test_empty_string(self):
        """Test that empty strings are handled properly."""
        input_ = [
            "class MySchema(Schema):",
            "    foo = fields.String(",
            '        missing="",',
            "    )",
        ]
        actual = core.format_marshmallow(input_)
        expected = [
            "class MySchema(Schema):",
            "    foo = fields.String(",
            '        missing="",',
            "    )",
        ]
        assert actual == expected

    def test_multiline_string(self):
        """Test that multi-line strings are handled properly."""
        input_ = [
            "class MySchema(Schema):",
            "    foo = fields.String(",
            '        missing="abcde fghij klmno qrstu vwxyz 123 456 789"',
            '                "abcde fghij klmno qrstu vwxyz 123 456 789"',
            "    )",
        ]
        actual = core.format_marshmallow(input_, max_line_length=55)
        expected = [
            "class MySchema(Schema):",
            "    foo = fields.String(",
            "        missing=(",
            '            "abcde fghij klmno qrstu vwxyz 123 456 "',
            '            "789abcde fghij klmno qrstu vwxyz 123 "',
            '            "456 789"',
            "        ),",
            "    )",
        ]
        assert actual == expected

    def test_comments_are_preserved(self):
        """Test that comments are preserved."""
        input_ = [
            "# Leading comment.",
            "class MySchema(Schema):",
            "    # Actually it's an integer",
            "    foo = fields.String()",
            "    bar = fields.Boolean(",
            "        # Internal comment",
            "        required=True,",
            "    )",
        ]
        actual = core.format_marshmallow(input_)
        expected = [
            "# Leading comment.",
            "class MySchema(Schema):",
            "    # Actually it's an integer",
            "    foo = fields.String()",
            "    bar = fields.Boolean(",
            "        # Internal comment",
            "        required=True,",
            "    )",
        ]
        assert actual == expected

    @pytest.mark.xfail(reason="AST gets rid of them")
    def test_end_of_line_comments_are_preserved(self):
        """Test that end-of_line comments are preserved."""
        input_ = [
            "# Leading comment.",
            "class MySchema(Schema):",
            "    # Actually it's an integer",
            "    foo = fields.String()",
            "    bar = fields.Boolean(",
            "        # Internal comment",
            "        required=True,",
            "        allow_none=True,  # inline comment",
            "    )",
        ]
        actual = core.format_marshmallow(input_)
        expected = [
            "# Leading comment.",
            "class MySchema(Schema):",
            "    # Actually it's an integer",
            "    foo = fields.String()",
            "    bar = fields.Boolean(",
            "        # Internal comment",
            "        required=True,",
            "        allow_none=True,  # end-of-line comment",
            "    )",
        ]
        assert actual == expected

    def test_blank_lines_within_schema(self):
        """Test that blank lines within a schema don't matter."""
        input_ = [
            "class MySchema(Schema):",
            "    foo = fields.String()",
            "",
            "    bar = fields.Boolean()",
            "",
            "    qux = fields.Integer()",
            "",
            "",
            "class AnotherSchema():",
            "",
            "    thing = fields.List()",
            "",
        ]
        actual = core.format_marshmallow(input_)
        expected = [
            "class MySchema(Schema):",
            "    foo = fields.String()",
            "",
            "    bar = fields.Boolean()",
            "",
            "    qux = fields.Integer()",
            "",
            "",
            "class AnotherSchema():",
            "",
            "    thing = fields.List()",
            "",
        ]
        assert actual == expected
