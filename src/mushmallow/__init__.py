"""Mushmallow - a formatting tool for Marshmallow."""

import ast
import inspect
import json
import sys
import textwrap

import black
import marshmallow

from .formatting import format_metadata, maybe_wrap_line
from .text import indent, strip_quotes
from .repr_ast import repr_ast


def format_field(
    field,
    indent_size=4,
    max_line_length=80,
    fix_kwargs_for_marshmallow_4=True,
    sort_func=sorted,
):
    field = field.replace('""', "").replace("''", "")
    no_indent = field.lstrip()

    if "Nested(" in field:
        nonmetadata_field_kwargs = inspect.signature(
            marshmallow.fields.Nested
        ).parameters.keys()
    else:
        nonmetadata_field_kwargs = inspect.signature(
            marshmallow.fields.Field
        ).parameters.keys()

    # Get the pieces we need, i.e. the assignment of the field name, and
    # any args and kwargs passed into the field class.
    initial_indent_spaces = len(field) - len(no_indent)
    nodes = ast.parse(no_indent).body
    assert len(nodes) == 1
    statement = nodes[0]
    if (
        statement.value.func.value.id == "fields"
        and statement.value.func.attr == "Nested"
    ):
        nonmetadata_field_kwargs = inspect.signature(
            marshmallow.fields.Nested
        ).parameters.keys()
    else:
        nonmetadata_field_kwargs = inspect.signature(
            marshmallow.fields.Field
        ).parameters.keys()
    first_line = repr_ast(statement)

    # Format each arg, which might go over multiple lines.
    args = []
    for arg in statement.value.args:
        args.extend(
            black.format_str(
                repr_ast(arg, full_call_repr=True),
                mode=black.FileMode(line_length=max_line_length),
            ).splitlines()
        )

    def unwrap_ast_dict(dct):
        if not isinstance(dct, ast.Dict):
            return strip_quotes(repr_ast(dct, full_call_repr=True))

        new_dct = {
            strip_quotes(repr_ast(k)): unwrap_ast_dict(v)
            for k, v in zip(dct.keys, dct.values)
        }
        return new_dct

    # Create kwargs dict. We aren't dealing with long lines here, because we
    # will do it later if necessary.
    kwargs = {
        kw.arg: (
            unwrap_ast_dict(kw.value)
            if isinstance(kw.value, ast.Dict)
            else strip_quotes(repr_ast(kw.value, full_call_repr=True))
        )
        for kw in statement.value.keywords
    }

    if fix_kwargs_for_marshmallow_4:
        # Fix kwargs for Marshmallow 4
        new_kwargs = {}
        metadata = kwargs.pop("metadata", {})
        for kwarg_name, kwarg_value in kwargs.items():
            if kwarg_name not in nonmetadata_field_kwargs:
                metadata[kwarg_name] = kwarg_value
            else:
                new_kwargs[kwarg_name] = kwarg_value

        if metadata:
            new_kwargs["metadata"] = metadata

        kwargs = new_kwargs

    new_field_lines = [
        f"{first_line}(",
    ]
    arg_lines = [
        f"{arg}," if not (arg.endswith(",") or arg.endswith("(")) else arg
        for arg in args
    ]
    new_field_lines.extend(indent(arg_lines))
    kwarg_lines = []
    for kwarg_name, kwarg_value in sort_func(kwargs.items()):
        if kwarg_name == "metadata":
            meta_lines = format_metadata(
                kwarg_value,
                max_line_length=max_line_length,
                sort_func=sort_func,
            )
            kwarg_lines.extend(meta_lines)
        else:
            kwarg_lines.extend(
                maybe_wrap_line(
                    kwarg_name,
                    "=",
                    kwarg_value,
                    "()",
                    width=max_line_length - (indent_size * 2),
                )
            )
    new_field_lines.extend(indent(kwarg_lines))
    new_field_lines.append(")")  # Close the field definition

    indented_new_field_lines = indent(
        new_field_lines,
        number=initial_indent_spaces // indent_size,
    )
    return indented_new_field_lines


def fix_marshmallow(
    file_to_fix,
    max_line_length=80,
    indent_size=4,
    fix_kwargs_for_marshmallow_4=False,
    sort=False,
):
    """Fix/Format Marshmallow schemas in a file.

    :param pathlib.Path file_to_fix: the file to fix
    :param int max_line_length: how many characters per line to allow
    :param int indent_size: the number of spaces per indent
    :param bool fix_kwargs_for_marshmallow_4: If True, convert kwarg fields to
        metadata fields as per Marshmallow 4
    :param bool sort: Sort kwarg and/or metadata fields alphabetically.
        Otherwise order is arbitrary.
    """
    lines = file_to_fix.read_text().splitlines()

    if sort:
        sort_func = sorted
    else:
        sort_func = lambda it, **_: it

    outlines = []
    inside_schema = False
    inside_field = False
    curr_field = ""
    for line in lines:
        # This is a bit rubbish. We're assuming all Schemas inherit from an
        # object which ends with "Schema".
        if line.strip().startswith("class ") and line.endswith("Schema):"):
            inside_schema = True
        elif line.strip().startswith("def ") or not line:
            inside_schema = False

        if not inside_schema:
            outlines.append(line)
            continue

        # From this point, we are inside a schema definition
        if " = " in line and "fields." in line:
            inside_field = True

        if inside_field:
            # Accumulate all lines within a field definition, suppressing output
            # until we accumulate a whole definition.
            curr_field += line.strip() if curr_field else line
        else:
            outlines.append(line)

        if curr_field and curr_field.count("(") == curr_field.count(")"):
            # We're accumulateing a field, and we have an equal number of
            # opening and closing parenthesis. This means the field class is
            # fully closed. Obviously there a lot of ways this could fail.
            field = curr_field
            curr_field = ""
            inside_field = False

            field_lines = format_field(
                field,
                indent_size=indent_size,
                max_line_length=max_line_length,
                fix_kwargs_for_marshmallow_4=fix_kwargs_for_marshmallow_4,
                sort_func=sort_func,
            )
            outlines.extend(field_lines)

    file_to_fix.write_text("\n".join(outlines) + "\n")
