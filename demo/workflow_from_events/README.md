# Workflow-from-Events Examples

Example `Workflow` graphs (exported from the AYON Workflow web editor) showing
how to trigger a workflow automatically — from a cron schedule, an AYON
event, or a simple action — instead of running it manually.

## Examples

| File | Trigger node | What it does |
| --- | --- | --- |
| `trigger_from_cron.json` | `OnSchedule` (`*/1 * * * *`) | Runs every minute; dispatches a `NoOp` task to Deadline Thinkbox. |
| `trigger_from_version_created_event.json` | `OnVersionCreated` | Reacts to the `entity.version.created` AYON event, uses an `If` node to only continue for project `"Demo"`, dispatches to Deadline Thinkbox. |
| `trigger_from_simple_action_folder.json` | `OnActionFromFolder` | Reacts to a custom simple action registered on Folder entities. |
| `trigger_from_simple_action_version.json` | `OnActionFromVersion` | Reacts to a custom simple action registered on Version entities. |
| `on_task_assignees_changed_watch_parent_folder.json` | `OnTaskAssigneesChanged` | Reacts to `entity.task.assignees_changed` and adds the new assignees as watchers on the task's **parent folder** (`GetParentContext` → `SetEntityWatchers`). Runs locally, no farm dispatch. |

## 1. Load and register a workflow

1. Open the web editor (AYON tray → Workflow, or `$AYON_EXECUTABLE addon workflow editor`).
2. `File` → `Load`, pick one of the `.json` files in this folder.
3. `File` → register it, so it can be found by name when its trigger fires.

## 2. Wire up simple actions

`trigger_from_simple_action_folder.json` and `trigger_from_simple_action_version.json`
only fire once a matching simple action is enabled in `ayon-workflow`'s
settings (`ayon+settings://workflow/simple_actions`):

```json
{
  "simple_actions": [
    {
      "enabled": true,
      "local": true,
      "workflow_name": "SimpleActionWorkflowFolder",
      "label": "My custom Folder trigger",
      "input_entity": "Folder"
    }
  ]
}
```

- `workflow_name` must match the workflow's `name` field in the `.json`
  (e.g. `SimpleActionWorkflowFolder`, `SimpleActionWorkflowVersion`).
- `input_entity` must match the trigger node used: `"Folder"` for
  `OnActionFromFolder`, `"Version"` for `OnActionFromVersion`.
- `local: true` runs the workflow on your machine when the action is used;
  `local: false` dispatches it to the event processor instead.

`trigger_from_version_created_event.json` and
`on_task_assignees_changed_watch_parent_folder.json` need no extra
settings — they react to built-in AYON events directly.

## 3. Run the event processor

Cron triggers, AYON-event triggers, and non-local simple actions all need
`ayon-workflow`'s event processor running to actually be picked up and
dispatched — without it, a registered workflow just sits there.

```
$AYON_EXECUTABLE --use-dev event-processor
```

For a persistent/production deployment (e.g. on ASH), run the
`ayon-workflow-event-processor` service instead — see `ayon-workflow`'s own
deployment docs.

## 4. Verify it worked

- `trigger_from_cron.json` — executes on its own every minute.
- `trigger_from_version_created_event.json` — publish a new version in a
  project named `Demo` (other projects are filtered out by the `If` node).
- `trigger_from_simple_action_folder.json` / `_version.json` — trigger the
  registered simple action from a Folder/Version entity in AYON.
- `on_task_assignees_changed_watch_parent_folder.json` — change a task's
  assignees; they should appear as watchers on its parent folder.
