from typing import Any, Dict, Optional

import ayon_api
from taskflow.engines.action_engine import engine

from ayon_workflow.datatypes import Entity
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)

from . import _utils


TRUE = ("true", "yes", "on", "1")
FALSE = ("false", "no", "off", "0")


def _enum_value(attribute: str, value: Any, enum: list) -> Any:
    """ The enum value matching a value or a label, without case. """
    for item in enum:
        options = (item.get("value"), item.get("label"))
        if value in options or any(
            isinstance(option, str) and str(value).lower() == option.lower()
            for option in options
        ):
            return item.get("value")
    labels = ", ".join(
        str(item.get("label") or item.get("value")) for item in enum
    )
    raise ValueError(f"{attribute} takes one of {labels}, not {value!r}.")


def _as_list(value: Any) -> list:
    if isinstance(value, (list, tuple)):
        return list(value)
    if value is None or value == "":
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def convert_value(attribute: str, value: Any, schema: dict) -> Any:
    """ The value as the attribute type wants it: text from the editor
    becomes a number, yes/no or a list (comma separated).
    """
    attr_type = schema.get("type") or "string"
    enum = schema.get("enum") or []
    try:
        if attr_type == "integer":
            if isinstance(value, float) and not value.is_integer():
                raise ValueError
            converted = int(str(value).strip()) if isinstance(value, str) \
                else int(value)
        elif attr_type == "float":
            converted = float(value)
        elif attr_type == "boolean":
            if isinstance(value, bool):
                converted = value
            elif str(value).strip().lower() in TRUE:
                converted = True
            elif str(value).strip().lower() in FALSE:
                converted = False
            else:
                raise ValueError
        elif attr_type == "list_of_strings":
            converted = [str(item) for item in _as_list(value)]
        elif attr_type == "list_of_integers":
            converted = [int(item) for item in _as_list(value)]
        elif attr_type in ("string", "datetime"):
            converted = "" if value is None else str(value)
        else:
            # lists of anything, dicts: as given
            converted = value
    except (TypeError, ValueError):
        readable = {
            "integer": "a whole number",
            "float": "a number",
            "boolean": "yes or no",
            "list_of_integers": "whole numbers separated by commas",
        }.get(attr_type, attr_type)
        raise ValueError(
            f"{attribute} takes {readable}, not {value!r}."
        ) from None

    if enum:
        if isinstance(converted, list):
            return [_enum_value(attribute, item, enum) for item in converted]
        return _enum_value(attribute, converted, enum)
    return converted


class SetAttribute(WorkflowTaskNode):
    """Set an attribute of an AYON folder, task, product or version."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_entity",
            description="The folder, task, product or version to change.",
        ),
        InputAttribute(
            name="attribute",
            description="The attribute name, for example frameStart.",
            # editors can offer the attributes of the entity type
            widget={"name": "attribute"},
        ),
        InputAttribute(
            name="value",
            description=(
                "The new value. Text is converted to the type of the "
                "attribute: numbers, yes/no, lists separated by commas."
            ),
        ),
    ]
    outputs = [
        OutputAttribute(
            name="edited_entity",
            description="The entity with the attribute set.",
        )
    ]

    def execute(
        self,
        input_entity: Entity,
        attribute: str,
        value: Optional[Any] = None,
        _engine: Optional[engine.ActionEngine] = None,
    ) -> Entity:
        entity_type = getattr(input_entity, "entity_type", None)
        if not attribute:
            raise ValueError("No attribute to set.")
        schemas = ayon_api.get_attributes_for_type(entity_type) or {}
        if attribute not in schemas:
            raise ValueError(
                f"{attribute!r} is not a {entity_type} attribute. "
                f"Expected one of: {', '.join(sorted(schemas))}."
            )
        converted = convert_value(attribute, value, schemas[attribute])

        # kept to restore it if a later node fails
        data = _utils.get_entity_data(
            input_entity, fields={f"attrib.{attribute}"}
        )
        self.inject_custom_backend_data(
            _engine,
            previous=(data.get("attrib") or {}).get(attribute)
        )
        _utils.update_entity(input_entity, attrib={attribute: converted})
        return input_entity

    def revert_execute(
        self,
        input_entity: Entity,
        attribute: str,
        value: Optional[Any] = None,
        _custom_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        if "previous" in (_custom_data or {}):
            _utils.update_entity(
                input_entity, attrib={attribute: _custom_data["previous"]}
            )
