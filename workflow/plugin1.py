from typing import Optional

import os
import random
import tempfile
import shutil


def do_stuff():
    return random.randint(1, 100)


def pass_through(input):
    return input


def print_stuff(input_str: str, template: Optional[str] = None):
    if template is None:
        print(input_str)
    else:
        print(template.format(input_str=input_str) )


def concatenate_as_string(
        input_A: str,
        input_B: str = "",
        input_C: str = ""
    ) -> str:
    return f"{input_A}+{input_B}+{input_C}"


def raise_exception(message: Optional[object] = None):
    raise Exception(str(message) if message else "")


def write_to_file(
        content: object,
        filepath: Optional[str] = None,
        directory: Optional[str] = None,
    ) -> str:

    if filepath is None:
        directory = directory or tempfile.mkdtemp()
        filepath = tempfile.NamedTemporaryFile(dir=directory).name

    with open(filepath, "w", encoding="utf-8") as file_handler:
        file_handler.write(str(content))

    return filepath


def delete_file(file_path: str):
        os.remove(file_path)


def revert_write_to_file(
        result: object, # result return from write_to_file
        content: str,
        filepath: Optional[str] = None,
        directory: Optional[str] = None,
        flow_failures: Optional[object] = None
    ):
    """ Revert a write_to_file execution.
    """
    # Directory was not explicitely provided
    # delete it and its content.
    if directory is None and os.path.exists(result):
        directory = os.path.dirname(result)
        shutil.rmtree(directory)

    # A file was created properly, delete it.
    elif os.path.exists(result):
        delete_file(result)

    # No file was created,
    # error come from this writing to file.
    else:
        print(result.exception_str)
