# Node Authoring Guide

This guide explains how to implement a workflow node (a "plugin") for the AYON
Workflow addon, following the conventions used by the official nodes in this
repository. Code excerpts come from this repository's source, with file paths
so you can check the full implementation.

If you're writing custom nodes for your studio, keep them in your own
repository rather than here. The conventions below apply to them the same way.
For how to register them with the Workflow addon, and for complete example
modules, see
[Extending Workflow Nodes (Custom Plugins)](https://docs.ayon.dev/docs/dev_addon_workflow#extending-workflow-nodes-custom-plugins).

## Your first node

A node is a Python class. The Workflow addon reads it to build the node in the
editor and to run it: the docstring becomes the node's description, `inputs`
and `outputs` become its ports, and the `execute()` method does the work. The
type hints and defaults in the `execute()` signature define the node's inputs
and outputs: each input's type, editor widget, and default value, and the
type of each output.

**Where to put it.** Nodes are grouped by category under
[`workflow/`](../workflow/):

| Folder | Contents |
| --- | --- |
| `essentials/` | Generic utility nodes |
| `conditions/` | Branching nodes |
| `inputs/` | Trigger and input nodes (cron, AYON events, simple actions) |
| `applications/` | DCC integrations (Blender, Nuke) |
| `publish/` | Publishing nodes |

Create `workflow/<category>/<node_name>.py` in the category that fits, and add
a new category folder only if none does.

**Write the class.** Most nodes subclass `WorkflowTaskNode`. Here's a complete
one:

```python
from typing import Any, List, Union

from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)


class Append(WorkflowTaskNode):
    """Group or Append inputs as a list."""

    version = "0.0.1"

    inputs = [
        InputAttribute(
            name="inputs",
            description="Any input(s).",
            allow_multi_connection=True,
        )
    ]
    outputs = [
        OutputAttribute(name="appended_data", description="The appended data as a list.")
    ]

    def execute(self, inputs: Union[Any, List[Any]]) -> List[Any]:
        result = []
        for input in inputs:
            result.extend(input) if isinstance(input, list) else result.append(input)
        return result
```

Source: [`workflow/essentials/append.py`](../workflow/essentials/append.py)

Keep the docstring to a single, accurate sentence, since it's what users see
in the editor. Set `version` to a semver-like string and bump it on breaking
changes. To show a different node type name in the editor, set `name`; for
example, `VideoNode` sets `name = "Video"`.

**Register it.** The Workflow addon only knows about nodes returned by
`get_plugins()` in [`workflow/__init__.py`](../workflow/__init__.py). Import
your class there and add it to the list:

```python
def get_plugins(
    execution_scope: ExecutionScope = ExecutionScope.WORKSTATION,
) -> list[WorkflowNode]:
    from .essentials.append import Append
    nodes = [Append, ...]
    ...
    return nodes
```

Some nodes are only added in certain execution scopes. See
[Execution scope](#execution-scope) for when that applies.

**Run it.** Open the AYON Console from the AYON tray, then build and run a
small workflow around your node:

```python
from ayon_workflow.plugin_system import register_all_plugins
from ayon_workflow.workflow_editor import Workflow
from ayon_workflow.workflow_execution import execute_workflow

register_all_plugins()  # discovers get_plugins() from every source

workflow = Workflow(name="test_workflow")
node = workflow.execution_graph.create_node("Append")
node["inputs"] = ["hello", ["world", "!"]]

print(execute_workflow(workflow))
```

Then check it in the Workflow editor too: launch the editor from the AYON tray,
add your node to a graph, and confirm its description, ports, and widgets look
right. For longer walkthroughs, see [`demo/example.py`](../demo/example.py),
which covers connecting nodes, JSON serialization, and CLI execution.

## Inputs and outputs

**Inputs.** Each input is an `InputAttribute`, bound by name to an `execute()`
parameter, so the names must match exactly. Every parameter needs a type hint,
which also decides the default editor widget. Put default values in the
`execute()` signature (`text: str = "default"`), not on the `InputAttribute`.

```python
InputAttribute(
    name="input_text",              # matches an execute() parameter name
    description="Input text to process.",
    allow_multi_connection=False,   # True accepts several connections as a list (see Append)
    widget={                        # optional; controls the editor widget
        "name": "filepath",
        "select": "file",           # or "directory"
        "caption": "Select a file.",
        "filter": "Nuke Scene (*.nk)",  # optional file filter
    },
)
```

If `widget` is omitted or `{}`, the widget is inferred from the type hint.
Widget `name` values used in this repository are `filepath`, `text`
(multi-line), `choice` (fixed `options`), and `enum` (`fields`). For the full
set, see [`workflow/ui_test.py`](../workflow/ui_test.py).

**Outputs.** Each output is an `OutputAttribute`, and the return value of
`execute()` needs a type hint. For one output, return the value directly. For
several, return a `tuple` in the same order as `outputs`:

```python
outputs = [
    OutputAttribute(name="concatenated_text", description="..."),
    OutputAttribute(name="float_value", description="..."),
]

def execute(self, text1: str, text2: str) -> tuple[str, float]:
    return f"{text1}{text2}", 1.0   # order matches `outputs`
```

For a real example, see
[`OnVersionCreated.execute`](../workflow/inputs/events/entity_version_created.py),
which returns `Tuple[Optional[FolderItem], Optional[VersionItem]]`.

**Data types.** Type hints can use built-in Python types (`str`, `int`,
`float`, and so on) and the types in `ayon_workflow.datatypes`. For structured
data passed between nodes, use the `ayon_workflow.datatypes` types instead of
ad-hoc dicts (such as recreating `FrameRange` as
`{"first_frame": 1001, "last_frame": 1100}`), so the editor and other nodes
know what the data is.

| Type | Purpose |
| --- | --- |
| `Entity` | Base class for AYON entities, with an id, project, and entity type. |
| `ContextItem` | An AYON context, either a `ProjectItem`, a `FolderItem`, or a `TaskItem`. |
| `ProjectItem` | An AYON project context: project name. |
| `FolderItem` | An AYON folder entity: project name, and the folder's name, type, path, and id. |
| `TaskItem` | An AYON task entity: project name, the parent folder's name, type, path, and id, and the task's name, type, and id. |
| `ProductItem` | An AYON product entity: project name and product id. |
| `VersionItem` | An AYON version entity: project name, product id, and version id or number. |
| `FrameRange` | A frame range: `first_frame`, `last_frame`, `step`. |
| `ImageSequence` | An image sequence: `directory`, `head`, `tail`, `padding`, `frame_range`. |
| `Video` | A video file: `path`, `frame_range`. |
| `MediaType` | A media input, either an `ImageSequence` or a `Video`. |
| `RepresentationItem` | A representation to be published. |
| `PublishInput` | A publishing payload, either a `str`, a `MediaType`, or a `RepresentationItem`. |

## Paths and cleanup

**Cross-platform paths.** A workflow can be built on one OS and run on
another, for example on a Windows workstation and then a Linux farm node, so
paths are passed between nodes as rootless paths like
`{root[work]}/to/a/file.ext`. Resolve a path input with `remap_input()` before
using it, but return or forward the original rootless path, so the next node
can resolve it on its own machine.

**Reverting execution.** If a downstream node fails, the execution engine
calls `revert_execute()` on nodes that already ran, with the same arguments as
`execute()`. Implement it for any side effect that should be undone, such as
creating files, calling external APIs, or submitting to the farm.

This example shows both. Note that `revert_execute()` remaps the path too:

```python
import os

from ayon_workflow.datatypes import ContextItem
from ayon_workflow.utils import remap_input

def execute(self, context: ContextItem, file_path: str, content: str = "") -> str:
    remapped_path = remap_input(file_path, context.project_name)
    with open(remapped_path, "w") as f:
        f.write(content)
    return file_path  # the rootless path, not remapped_path

def revert_execute(self, context: ContextItem, file_path: str, content: str = ""):
    remapped_path = remap_input(file_path, context.project_name)
    if os.path.exists(remapped_path):
        os.remove(remapped_path)
```

**What `revert_execute()` receives.** The engine always gives it
`flow_failures`, the failures that triggered the revert, so it must declare
`flow_failures` or accept `**kwargs`. It also gives it `result` and
`_custom_data` when it declares them or accepts `**kwargs`, so a
`revert_execute()` that takes neither still works. Positional-only parameters
(`def revert_execute(self, result, /)`) are refused when the node class is
defined, the engine only gives keyword arguments.

**Using the result of `execute()`.** What `execute()` returned is given to
`revert_execute()` as `result`, so a node that creates something can delete it
without keeping anything else:

```python
def execute(self, folder: FolderItem, task_name: str) -> str:
    return create_task(folder, task_name)  # the id of the new task

def revert_execute(self, folder: FolderItem, task_name: str, **kwargs):
    task_id = kwargs.get("result")
    if isinstance(task_id, str):
        delete_task(folder, task_id)
```

- With several outputs, `result` is the tuple `execute()` returned.
- If `execute()` itself failed, the node is reverted too and `result` is a
  taskflow `Failure`, not a value: check its type before using it.

**Keeping custom data for the revert.** `revert_execute()` often needs more than
the result, like the previous status of what `execute()` changed. Store it with
`inject_custom_backend_data()` and read it back from `_custom_data`:

```python
def execute(self, task: TaskItem, status: str, _engine=None) -> TaskItem:
    self.inject_custom_backend_data(_engine, previous_status=get_status(task))
    set_status(task, status)
    return task

def revert_execute(self, task: TaskItem, status: str, _custom_data=None, **kwargs):
    previous = _custom_data.get("previous_status")
    if previous:
        set_status(task, previous)
```

- Declare `_engine=None` in `execute()`, the engine passes it. It is `None` when
  a node is called outside an engine, which `inject_custom_backend_data()` does
  not accept.
- The data must be serializable (strings, numbers, booleans, lists, dicts). It
  is saved in the workflow backend, so the revert gets it even when it runs in
  another process or machine.
- It is not an output of the node: nothing connects to it and the editor does
  not show it.
- Every call adds to the previous ones, the same key is replaced, and the data
  starts empty at each `execute()`.
- `_custom_data` is `{}` when nothing was stored.
- Do not keep this data on `self`: an attribute is lost when the revert runs in
  another process.

No node in this repository overrides `revert_execute()` yet, so this snippet is
illustrative. For a runnable demo of a failing workflow that triggers a
revert, see [`demo/example_revert.py`](../demo/example_revert.py). For the full
path-remapping pattern, including subprocesses and log streaming, see
[`workflow/applications/_base.py`](../workflow/applications/_base.py) and
[`workflow/applications/nuke.py`](../workflow/applications/nuke.py).

## Trigger and condition nodes

Most nodes subclass `WorkflowTaskNode`, but two kinds of nodes use a
different base class.

**Trigger nodes** start event-triggered workflows and have no required
upstream input. They derive from `WorkflowInputTaskNode`, usually through one
of the two base triggers in this repository:

- [`EventTrigger`](../workflow/inputs/events/base.py) reacts to an AYON event.
  Create one node per kind of event you want to handle.
- [`OnSchedule`](../workflow/inputs/cron.py) runs on a cron schedule. It only
  validates the cron expression; the Workflow addon handles the scheduling.

A concrete event trigger overrides the class method `get_event_topics()` and
`execute()`. `get_event_topics()` returns the list of event topics that start
the workflow. It gets the values set on the node, so the topics can depend on
them. It must return a `list` of strings: the base class returns an empty list,
and anything else is refused, so the workflow is not registered for events.
`execute()` calls `super().execute()` to fetch the raw event, then shapes it
into typed outputs:

```python
class OnTaskAssigneesChanged(EventTrigger):
    version = "0.0.1"
    outputs = [
        OutputAttribute(name="event_context", description="..."),
        OutputAttribute(name="event_assignees", description="..."),
    ]

    @classmethod
    def get_event_topics(cls, execute_values: Dict[str, Any]) -> List[str]:
        return ["entity.task.assignees_changed"]

    def execute(
        self, event_id: Optional[str] = None
    ) -> Tuple[Optional[TaskItem], Optional[List[str]]]:
        if event_id is None:
            return None, None
        event_data = super().execute(event_id)
        # ... resolve typed objects from event_data ...
        return task_item, event_data["summary"]["value"]
```

When the workflow runs outside an actual event, such as from the editor,
`event_id` is `None`, so `execute()` must return `None` or empty outputs in
that case. For well-known event topics, see the
[AYON Event Viewer article](https://help.ayon.app/en/help/articles/2566382-ayon-event-viewer#e4bo4xwd0ei).
For an `OnSchedule` subclass example, see
[Reference: creating your own EventTrigger or OnSchedule input node](https://docs.ayon.dev/docs/dev_addon_workflow_event#reference-creating-your-own-eventtrigger-or-onschedule-input-node).

**Condition nodes** have several mutually exclusive outputs, where only one
branch continues downstream. They derive from `WorkflowConditionTaskNode`,
declare branches with `ConditionOutputAttribute`, and call
`self.skip_output(...)` on the branch that must not run:

```python
class If(WorkflowConditionTaskNode):
    version = "0.0.1"
    inputs = [
        InputAttribute(name="input_data", description="The input data."),
        InputAttribute(name="condition", description="..."),
    ]
    outputs = [
        ConditionOutputAttribute(name="on_True", description="input_data when condition is True"),
        ConditionOutputAttribute(name="on_False", description="input_data when condition is False"),
    ]

    def execute(
        self, input_data: Any, condition: Union[bool, str, None] = None,
        _engine=None, _backend_directory=None, _main_flow_id=None,
    ) -> Tuple[Any, Any]:
        if self.evaluate_condition(condition, input_data=input_data):
            ignored_output, result = "on_False", (input_data, None)
        else:
            ignored_output, result = "on_True", (None, input_data)
        self.skip_output(
            output_name=ignored_output,
            _engine=_engine, _backend_directory=_backend_directory, _main_flow_id=_main_flow_id,
        )
        return result
```

Source: [`workflow/conditions/branch.py`](../workflow/conditions/branch.py)

The execution engine injects `_engine`, `_backend_directory`, and
`_main_flow_id` when they appear in the signature. Only nodes that need engine
internals, such as `skip_output()`, should declare them.

## Execution scope

`get_plugins()` receives the execution scope it's being called for, so a node
can be registered only where it can actually run:

```python
def get_plugins(
    execution_scope: ExecutionScope = ExecutionScope.WORKSTATION,
) -> list[WorkflowNode]:
    from .essentials.append import Append
    # Available in every scope: ExecutionScope.SERVER and ExecutionScope.WORKSTATION.
    nodes = [Append, ...]
    if execution_scope == ExecutionScope.WORKSTATION:
        # Added only for ExecutionScope.WORKSTATION: pipeline tools such as
        # DCC and publish nodes.
        from .publish.publish import Publish
        nodes.append(Publish)
    return nodes
```

By default, add nodes outside the `if` block, so they're available in every
scope. Add a node inside the `ExecutionScope.WORKSTATION` block only if it
needs a local, interactive environment: a DCC application, a display,
publishing, or production storage. To see which official nodes are available
in each scope, check `get_plugins()` in
[`workflow/__init__.py`](../workflow/__init__.py).

For event-triggered workflows, the scope depends on how the event processor is
run:

- **As an AYON service**, spawned from the Services page, it runs in
  `ExecutionScope.SERVER`, so `WORKSTATION`-only nodes aren't available.
- **Through the AYON launcher CLI**, it runs in `ExecutionScope.WORKSTATION`,
  so all nodes are available.

For both options, see
[Run Event Processor Service](https://help.ayon.app/en/help/articles/0480584-configure-workflow-addon).

## Checklist

Before considering a new or changed node done:

- [ ] The class docstring is a single, accurate sentence.
- [ ] `version` is set, semver-like, and bumped on breaking changes.
- [ ] Every `execute()` parameter name matches an `InputAttribute.name`.
- [ ] Every `execute()` parameter and the return value are type-hinted.
- [ ] Defaults are in the `execute()` signature. `default=` is NEVER passed to `InputAttribute`.
- [ ] Multiple return values are a `tuple`, in the same order as `outputs`.
- [ ] Structured data between nodes uses `ayon_workflow.datatypes` types, not ad-hoc dicts.
- [ ] Path inputs go through `remap_input()`, and the original rootless path is returned.
- [ ] Side effects (files, external APIs, farm submissions) have a matching `revert_execute()`.
- [ ] Data needed by `revert_execute()` is stored with `inject_custom_backend_data()`, not on `self`.
- [ ] Trigger nodes handle `event_id=None`.
- [ ] Engine parameters (`_engine`, `_backend_directory`, `_main_flow_id`) are declared only when needed.
- [ ] The node is in `get_plugins()`, gated behind `ExecutionScope.WORKSTATION` only if needed.
- [ ] The node runs in the AYON Console and looks right in the Workflow editor.