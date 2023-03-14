"""Format output lines."""

import ast
import inspect
import json

import black
import marshmallow

from . import text
from .repr_ast import repr_ast


def noop(first_arg, *args, **kwargs):  # pylint: disable=unused-argument
    # pylint: disable=missing-function-docstring
    # pylint: disable=missing-return-doc, missing-return-type-doc
    return first_arg


def format_metadata(metadata, indent_size=4, max_line_length=80, sort_func=noop):
    """Format the metadata dictionary for Marshmallow.

    The lines of text returned here are the "final" lines, minus any leading
    indentation which needs to be added.

    :param dict metadata: the metadata dictionary to format as a list of strings
    :param int indent_size: the number of spaces to add infront of each item in
        the metadata dict
    :param int max_line_length: the maximum length of line, including any
        indentation
    :param callable sort_func: a function to sort the the metadata items

    :returns: the list of lines from having formatted the the metadata
    :rtype: list[str]
    """
    if not metadata:
        return ["metadata={},"]

    meta_lines = [
        "metadata={",
    ]
    items = []
    for meta_name, meta_value in sort_func(metadata.items()):
        items.extend(
            maybe_wrap_line(
                text.format_builtin(meta_name),
                ": ",
                meta_value,
                "()",
                width=max_line_length - indent_size,
            )
        )
    meta_lines.extend(text.indent(items))
    meta_lines.append("},")
    return meta_lines


def maybe_wrap_line(first_bit, sep, second_bit, parens, width=80):
    """Wrap a line over multiple lines using parentheses if necessary.

    To be used for lines like:
        "dict_key": "the value of the dict",
    or:
        keyword="the keyword value",

    To produce:
        "dict_key": (
            "the value of the dict"
        ),
    or:
        keyword=(
            "the keyword value",
        ),
    respectively.

    :param str first_bit: the name of the dictionary key or keyword
    :param str sep: the separator between the first bit and the second bit
    :param str second_bit: the string value of the dictionary key or keyword
    :param str parens: a two-character string with the opening and closing
        parenthesis to use to wrap the multi-line string if necessary
    :param int width : the maximum length of line, after which wrapping is
        required

    :returns: the list of lines after wrapping. If no wrapping is required, then
        the `first_bit`, `sep`, and `second_bit` are formatted into a single
        line and returned as a single-element list
    :rtype: list[str]
    """
    new_line = f"{first_bit}{sep}{second_bit},"
    if len(new_line) > width:
        if second_bit.startswith('"') and second_bit.endswith('"'):
            # Strip the quotes off each end of the text, we'll requote later
            second_bit = text.strip_quotes(second_bit)

            wrapped_lines = text.indent(text.wrap_text(second_bit, width=width))
            new_lines = [f"{first_bit}{sep}{parens[0]}"]
            new_lines.extend(wrapped_lines)
            new_lines.append(f"{parens[1]},")
        else:
            new_lines = black.format_str(
                second_bit,
                mode=black.FileMode(line_length=width),
            ).splitlines()
            new_lines[0] = f"{first_bit}{sep}{new_lines[0]}"
            new_lines[-1] = f"{new_lines[-1]},"

    else:
        new_lines = [new_line]

    return new_lines


def format_args(call, max_line_length=80):
    """Format positional arguments from a function call.

    :param ast.Call call: the call for which to format the position arguments
    :param int max_line_length: the maximum length of line, including any
        indentation

    :returns: the list of lines from having formatted the the metadata
    :rtype: list[str]
    """
    # Format each arg, which might go over multiple lines.
    args = []
    for arg in call.args:
        args.extend(
            black.format_str(
                repr_ast(arg, full_call_repr=True),
                mode=black.FileMode(line_length=max_line_length),
            ).splitlines()
        )

    arg_lines = [
        f"{arg}," if not (arg.endswith(",") or arg.endswith("(")) else arg
        for arg in args
    ]
    return arg_lines


def kwargs_to_metadata(kwargs, nonmetadata_field_kwargs):
    """Move unknown fields kwargs to metadata.

    This conversion is required for Marshmallow 4. See
    https://github.com/marshmallow-code/marshmallow/commit/013abfd669f64446cc7954d0320cf5f1d668bd49

    :param dict kwargs: the keyword arguments to a marshmallow field
    :param set[str] nonmetadata_field_kwargs: the set of valid keyword
        arguments (and anything else is metadata)

    :returns: the modified kwargs
    :rtype: dict
    """
    new_kwargs = {}
    metadata = kwargs.pop("metadata", {})
    for kwarg_name, kwarg_value in kwargs.items():
        if kwarg_name not in nonmetadata_field_kwargs:
            metadata[kwarg_name] = kwarg_value
        else:
            new_kwargs[kwarg_name] = kwarg_value

    if metadata:
        new_kwargs["metadata"] = metadata
    return new_kwargs


def format_kwargs(
    call,
    max_line_length=80,
    indent_size=4,
    fix_kwargs_for_marshmallow_4=False,
    sort_func=noop,
):
    """Format keyword arguments from a function call.

    :param ast.Call call: the call for which to format the position arguments
    :param int max_line_length: the maximum length of line, including any
        indentation
    :param int indent_size: the number of spaces to add infront of each item in
    :param bool fix_kwargs_for_marshmallow_4: If True, convert kwarg fields to
        metadata fields as per Marshmallow 4
    :param callable sort_func: a function to sort the the metadata items

    :returns: the list of lines from having formatted the the metadata
    :rtype: list[str]
    """

    def unwrap_ast_dict(dct):
        """The AST node to unwrap recursively.

        If the node is not a dictionary, it is returned stringified. If any of
        the fields map to another dictionary, that is also unwrapped.

        :param ast.Dict dct: the dictionary node to unwrap

        :returns: the unwrapped dictionary
        :rtype: dict
        """
        if not isinstance(dct, ast.Dict):
            return text.strip_quotes(repr_ast(dct, full_call_repr=True))

        new_dct = {
            text.strip_quotes(repr_ast(k)): unwrap_ast_dict(v)
            for k, v in zip(dct.keys, dct.values)
        }
        return new_dct

    # Create kwargs dict. We aren't dealing with long lines here, because we
    # will do it later if necessary.
    kwargs = {
        kw.arg: (
            unwrap_ast_dict(kw.value)
            if isinstance(kw.value, ast.Dict)
            else repr_ast(kw.value, full_call_repr=True)
        )
        for kw in call.keywords
    }

    if fix_kwargs_for_marshmallow_4:
        nonmetadata_field_kwargs = set(
            inspect.signature(marshmallow.fields.Field).parameters.keys()
        )
        if call.func.value.id == "fields" and call.func.attr == "Nested":
            nonmetadata_field_kwargs.update(
                set(inspect.signature(marshmallow.fields.Nested).parameters.keys())
            )
        kwargs = kwargs_to_metadata(kwargs, nonmetadata_field_kwargs)

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
            if isinstance(kwarg_value, dict):
                kwarg_value = json.dumps(kwarg_value)

            kwarg_lines.extend(
                maybe_wrap_line(
                    kwarg_name,
                    "=",
                    kwarg_value,
                    "()",
                    width=max_line_length - (indent_size * 2),
                )
            )

    return kwarg_lines
