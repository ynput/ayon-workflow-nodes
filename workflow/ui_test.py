from typing import List
from ayon_workflow.plugin_system import (
    InputAttribute,
    WorkflowTaskNode,
)


class UITest(WorkflowTaskNode):
    """Shows all supported widgets for testing"""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="string",
            description="whatever",
        ),
        InputAttribute(
            name="filepath",
            description="whatever",
            widget={
                "name": "filepath",
            },
        ),
        InputAttribute(
            name="text",
            description="whatever",
            widget={
                "name": "text",
            },
        ),
        InputAttribute(
            name="choice",
            description="whatever",
            widget={
                "name": "choice",
                "options": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            },
        ),
        InputAttribute(
            name="bool",
            description="A binary choice",
        ),
        InputAttribute(
            name="int",
            description="whatever",
        ),
        InputAttribute(
            name="enum",
            description="whatever",
            widget={
                "name": "enum",
                "fields": ["do this", "do that", "have a break"],
            },
        ),
        InputAttribute(
            name="float",
            description="whatever",
        ),
        InputAttribute(
            name="string_array",
            description="whatever",
        ),
        InputAttribute(
            name="float_array",
            description="whatever",
        ),
        InputAttribute(
            name="int_array",
            description="whatever",
        ),
    ]
    outputs = []

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
