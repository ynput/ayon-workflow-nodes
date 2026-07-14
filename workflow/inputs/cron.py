from typing import Any

import croniter

from ayon_workflow.plugin_system import (
    InputAttribute,
    WorkflowInputTaskNode,
)


class Cron(WorkflowInputTaskNode):
    """A cron trigger input node."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="cron_expression",
            description="The cron expression.",
        )
    ]
    outputs = []

    def execute(self, cron_expression: str) -> Any:
        """ Validate the cron expression.
        """
        if not croniter.is_valid(cron_expression, strict=True):
            raise ValueError(
                f"Invalid cron expression: {cron_expression}"
            )
