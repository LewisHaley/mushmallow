"""Convert AST nodes into strings as they would appear in Python files."""

import ast

from . import text


def repr_ast(node, full_call_repr=False):
    """Format AST as a string.

    The function acts recursively, decending down the tree to format each node.

    :param ast.AST node: Abstract-Syntax Tree object to be formatted
    :param bool full_call_repr: If True, format a full `ast.Call` object if
        encountered, including parenthesis, positional arguments and keyword
        arguments. If False, only the function name and any namespace is
        included.

    :returns: The string representation of of the node tree
    :rtype: str

    :raises ValueError: If the passed in node is not of type `ast.AST`
    :raises RuntimeError: If a valid node is found, but formatting is not
        implemented
    """
    if not isinstance(node, ast.AST):
        raise ValueError(f"{node!r} is not an AST type")

    node_func_mapping = {
        ast.Name: _repr_name,
        ast.Constant: _repr_constant,
        ast.Attribute: _repr_attribute,
        ast.arguments: _repr_arguments,
        ast.keyword: _repr_keyword,
        ast.Call: _repr_call,
        ast.Assign: _repr_assign,
        ast.List: _repr_list,
        ast.ListComp: _repr_listcomp,
        ast.Set: _repr_set,
        ast.SetComp: _repr_setcomp,
        ast.Dict: _repr_dict,
        ast.Expr: _repr_expr,
        ast.Tuple: _repr_tuple,
        ast.JoinedStr: _repr_joinedstr,
        ast.FormattedValue: _repr_formattedvalue,
        ast.BinOp: _repr_binop,
        ast.Add: lambda *_: "+",
        ast.Sub: lambda *_: "-",
        ast.Mult: lambda *_: "*",
        ast.Pow: lambda *_: "**",
        ast.Div: lambda *_: "/",
        ast.Mod: lambda *_: "%",
        ast.Lambda: _repr_lambda,
    }

    if repr_func := node_func_mapping.get(node.__class__):
        ret = repr_func(node, full_call_repr)
    else:
        raise RuntimeError(f"Couln't repr {node}")

    return ret


def _repr_name(node, full_call_repr):  # pylint: disable=unused-argument
    """Repr an `ast.Name`.

    :param ast.Name node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    return node.id


def _repr_constant(node, full_call_repr):  # pylint: disable=unused-argument
    """Repr an `ast.Constant`.

    :param ast.Constant node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    return text.format_builtin(node.value)


def _repr_attribute(node, full_call_repr):
    """Repr an `ast.Attribute`.

    :param ast.Attribute node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    return f"{repr_ast(node.value, full_call_repr)}.{node.attr}"


def _repr_arguments(node, full_call_repr):  # pylint: disable=unused-argument
    """Repr an `ast.keyword`.

    :param ast.keyword node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    # TODO: This is incompled and only supports positional arguments
    return ", ".join(arg.arg for arg in node.args)


def _repr_keyword(node, full_call_repr):
    """Repr an `ast.keyword`.

    :param ast.keyword node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    return f"{node.arg}={repr_ast(node.value, full_call_repr)}"


def _repr_call(node, full_call_repr):
    """Repr an `ast.Call`.

    :param ast.Call node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    if full_call_repr:
        ret = f"{repr_ast(node.func)}("
        args = ", ".join(repr_ast(arg, full_call_repr) for arg in node.args)
        ret += args
        kwargs = ", ".join(repr_ast(kw, full_call_repr) for kw in node.keywords)
        if args and kwargs:
            ret += ", "
        ret += kwargs
        ret += ")"
    else:
        ret = repr_ast(node.func)

    return ret


def _repr_assign(node, full_call_repr):
    """Repr an `ast.Assign`.

    :param ast.Assign node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    targets = ", ".join(map(lambda x: repr_ast(x, full_call_repr), node.targets))
    return f"{targets} = {repr_ast(node.value, full_call_repr)}"


def _repr_list(node, full_call_repr):
    """Repr an `ast.List`.

    :param ast.List node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    elts = [repr_ast(elt, full_call_repr) for elt in node.elts]
    return f"[{', '.join(elts)}]"


def _repr_listcomp(node, full_call_repr):
    """Repr an `ast.ListComp`.

    :param ast.ListComp node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    # TODO: We're only considering a single generator expression
    gen = node.generators[0]

    if isinstance(gen.target, ast.Tuple):
        target = f"{', '.join(repr_ast(elt) for elt in gen.target.elts)}"
    else:
        target = repr_ast(gen.target)

    ret = (
        f"[{repr_ast(node.elt)} "
        f"for {target} "
        f"in {repr_ast(gen.iter, full_call_repr)}]"
    )
    return ret


def _repr_dict(node, full_call_repr):
    """Repr an `ast.Dict`.

    :param ast.Dict node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    pairs = [
        f"{repr_ast(key)}: {repr_ast(val, full_call_repr)}"
        for key, val in zip(node.keys, node.values)
    ]
    return f"{{{', '.join(pairs)}}}"


def _repr_expr(node, full_call_repr):
    """Repr an `ast.Expre`.

    :param ast.Expr node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    return repr_ast(node.value, full_call_repr)


def _repr_tuple(node, full_call_repr):
    """Repr an `ast.Tuple`.

    :param ast.Tuple node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    elts = [repr_ast(elt, full_call_repr) for elt in node.elts]
    return f"({', '.join(elts)})"


def _repr_joinedstr(node, full_call_repr):
    """Repr an `ast.JoinedStr`.

    :param ast.JoinedStr node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    return f'f"{"".join(text.strip_quotes(repr_ast(v, full_call_repr)) for v in node.values)}"'


def _repr_formattedvalue(node, full_call_repr):
    """Repr an `ast.FormattedValue`.

    :param ast.FormattedValue node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    return f"{{{repr_ast(node.value, full_call_repr)}}}"


def _repr_binop(node, full_call_repr):
    """Repr an `ast.BinOp`.

    :param ast.BinOp node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    ret = (
        f"{repr_ast(node.left, full_call_repr)} "
        f"{repr_ast(node.op, full_call_repr)} "
        f"{repr_ast(node.right, full_call_repr)}"
    )
    return ret


def _repr_set(node, full_call_repr):
    """Repr an `ast.Set`.

    :param ast.Set node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    # TODO: This is identical to a list-comp except for using curly-brackets
    # rather than square-brackets
    elts = [repr_ast(elt, full_call_repr) for elt in node.elts]
    return f"{{{', '.join(elts)}}}"


def _repr_setcomp(node, full_call_repr):
    """Repr an `ast.SetComp`.

    :param ast.SetComp node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    # TODO: We're only considering a single generator expression
    # TODO: This is identical to a list-comp except for using curly-brackets
    # rather than square-brackets
    gen = node.generators[0]

    if isinstance(gen.target, ast.Tuple):
        target = f"{', '.join(repr_ast(elt) for elt in gen.target.elts)}"
    else:
        target = repr_ast(gen.target)

    ret = (
        f"{{{repr_ast(node.elt)} "
        f"for {target} "
        f"in {repr_ast(gen.iter, full_call_repr)}}}"
    )
    return ret


def _repr_lambda(node, full_call_repr):
    """Repr an `ast.Lambda`.

    :param ast.Lambda node:
    :param bool full_call_repr:

    :returns: the repr'd node
    :rtype: str
    """
    ret = "lambda"
    args = repr_ast(node.args, full_call_repr)
    if args:
        ret += f" {args}"
    ret += ": "
    ret += f"{repr_ast(node.body, full_call_repr)}"
    return ret
