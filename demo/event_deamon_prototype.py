""" Protytpe: event daemon service.
 Simplest and dumbest approach, not yet ready for production.
"""
import tempfile
from typing import Dict, Any, List

import logging
import collections
import json
import sys
import time
import socket
import subprocess
import traceback
import os

import ayon_api


logger = logging.getLogger(__file__)

#sys.path.append(r"C:\Users\robin\OneDrive\Bureau\dev_ayon\dev\ayon-workflow\client")
#sys.path.append(r"C:\Users\robin\OneDrive\Bureau\dev_ayon\dev\ayon-core\client")


class WorkflowEventProcessor:
    def __init__(self):
        """Initialize the daemon processor..
        """
        logger.info("Initializing the Workflow event processor.")
        ayon_api.init_service()

        settings = ayon_api.get_service_addon_settings(project_name="Dummy")

        self._handlers_per_event_type = collections.defaultdict(list)
        self._init_handlers(settings["workflows"])

    def _init_handlers(self, settings: List[Dict[str, Any]]):
        """ Initialize handler from settings.
        """
        for workflow in settings:
            if not workflow["enabled"]:
                continue

            for event_data in workflow["events_trigger"]:
                self._handlers_per_event_type[event_data["event_type"]].append(
                    {
                        "workflow": workflow,
                        "event_data": event_data,
                    }
                )

    def _prepare_input_file(
        self,
        project_name: str,
        action_inputs: Dict[str, Any],
        inputs_template: str,
        ) -> str:
        """ Prepare inputs from events as a temporary file.
        """
        def _resolve(obj: object, inputs: dict) -> object:
            if isinstance(obj, str):
                return obj.format_map(inputs)
            if isinstance(obj, dict):
                return {k: _resolve(v, inputs) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_resolve(item, inputs) for item in obj]
            return obj

        event_inputs = {
            "input": action_inputs,
            "project_name": project_name,
        }
        template_data = json.loads(inputs_template)

        with tempfile.NamedTemporaryFile(
            prefix="workflow_tmp_inputs",
            suffix=".json",
            mode="w",
            delete=False,
        ) as inputs_handler:
            inputs_data = _resolve(template_data, event_inputs)
            inputs_handler.write(json.dumps(inputs_data))
            return inputs_handler.name


    def start_processing(self):
        """Enroll AYON events `shotgrid.event`
        """
        if not self._handlers_per_event_type:
            print("Nothing to listen to.")
            return

        # Figuring out executable.
        executable_dir = os.path.dirname(os.getenv("AYON_EXECUTABLE", ""))
        executable_path = os.path.join(executable_dir, "ayon_console.exe")

        if not os.path.exists(executable_path):
            executable_path = (
                r"C:\Program Files\Ynput\AYON 1.5.4\ayon_console.exe"
            )

        while True:
            try:
                event = ayon_api.enroll_event_job(
                    list(self._handlers_per_event_type),
                    "workflow.proc",
                    socket.gethostname(),
                    description="Enrolling to any relevant Event...",
                    max_retries=2,
                    sequential=False,
                )

                if not event:
                    time.sleep(1.0)
                    logger.info("Wait for new events.")
                    print("wait")
                    continue

                # Get source event because it is having payload to process
                source_event = ayon_api.get_event(event["dependsOn"])

                for workflow_entry in self._handlers_per_event_type[
                    source_event["topic"]
                ]:
                    try:
                        logging.info(f"workflow: {workflow_entry}")
                        logging.info(f"processing event {source_event}")
                        logging.info("-----------------")

                        product = ayon_api.get_product_by_id(
                            source_event["project"],
                            source_event["summary"]["parentId"],
                        )

                        if product["productBaseType"] != "render":
                            print("Ignore this product version.")
                            logger.info(f'Updating {event["id"]} to finished.')
                            ayon_api.update_event(
                                event["id"],
                                status="finished",
                            )
                            continue

                        # Prepare an JSON with inputs mapping.
                        prepared_inputs = self._prepare_input_file(
                            source_event["project"],
                            source_event["summary"].copy(),
                            workflow_entry["event_data"]["inputs_template"],
                        )

                        # Workflow execution through command line as
                        # the deamon service currently does not run within the
                        # AYON environment.
                        # TODO: a lot of this should be refactorized with
                        # process-event CLI that acts on AYON server actions.

                        # Farm submission
                        print("%r" % source_event)
                        if workflow_entry["workflow"]["submission"]:
                            args = [
                                executable_path,
                                "addon",
                                "workflow",
                                "submit",
                                "--workflow-path",
                                workflow_entry["workflow"]["workflow_path"],
                                "--inputs-path",
                                prepared_inputs,
                                "--project",
                                source_event["project"],
                            ]
                        else:
                            args = [
                                executable_path,
                                "addon",
                                "workflow",
                                "execute",
                                "--workflow-path",
                                workflow_entry["workflow"]["workflow_path"],
                                "--inputs-path",
                                prepared_inputs,
                                "--project",
                                source_event["project"],
                            ]

                        if os.getenv("AYON_USE_STAGING") == "1":
                            args.insert(1, "--use-staging")
                        elif os.getenv("AYON_USE_DEV") == "1":
                            args.insert(1, "--use-dev")

                        logger.debug(args)
                        print("Processing %r" % args)
                        try:
                            subprocess.run(
                                args,
                                check=True,
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                            )
                        finally:
                            os.remove(prepared_inputs)
                            pass


                        logger.info(f'Updating {event["id"]} to finished.')
                        ayon_api.update_event(
                            event["id"],
                            status="finished",
                        )

                    except Exception:
                        logger.error(
                            "Unable to process handler",
                            exc_info=True
                        )
                        ayon_api.update_event(
                            event["id"],
                            status="failed",
                            description="An error occurred while processing",
                            payload={"message": traceback.format_exc()},
                        )
                        raise

            except Exception:
                logger.error(traceback.format_exc())
                raise


def service_main():
    ayon_api.init_service()
#    ayon_api.set_sender_type("workflow")

    workflow_processor = WorkflowEventProcessor()
    sys.exit(workflow_processor.start_processing())


if __name__ == "__main__":
    os.environ["AYON_SERVER_URL"] = "http://127.0.0.1:5000"
    os.environ["AYON_ADDON_NAME"] = "workflow"
    os.environ["AYON_ADDON_VERSION"] = "0.3.2+dev.rr6"
    os.environ["AYON_API_KEY"] = "cf8d512ad405457b801a6804d4bf5368"
#    os.environ["AYON_USE_DEV"] = "1"
    service_main()
