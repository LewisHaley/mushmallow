"""Format output lines."""

import black

from . import text
from .repr_ast import repr_ast


def format_metadata(metadata, indent_size=4, max_line_length=80, sort_func=sorted):
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
        # Strip the quotes off each end of the text, we'll requote later
        second_bit = text.strip_quotes(second_bit)

        wrapped_lines = text.indent(text.wrap_text(second_bit, width=width))
        new_lines = [f"{first_bit}{sep}{parens[0]}"]
        new_lines.extend(wrapped_lines)
        new_lines.append(f"{parens[1]},")
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
