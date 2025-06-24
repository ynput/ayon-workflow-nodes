import random


def do_stuff():
    return random.randint(1, 100)


def pass_through(input):
    return input


def print_stuff(input_str: str):
    print(input_str)


def concatenate_as_string(
        input_A: str,
        input_B: str = "",
        input_C: str = ""
    ) -> str:
    return f"{input_A}+{input_B}+{input_C}"
