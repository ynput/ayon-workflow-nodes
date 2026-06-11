from typing import List
from ayon_workflow.plugin_system.interface import WorkflowNode


class UITest(WorkflowNode):
    """Shows all supported widgets for testing"""

    version = "0.0.1"
    inputs = {
        "string": {
            "description": "whatever",
        },
        "filepath": {
            "description": "whatever",
            "widget": {
                "name": "filepath",
            },
        },
        "text": {
            "description": "whatever",
            "widget": {
                "name": "text",
            },
        },
        "choice": {
            "description": "whatever",
            "widget": {
                "name": "choice",
                "options": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            },
        },
        "bool": {
            "description": "A binary choice",
        },
        "int": {
            "description": "whatever",
        },
        "enum": {
            "description": "whatever",
            "widget": {
                "name": "enum",
                "fields": ["do this", "do that", "have a break"],
            },
        },
        "float": {
            "description": "whatever",
        },
        "string_array": {
            "description": "whatever",
        },
        "float_array": {
            "description": "whatever",
        },
        "int_array": {
            "description": "whatever",
        },
    }
    outputs = {}

    def execute(
        self,
        string: str = "some string data",
        filepath: str = "/foo/bar.txt",
        text: str = "Enter longer text with line breaks.",
        choice: str = "/foo/bar.txt",
        bool: bool = True,
        int: int = 42,
        enum: int = 1,
        float: float = 1.234567,
        string_array: List[str] = ["foo", "bar", "baz"],
        float_array: List[float] = [],
        int_array: List[int] = [],
    ):
        """ Do nothing, UI/UX dev only.
        """
        pass
