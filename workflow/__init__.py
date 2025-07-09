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
                },
                {
                    "name": "template",
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
        {
            "name": "Write to File",
            "description": "Concatenate 2 strings",
            "version": __version__,
            "inputs": [
                {
                    "name": "content",
                    "description": "whatever",
                    "type": object,
                },
                {
                    "name": "filepath",
                    "description": "whatever",
                    "type": str,
                },
                {
                    "name": "directory",
                    "description": "whatever",
                    "type": str,
                },
            ],
            "outputs": [
                {
                    "name": "filepath",
                    "type": object,
                }
            ],
        },
        {
            "name": "Fail",
            "description": "Raise an exception",
            "version": __version__,
            "inputs": [
                {
                    "name": "message",
                    "description": "whatever",
                    "type": object,
                },
            ],
            "outputs": [],
        },
        {
            "name": "NukeRender",
            "description": "Perform a render through Nuke.",
            "version": __version__,
            "inputs": [
                {
                    "name": "folder",
                    "description": "The folder associated to the Render.",
                    "type": object,
                },
                {
                    "name": "nuke_script_path",
                    "description": "The path to the Nuke script.",
                    "type": str,
                },
                {
                    "name": "input_media",
                    "description": "The input media",
                    "type": object,
                },
                {
                    "name": "output_media",
                    "description": "The output media",
                    "type": object,
                },
                {
                    "name": "python_script_path",
                    "description": "The path to a python script.",
                    "type": str,
                },
                {
                    "name": "frame_range",
                    "description": "Restrictive frame range.",
                    "type": object,
                },
                {
                    "name": "read_node_name",
                    "description": "Explicit a Read node to use.",
                    "type": str,
                },
                {
                    "name": "write_node_name",
                    "description": "Explicit a Write node to use.",
                    "type": str,
                },
                {
                    "name": "nuke_application_variant",
                    "description": "An application variant to use.",
                    "type": str,
                }
            ],
            "outputs": [
                {
                    "name": "filepath",
                    "type": object,
                }
            ],
        },
    ]


def get_plugin_function(name):
    from . import plugin1
    from .applications import nuke

    if name == "Random Number":
        return plugin1.do_stuff

    elif name == "NoOp":
        return plugin1.pass_through

    elif name == "Print":
        return plugin1.print_stuff

    elif name == "Concatenate String":
        return plugin1.concatenate_as_string

    elif name == "Write to File":
        return plugin1.write_to_file

    elif name == "Fail":
        return plugin1.raise_exception

    elif name == "NukeRender":
        return nuke.run_nuke_render

    return None


def get_plugin_revert_function(name):
    from . import plugin1

    if name == "Write to File":
        return plugin1.revert_write_to_file

    return None
