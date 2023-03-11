"""Text manipulation."""

import textwrap


def wrap_text(text, width=80):
    """Wrap text at a certain width.

    This is basically `textwrap.wrap` but:
    * continued lines have a space added at the end of the line
    * the returned lines are double-quoted

    :param str text: the text to wrap
    :param int width: the number of columns to wrap at

    :returns: the list of lines of wrapped text
    :rtype: list[str]
    """
    # Strip the quotes off each end of the text, we'll requote later
    text = strip_quotes(text)

    wrapped_lines = textwrap.wrap(text, width=width)
    # Add a space at the end of every line except the last one
    last_line_idx = len(wrapped_lines)
    wrapped_lines = [
        f"{line} " if idx != last_line_idx else line
        for idx, line in enumerate(wrapped_lines, start=1)
    ]
    lines = [format_builtin(line) for line in wrapped_lines]
    return lines


def indent(lines, indent_size=4, number=1):
    """Indent a list of lines of text.

    :param list[str] lines: the lines of text to indent
    :param int indent_size: the number of spaces per indent
    :param int number: the number of indent levels to add (>1)

    :returns: the list of indented lines:
    :rtype: list[str]
    """
    assert number >= 1
    spaces = " " * indent_size * number
    new_lines = [f"{spaces}{line}" for line in lines]
    return new_lines


def format_builtin(obj):
    """Format an object of built-in type as a string.

    String objects are double-quoted.

    :param object obj: the object to format as a string

    :returns: the formatted object
    :rtype: str
    """
    if isinstance(obj, str):
        ret = f'"{obj}"'
    else:
        ret = str(obj)
    return ret


def strip_quotes(text):
    """Strip matching double- or single-quotes from each end of a string.

    :param str text: the text from which to strip quotes

    :returns: the text without quotes
    :rtype: str
    """
    if (text[0] == '"' and text[-1] == '"') or (text[0] == "'" and text[-1] == "'"):
        text = text[1:-1]
    return text
