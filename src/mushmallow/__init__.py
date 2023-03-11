import ast
import inspect
import json
import sys
import textwrap

import black
import marshmallow

from ._text import indent, wrap_text


def repr_ast(ast_, full_call_repr=False):
    if not isinstance(ast_, ast.AST):
        raise ValueError(f"{ast_!r} is not an AST type")

    if isinstance(ast_, ast.Name):
        ret = ast_.id

    elif isinstance(ast_, ast.Constant):
        ret = format_builtin(ast_.value)

    elif isinstance(ast_, ast.Attribute):
        ret = f"{repr_ast(ast_.value, full_call_repr=full_call_repr)}.{ast_.attr}"

    elif isinstance(ast_, ast.keyword):
        ret = f"{ast_.arg}={repr_ast(ast_.value, full_call_repr=full_call_repr)}"

    elif isinstance(ast_, ast.Call):
        if full_call_repr:
            ret = f"{repr_ast(ast_.func)}("
            args = ", ".join(
                repr_ast(arg, full_call_repr=full_call_repr)
                for arg in ast_.args
            )
            ret += args
            kwargs = ", ".join(
                repr_ast(kw, full_call_repr=full_call_repr)
                for kw in ast_.keywords
            )
            if args and kwargs:
                ret += ", "
            ret += kwargs
            ret += ")"
        else:
            ret = repr_ast(ast_.func)

    elif isinstance(ast_, ast.Assign):
        targets = ", ".join(map(
            lambda x: repr_ast(x, full_call_repr=full_call_repr),
            ast_.targets
        ))
        first_line = f"{targets} = {repr_ast(ast_.value, full_call_repr=full_call_repr)}"
        ret = first_line

    elif isinstance(ast_, ast.List):
        ret = [repr_ast(elt) for elt in ast_.elts]

    elif isinstance(ast_, ast.ListComp):
        ret = (
            f"[{repr_ast(ast_.elt)} "
            f"for {repr_ast(ast_.generators[0].target)} "
            f"in {repr_ast(ast_.generators[0].iter)}]"
        )

    elif isinstance(ast_, ast.Dict):
        ret = "{}"

    else:
        raise ValueError(f"Couln't repr {ast_}")

    return ret


def format_metadata(
    metadata, indent_size=4, max_line_length=80, sort_func=sorted
):
    meta_lines = [
        "metadata={",
    ]
    items = []
    for meta_name, meta_value in sort_func(metadata.items()):
        items.extend(maybe_wrap_line(
            meta_name, ": ", meta_value, "()",
            width=max_line_length - (indent_size * 2),
        ))
    meta_lines.extend(indent(items))
    meta_lines.append("},")
    return meta_lines


def maybe_wrap_line(first_bit, sep, second_bit, parens, width=80):
    new_line = f"{first_bit}{sep}{second_bit},"
    if len(new_line) > width:
        wrapped_lines = indent(wrap_text(second_bit, width=width))
        new_lines = [f"{first_bit}{sep}{parens[0]}"]
        new_lines.extend(wrapped_lines)
        new_lines.append(f"{parens[1]},")
    else:
        new_lines = [new_line]

    return new_lines


def format_field(
    field,
    indent_size=4,
    max_line_length=80,
    fix_kwargs_for_marshmallow_4=True,
    sort_func=sorted,
):
    field = field.replace("\"\"", "").replace("''", "")
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
    ast_ = ast.parse(no_indent).body
    assert len(ast_) == 1
    statement = ast_[0]
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

    # Create kwargs dict. We aren't dealing with long lines here, because we
    # will do it later if necessary.
    kwargs = {
        kw.arg: repr_ast(kw.value, full_call_repr=True)
        for kw in statement.value.keywords
    }

    if fix_kwargs_for_marshmallow_4:
        # Fix kwargs for Marshmallow 4
        new_kwargs = {}
        metadata = kwargs.get("metadata", {})
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
        f"{arg},"
        if not (
            arg.endswith(",")
            or arg.endswith("(")
        )
        else arg
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
            kwarg_lines.extend(maybe_wrap_line(
                kwarg_name, "=", kwarg_value, "()",
                width=max_line_length - (indent_size * 2),
            ))
    new_field_lines.extend(indent(kwarg_lines))
    new_field_lines.append(")")  # Close the field definition

    indented_new_field_lines = indent(
        new_field_lines,
        number=initial_indent_spaces // indent_size,
    )
    return indented_new_field_lines


def main():
    file_to_fix = sys.argv[1]

    with open(file_to_fix, mode="r") as fd:
        lines = map(str.rstrip, fd.readlines())

    max_line_length = 80
    indent_size = 4
    fix_kwargs_for_marshmallow_4 = True
    sort_items = False

    if sort_items:
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

    print("\n".join(outlines))


if __name__ == "__main__":
    main()
