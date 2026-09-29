# Event-Triggered Workflow Examples

Example workflow graphs that show how to use the AYON Workflow addon for
automations: running a workflow when an event occurs or on a schedule, or
providing it as an action users can trigger on demand from the AYON web UI.

The same examples ship with the Workflow addon under
`ayon_workflow/demo/workflow_from_events/`.

## Requirements

- **Workflow addon service:** The Workflow addon service must be running on
  your AYON server, since it picks up registered workflows and runs them when
  their trigger fires. See
  [Configure Workflow Addon](https://help.ayon.app/en/help/articles/0480584-configure-workflow-addon).
- **Deadline:** All examples except
  `on_task_assignees_changed_watch_parent_folder.json` dispatch their work to
  Deadline Thinkbox, so they need a working Deadline setup to see a result. See
  [Configure Deadline Addon](https://help.ayon.app/en/help/articles/5372986-configure-deadline-addon).

## Examples

| File | Trigger node | What it does |
| --- | --- | --- |
| `on_task_assignees_changed_watch_parent_folder.json` | `OnTaskAssigneesChanged` | Runs when assignees change on any task (`entity.task.assignees_changed`) and adds the new assignees as watchers on the task's parent folder (`GetParentContext` → `SetEntityWatchers`). Runs without farm dispatch. |
| `trigger_from_version_created_event.json` | `OnVersionCreated` | Runs when a new version is created (`entity.version.created`). Uses an `If` node so it only continues for versions in the `Demo` project, then dispatches to Deadline. |
| `trigger_from_cron.json` | `OnSchedule` (cron: `*/1 * * * *`) | Runs every minute and dispatches a `NoOp` task to Deadline. |
| `trigger_from_simple_action_folder.json` | `OnActionFromFolder` | Runs from a custom action in the folder action menu and dispatches a `NoOp` task to Deadline. |
| `trigger_from_simple_action_version.json` | `OnActionFromVersion` | Runs from a custom action in the version action menu and dispatches a `NoOp` task to Deadline. |

## Using the Examples

Every example follows the same two steps:

1. **Load it.** In the Workflow editor, go to `File > Load...` and select the
   example's `.json` file.
2. **Register it.** Go to `File > Registered Workflows > Register Current Workflow...`
   and give the workflow a name. From then on, the Workflow addon service runs
   it whenever its trigger fires.

The two simple action examples need one more step so the action appears in
the web UI:

3. **Add the action in settings.** Open the Workflow addon settings,
   `ayon+settings://workflow/simple_actions/from_folder` or
   `ayon+settings://workflow/simple_actions/from_version`. Add an entry with an
   action label and your registered workflow's name, then enable the entry,
   since new entries are disabled by default. The **Execute Locally** option
   controls where the workflow runs: enabled, it runs through the AYON launcher
   on the user's machine; disabled, it's handed to the Workflow addon service.

For the full walkthrough, including how to test each example and what result
to expect, see
[Workflows & Automations](https://help.ayon.app/en/help/articles/1804107-workflows-and-automations).

## Further Reading

- [Event-triggered workflows dev docs](https://docs.ayon.dev/docs/dev_addon_workflow_event): how event-triggered workflows work under the hood
- [Creating your own EventTrigger or OnSchedule input node](https://docs.ayon.dev/docs/dev_addon_workflow_event#reference-creating-your-own-eventtrigger-or-onschedule-input-node): react to event topics not covered by the built-in trigger nodes