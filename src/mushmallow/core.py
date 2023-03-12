"""Core functionality for Mushmallow."""

import ast

from .formatting import format_args, format_kwargs, noop
from .repr_ast import repr_ast
from .text import indent


def format_field(
    field,
    indent_size=4,
    max_line_length=80,
    fix_kwargs_for_marshmallow_4=False,
    sort_func=noop,
):
    """Format a single field into lines of text.

    :param str field: a single string containing the definition of an entire
    :param int indent_size: the number of spaces per indent
    :param int max_line_length: how many characters per line to allow
    :param bool fix_kwargs_for_marshmallow_4: If True, convert kwarg fields to
        metadata fields as per Marshmallow 4
    :param callable sort_func: a function to sort the field kwargs

    :returns: the list of lines having formatted the field string
    :rtype: list[str]
    """
    field = field.replace('""', "").replace("''", "")
    no_indent = field.lstrip()

    # Get the pieces we need, i.e. the assignment of the field name, and
    # any args and kwargs passed into the field class.
    initial_indent_spaces = len(field) - len(no_indent)
    nodes = ast.parse(no_indent).body
    assert len(nodes) == 1
    statement = nodes[0]
    first_line = repr_ast(statement)

    arg_lines = format_args(statement.value, max_line_length=max_line_length)
    kwarg_lines = format_kwargs(
        statement.value,
        max_line_length=max_line_length,
        indent_size=indent_size,
        fix_kwargs_for_marshmallow_4=fix_kwargs_for_marshmallow_4,
        sort_func=sort_func,
    )

    new_field_lines = [
        f"{first_line}(",
    ]
    new_field_lines.extend(indent(arg_lines))
    new_field_lines.extend(indent(kwarg_lines))
    new_field_lines.append(")")  # Close the field definition

    indented_new_field_lines = indent(
        new_field_lines,
        number=initial_indent_spaces // indent_size,
    )
    return indented_new_field_lines


def format_marshmallow(
    lines,
    max_line_length=80,
    indent_size=4,
    fix_kwargs_for_marshmallow_4=False,
    sort=False,
):
    """Format Marshmallow schemas in lines of a file.

    :param list[str] lines: the original lines to format
    :param int max_line_length: how many characters per line to allow
    :param int indent_size: the number of spaces per indent
    :param bool fix_kwargs_for_marshmallow_4: If True, convert kwarg fields to
        metadata fields as per Marshmallow 4
    :param bool sort: Sort kwarg and/or metadata fields alphabetically.
        Otherwise order is arbitrary.

    :returns: the lines of the file having been formatted
    :rtype: list[str]
    """
    if sort:
        sort_func = sorted
    else:
        sort_func = noop

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

    return outlines
