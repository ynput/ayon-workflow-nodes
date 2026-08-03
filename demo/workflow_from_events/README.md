0. Upload the content of this directory as new registered workflows
```python
import os

import ayon_api

# Delete a registered workflow
res = ayon_api.delete("addons/workflow/{addon_version}/registered_workflows/toto")
print(resp.text)

# List registered workflow
resp = ayon_api.get("addons/workflow/{addon_version}/registered_workflows")
print(resp.text)


# Upload workflow from content.
path = r"path\to\ayon-workflow\client\ayon_workflow\demo\workflow_from_events"
for file in os.listdir(path):
    if not file.lower().endswith(".json"):
        continue

    with open(os.path.join(path, file), "r") as f:
        content = f.read()

    resp = ayon_api.post(
        "addons/workflow/{addon_version}/upload",
        workflow_name=file,
        data=content,
    )
    print(resp.text)
```

1. Define a new simple action
```
{
  "simple_actions": [
    {
      "enabled": true,
      "local": true,
      "workflow_name": "SimpleActionWorkflow",
      "label": "My custom Workflow trigger",
      "input_entity": "Folder"
    }
  ],
}
```
2. This register this 3 workflows from the directory, those can be reviewed through the web-editor:
    * `trigger_from_cron`: Autmatically triggered from cron expression every minute.
    * `trigger_from_version_created_event`: Triggered from external event when a new version is created.
    * `trigger_from_simple_action`: Triggered from the `SimpleActionWorkflow` simple action defined in settings (locally or remotely).
3. Prepare a service user and set it token id in the `AYON_WORKFLOW_API_KEY` environment variable.
4. Run the processor through AYON launcher: `$AYON_EXECUTABLE --use-dev event-processor`
5. Results:
    * Ensure the cron workflow is triggered on its own every minutes.
    * Ensure the simple action workflow is triggered when the simple action is triggered and not local.
    * Ensure the simple action workflow is run locally when the simple action is triggered and local.
    * Ensure the workflow from version created event is triggered when a new version is created.
