# Mushmallow

Reformat Marshmallow schemas.

I wrote this tool to handle the transformation of implicit to explicit metadata
fields in Marshmallow schemas, as per https://github.com/marshmallow-code/marshmallow/pull/1702.

For example:

```
from marshmallow import Schema, fields

class MySchema(Schema):
    my_field = fields.String(
        allow_none=True,
        description="This is my field"
    )
```

gets transformed to

```
from marshmallow import Schema, fields

class MySchema(Schema):
    my_field = fields.String(
        allow_none=True,
        metadata={
            "description": "This is my field",
        },
    )
```

(with `--fix-kwargs-for-marshmallow-4` specified`).

The tool can/will:
* Wrap lines at a configurable line length (a bit like `black`)
* Standardize on double quoted strings (a bit like `black`)
* Standardize on how multi-line strings are formatted
* Add trailing commas (a bit like `black`)
* Optionally sort keyword arguments/dictionary keys alphabetically
* Optionally produce a diff rather than modifiy the files (a bit like `black`)

See `--help` for the full list of options. See the unit tests (particularly
`test_core.py` to see the transformations that are applied.

### Installation and running

1. Checkout the repo
2. `make venv`
3. `venv/bin/python -m mushmallow <options> <path to file>`

Note that this tool is not available on PyPi at the time of writing.

### Development

Run `make check` to run full CI. Run `make check-<thing>` to run specific targets.
See the Makefile.

### Limitations

* I hacked this together to get it working for the schemas I need to transform.
* It is not exhaustively tested and there maybe cases that simply don't work
  (probably around the AST handling).
* Only tested against Python3.11.
* Identifies schema definitions based on sub-classes of classes suffixed with
  'Schema'.
