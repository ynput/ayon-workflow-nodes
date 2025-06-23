"""
This should be as simple as possible to avoid import errors.
"""

__version__ = "1.3.0"


def get_plugins():
    return [
        {
            "name": "Random Number",
            "description": "Return a random number between 1 and 100",
            "version": __version__,
            "inputs": [],
            "outputs": [
                {
                    "name": "result",
                    "description": "A random [1:100] integer",
                    "type": int,
                }
            ],
        },
        {
            "name": "NoOp",
            "description": "Return input (pass-through does nothing)",
            "version": __version__,
            "inputs": [
                {
                    "name": "input",
                    "description": "whatever",
                    "type": object,
                }
            ],
            "outputs": [
                {
                    "name": "untouched_input",
                    "type": object,
                }
            ],
        },
        {
            "name": "Print",
            "description": "Print stuff",
            "version": __version__,
            "inputs": [
                {
                    "name": "input_str",
                    "description": "whatever",
                    "type": str,
                }
            ],
            "outputs": [],
        },
        {
            "name": "Concatenate String",
            "description": "Concatenate 2 strings",
            "version": __version__,
            "inputs": [
                {
                    "name": "input_A",
                    "description": "whatever",
                    "type": str,
                },
                {
                    "name": "input_B",
                    "description": "whatever",
                    "type": str,
                },
                {
                    "name": "input_C",
                    "description": "whatever",
                    "type": str,
                },
            ],
            "outputs": [],
        },
    ]


def get_plugin_function(name):
    from . import plugin1

    if name == "Random Number":
        return plugin1.do_stuff

    elif name == "NoOp":
        return plugin1.pass_through

    elif name == "Print":
        return plugin1.print_stuff

    elif name == "Concatenate String":
        return plugin1.concatenate_as_string

    return None
