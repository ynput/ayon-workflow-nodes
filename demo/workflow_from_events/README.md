1. Open the web editor.
2. Load and upload some example workflows from this directory.
3. Add them as new registered workflows (this is done through the web-editor-> File menu)
4. Specific to `trigger_from_simple_action_folder`, define a new simple action that is enabled on Folder in the `ayon_workflow` settings `ayon+settings://workflow/simple_actions`.
   This should connect the registered workflow `trigger_from_simple_action_folder` to a simple action "My custom Folder trigger" available on folder entities.
```
{
  "simple_actions": [
    {
      "enabled": true,
      "local": true,
      "workflow_name": "SimpleActionWorkflowFolder",
      "label": "My custom Folder trigger",
      "input_entity": "Folder"
    }
  ],
}
```
5a. (locally) Run the processor through AYON launcher: `$AYON_EXECUTABLE --use-dev event-processor`
5b. (from ASH host)
    1. Log in to the private `harbor.ynput.team` (credentials to be provided by an admin)
    2. Pull the latest docker image from `harbor.ynput.team/services/ayon-workflow-event-processor`
    3. Register the service from ASH service page on the AYON server

6. Results:
    * Ensure the cron workflow is triggered on its own every minute.
    * Ensure the simple action workflow is triggered when the simple action is triggered and not local.
    * Ensure the simple action workflow is run locally when the simple action is triggered and local.
    * Ensure the workflow from version created event is triggered when a new version is created.
