# Node Authoring Guide

How to write a workflow node (a "plugin") for `ayon-workflow`, using the API
this repo's nodes are built on. Applies to nodes in this repo and to custom
nodes exposed by other AYON addons. Every claim below is grounded in this
repo's own source — file paths are given so it can be verified/extended
directly.

## Contents

- [Add a node in 5 steps](#add-a-node-in-5-steps)
- [1. Discovery](#1-discovery)
- [2. Choosing a base class](#2-choosing-a-base-class)
- [3. Minimal node template](#3-minimal-node-template)
- [4. Authoring rules](#4-authoring-rules)
- [5. Inputs and outputs](#5-inputs-and-outputs)
- [6. Multiple outputs](#6-multiple-outputs)
- [7. Input / trigger nodes](#7-input--trigger-nodes)
- [8. Condition nodes (branching)](#8-condition-nodes-branching)
- [9. Cross-platform paths](#9-cross-platform-paths)
- [10. Revert logic](#10-revert-logic)
- [11. AYON datatypes](#11-ayon-datatypes)
- [12. Testing locally](#12-testing-locally)
- [Self-check before finishing](#self-check-before-finishing)

## Add a node in 5 steps

1. Pick the sub-package: `essentials/`, `applications/`, `inputs/`,
   `conditions/`, `publish/` — or create a new one.
2. Create `workflow/<sub-package>/<node_name>.py` and subclass the base
   class picked in [§2](#2-choosing-a-base-class).
3. Implement `execute()` (and `revert_execute()` if the node has a side
   effect, [§10](#10-revert-logic)).
4. Import the class and append it to the list returned by `get_plugins()`
   in [`workflow/__init__.py`](../workflow/__init__.py) — only inside the
   `ExecutionScope.WORKSTATION` branch if the node needs a local/
   interactive environment ([§1](#1-discovery)).
5. Run the [self-check](#self-check-before-finishing) before considering
   the node done.

## 1. Discovery

A package exposes nodes via a `get_plugins()` function. In this repo:
[`workflow/__init__.py`](../workflow/__init__.py)

```python
from ayon_workflow.plugin_system import WorkflowNode, ExecutionScope

def get_plugins(
    execution_scope: ExecutionScope = ExecutionScope.WORKSTATION,
) -> list[WorkflowNode]:
    from .essentials.append import Append
    nodes = [Append, ...]
    if execution_scope == ExecutionScope.WORKSTATION:
        # Needs a local/interactive environment: DCC, publish, local disk.
        from .publish.publish import Publish
        nodes.append(Publish)
    return nodes
```

- MUST be added to the list returned by `get_plugins()` to be discoverable.
- MUST only be gated behind `ExecutionScope.WORKSTATION` if it needs a
  local app/display/production disk access. Default: scope-agnostic.
- A third-party addon follows the same contract: expose `get_plugins()`
  from a discoverable module; `ayon-workflow`'s plugin discovery picks it
  up automatically.

## 2. Choosing a base class

All base classes are imported from `ayon_workflow.plugin_system` and
subclass `WorkflowNode`. Pick one:

- Node has **no required upstream input** — it's an entry point (cron,
  AYON event, ...) → **`WorkflowInputTaskNode`**
  (see `OnSchedule`, `EventTrigger`).
- Node exposes **multiple mutually-exclusive outputs** and only one branch
  should continue downstream → **`WorkflowConditionTaskNode`**
  (see `If`).
- Anything else (an input/inputs in, an output/outputs out) →
  **`WorkflowTaskNode`**. This covers most nodes (see `Append`).

## 3. Minimal node template

```python
from typing import Any, List, Union

from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)


class Append(WorkflowTaskNode):
    """Group or Append inputs as a list."""     # -> node description in the editor

    version = "0.0.1"                            # required, semver-like

    inputs = [
        InputAttribute(
            name="inputs",                        # must match an execute() param name
            description="Any input(s).",
            allow_multi_connection=True,           # accepts several incoming connections
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

## 4. Authoring rules

| # | Rule |
| --- | --- |
| 1 | `version` MUST be set and semver-like (`"0.0.1"`). Bump it on any breaking change. |
| 2 | `execute()` parameter names MUST exactly match `inputs[].name` — binding is by name. |
| 3 | Every `execute()` parameter and the return value MUST be type-hinted. Types drive the editor's widgets; there is no separate schema. |
| 4 | Default values MUST live in the `execute()` signature (`text: str = "default"`). NEVER set a default on `InputAttribute`. |
| 5 | The class docstring MUST be a single, accurate sentence — it becomes the node's description in the editor. |
| 6 | Optional: set `name = "..."` to override the node type name shown in the editor (see `VideoNode.name = "Video"`). |
| 7 | Multiple return values MUST be returned as a `tuple`, in the same order as `outputs`. |
| 8 | File-path inputs MUST be resolved with `remap_input()` before use ([§9](#9-cross-platform-paths)). Return/forward the original rootless path — NEVER the resolved absolute one. |
| 9 | Side effects that need cleanup MUST implement `revert_execute()` ([§10](#10-revert-logic)). |
| 10 | Prefer `ayon_workflow.datatypes` objects over ad-hoc dicts for structured data crossing node boundaries. |

## 5. Inputs and outputs

```python
InputAttribute(
    name="input_text",              # required, matches execute() param
    description="Input text to process.",
    allow_multi_connection=False,   # True = accepts a list of connections, see Append
    widget={                        # optional, controls the editor widget
        "name": "filepath",
        "select": "file",           # or "directory"
        "caption": "Select a file.",
        "filter": "Nuke Scene (*.nk)",  # optional file filter
    },
)
```

Widget `name` values seen in this repo (default inferred from the type hint
if `widget={}`): `filepath`, `text` (multi-line), `choice` (fixed
`options`), `enum` (`fields`). Full palette:
[`workflow/ui_test.py`](../workflow/ui_test.py).

## 6. Multiple outputs

```python
outputs = [
    OutputAttribute(name="concatenated_text", description="..."),
    OutputAttribute(name="float_value", description="..."),
]

def execute(self, text1: str, text2: str) -> tuple[str, float]:
    return f"{text1}{text2}", 1.0   # tuple order must match `outputs` order
```
Real example: [`OnVersionCreated.execute`](../workflow/inputs/events/entity_version_created.py)
returns `Tuple[Optional[FolderItem], Optional[VersionItem]]`.

## 7. Input / trigger nodes

Derive from `WorkflowInputTaskNode`. Event-based triggers share
[`EventTrigger`](../workflow/inputs/events/base.py):

```python
class EventTrigger(WorkflowInputTaskNode):
    version = "0.0.1"
    event_topic: Union[str, List[str], None] = None   # AYON event topic(s)
    inputs = [InputAttribute(name="event_id", description="The id of the event to inject.")]

    def execute(self, event_id: Optional[str] = None) -> Dict[str, Any]:
        if event_id is None:
            return {}
        return ayon_api.get_event(event_id)
```

A concrete trigger sets `event_topic` (string or list of topics) and
overrides `execute()`, calling `super().execute()` to fetch the raw event
then shaping it into typed outputs:

```python
class OnTaskAssigneesChanged(EventTrigger):
    version = "0.0.1"
    event_topic = "entity.task.assignees_changed"
    outputs = [
        OutputAttribute(name="event_context", description="..."),
        OutputAttribute(name="event_assignees", description="..."),
    ]

    def execute(self, event_id: Optional[str] = None) -> Tuple[Optional[TaskItem], Optional[List[str]]]:
        if event_id is None:
            return None, None
        event_data = super().execute(event_id)
        # ... resolve typed objects from event_data ...
        return task_item, event_data["summary"]["value"]
```

- `execute()` MUST degrade gracefully (`None`/empty outputs) when called
  with `event_id=None` — that happens outside of an actual event run.
- Non-event trigger example: [`OnSchedule`](../workflow/inputs/cron.py)
  only validates the cron expression; scheduling itself is handled by
  `ayon-workflow`.

## 8. Condition nodes (branching)

Derive from `WorkflowConditionTaskNode`, use `ConditionOutputAttribute` for
branch outputs, call `self.skip_output(...)` on the branch that must not
run downstream:

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

`_engine` / `_backend_directory` / `_main_flow_id` are injected by the
execution engine when present in the signature — only needed by nodes that
must reach engine internals (e.g. `skip_output`); ordinary nodes NEVER
declare them.

## 9. Cross-platform paths

File-path inputs MUST be resolved at execution time with `remap_input`;
return the original rootless path so the next node (possibly on another
OS) can resolve it itself:

```python
from ayon_workflow.utils import remap_input

def execute(self, context: ContextItem, file_path: str) -> str:
    remapped_path = remap_input(file_path, context.project_name)
    with open(remapped_path, "w") as f:
        ...
    return file_path  # not remapped_path
```
Full pattern (subprocess + log streaming) in
[`workflow/applications/_base.py`](../workflow/applications/_base.py) and
[`workflow/applications/nuke.py`](../workflow/applications/nuke.py).

## 10. Revert logic

Optional `revert_execute()` on `WorkflowTaskNode`, called by the execution
engine to undo a node's side effect if a downstream node fails. Same
parameters as `execute()`:

```python
def execute(self, file_path: str, content: str) -> str:
    with open(file_path, "w") as f:
        f.write(content)
    return file_path

def revert_execute(self, file_path: str, content: str):
    if os.path.exists(file_path):
        os.remove(file_path)
```

> No node currently in this repo overrides `revert_execute` — this snippet
> is illustrative. Add one for any side effect (file creation, external
> API call, farm submission) that should be undone on failure.

## 11. AYON datatypes

Use `ayon_workflow.datatypes` objects in `execute()` type hints instead of
raw dicts/strings, so the editor and other nodes understand the data:

| Type | Purpose |
| --- | --- |
| `ContextItem` / `ProjectItem` / `FolderItem` / `TaskItem` | AYON context |
| `Entity` | Base class for anything with id/project/entity type |
| `FrameRange` | `first_frame`, `last_frame`, `step` |
| `ImageSequence` | `directory`, `head`, `tail`, `padding`, `frame_range` |
| `Video` | `path`, `frame_range` |
| `ProductItem` / `VersionItem` / `RepresentationItem` / `PublishInput` | Publishing payloads |

## 12. Testing locally

Requires `ayon-workflow` installed/importable:

```python
from ayon_workflow.plugin_system import register_all_plugins
from ayon_workflow.workflow_editor import Workflow
from ayon_workflow.workflow_execution import execute_workflow

register_all_plugins()
workflow = Workflow(name="test_workflow")
node = workflow.execution_graph.create_node("Append")
node["inputs"] = ["hello", ["world", "!"]]
print(execute_workflow(workflow))
```
Longer walkthroughs: [`demo/example.py`](../demo/example.py) (connect
nodes, serialize to/from JSON, execute via CLI),
[`demo/example_revert.py`](../demo/example_revert.py) (failing workflow
triggers a revert).

## Self-check before finishing

Run through this before considering a new/changed node done:

- [ ] `version` is set and semver-like.
- [ ] Every `execute()` parameter name matches an `InputAttribute.name`.
- [ ] Every `execute()` parameter and the return value are type-hinted.
- [ ] No `default=` is passed to `InputAttribute` — defaults are in `execute()`.
- [ ] The class docstring is a single, accurate sentence.
- [ ] If `execute()` returns multiple values, they are a `tuple` in the
      same order as `outputs`.
- [ ] Any file-path input goes through `remap_input()` before use, and the
      original rootless path is returned/forwarded, not the resolved one.
- [ ] Any side effect (file, external API, farm submission) has a matching
      `revert_execute()`.
- [ ] The node class is imported and appended in `get_plugins()`
      ([`workflow/__init__.py`](../workflow/__init__.py)), gated behind
      `ExecutionScope.WORKSTATION` only if it needs a local/interactive
      environment.
- [ ] Structured data crossing node boundaries uses `ayon_workflow.datatypes`
      types, not ad-hoc dicts.
