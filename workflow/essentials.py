""" Essential features to be exposed as nodes.
"""
import logging
import os
from dataclasses import asdict
from typing import Optional, Any, List, Union
import tempfile

from ayon_workflow.plugins.workflow._runtime_requirements import get_ayon_api

from ayon_workflow.datatypes import (
    ContextItem,
    FolderItem,
    FrameRange,
    ImageSequence,
    ProjectItem,
    TaskItem,
    Video,
)

logger = logging.getLogger(__name__)


def pass_through(input_data: Any) -> Any:
    return input_data


def _get_task_item(
        project_name: str,
        folder_item: FolderItem,
        task_name: str,
        task_type: str,
        ensure_exists: Optional[bool] = True,
    ) -> TaskItem:
        if ensure_exists:
            ayon_api = get_ayon_api()
            task_dict = ayon_api.get_task_by_name(
                project_name,
                folder_item.folder_id,
                task_name,
            )

            if (
                not task_dict
                or task_dict.get("taskType") != task_type
            ):
                raise ValueError(
                    f"No task {task_name} ({task_type})"
                    f"under {folder_item}."
                )

        attrs = asdict(folder_item)
        attrs["_parent"] = folder_item.parent
        attrs["task_name"] = task_name
        attrs["task_type"] = task_type
        return TaskItem(**attrs)


def _get_folder_item(
        project_name: str,
        folder_id: Optional[str] = None,
        folder_path: Optional[str] = None,
        ensure_exists: Optional[bool] = True,
    ) -> FolderItem:
        if ensure_exists:
            ayon_api = get_ayon_api()
            if not (folder_id or folder_path):
                raise ValueError(
                    "Missing folder_path or folder_id."
                )

            if folder_id:
                folder_dict = ayon_api.get_folder_by_id(
                    project_name,
                    folder_id,
                )

            else:
                folder_dict = ayon_api.get_folder_by_path(
                    project_name,
                    folder_path
                )

            if folder_dict:
                if folder_dict["parentId"]:
                    parent_folder = _get_folder_item(
                        project_name,
                        folder_id=folder_dict["parentId"]
                    )
                else:
                    parent_folder = None

                return FolderItem(
                    folder_type=folder_dict["folderType"],
                    folder_name=folder_dict["name"],
                    folder_id=folder_dict["id"],
                    project_name=project_name,
                    _parent=parent_folder,
                )

            raise ValueError(
                "Provided folder does not exists for "
                f"project_name={project_name} "
                f"folder_path={folder_path} "
                f"folder_id={folder_id}."
            )

        raise NotImplementedError(
            "Promised folder are not implemented yet."
        )


def get_ayon_context(
    project_name: str,
    folder_id: Optional[str] = None,
    folder_path: Optional[str] = None,
    task_name: Optional[str] = None,
    task_type: Optional[str] = None,
    ensure_exists: Optional[bool] = True,
) -> ContextItem:

    if not project_name:
        raise ValueError("No project name provided.")

    if ensure_exists and not get_ayon_api().get_project(project_name):
        raise ValueError(f"Project {project_name} does not exist.")

    if folder_id or folder_path:
        folder_item = _get_folder_item(
            project_name,
            folder_path=folder_path,
            folder_id=folder_id,
            ensure_exists=ensure_exists,
        )
        if task_name and task_type:
            return _get_task_item(
                project_name,
                folder_item,
                task_name,
                task_type,
                ensure_exists=ensure_exists
            )

        logger.info(f"Returning folder item: {folder_item}")
        return folder_item

    logger.info(f"Returning project item: {project_name}")
    return ProjectItem(project_name=project_name)


def _check_parent_directory(
        parent_directory: Optional[str],
    ) -> str:
    if not parent_directory:
        parent_directory = tempfile.mkdtemp()

    return parent_directory


def prepare_image_sequence(
    head: str,
    tail: str,
    directory: Optional[str] = None,
    padding: Optional[int] = 4,
    frame_range: Optional[FrameRange] = None,
) -> ImageSequence:
    directory = _check_parent_directory(directory)
    return ImageSequence(
        directory=directory,
        head=head,
        tail=tail,
        padding=padding,
        frame_range=frame_range,
    )


def prepare_video(
    path: str,
    frame_range: Optional[FrameRange] = None,
) -> Video:
    directory = os.path.dirname(path)
    basename = os.path.basename(path)

    directory = _check_parent_directory(directory)
    return Video(
        path=os.path.join(directory, basename),
        frame_range=frame_range,
    )


def fetch_folder_attribute(
    folder: FolderItem,
    attribute_name: str,
    default_value: Optional[Any] = None,
) -> Any:
    ayon_api = get_ayon_api()

    if folder.folder_id:
        folder_entity = ayon_api.get_folder_by_id(
            folder.project_name,
            folder.folder_id,
        )

    elif folder.folder_path:
        folder_entity = ayon_api.get_folder_by_path(
            folder.project_name,
            folder.folder_path,
        )

    else:
        raise ValueError(f"Not a valid folder: {folder}")

    ayon_value = (
        folder_entity.get(attribute_name)
        or folder_entity.get("attrib", {}).get(attribute_name)
    )
    if ayon_value:
        logger.info(f"Fetched folder {attribute_name} value: {ayon_value}")
        return ayon_value

    logger.info(f"Returning default value: {default_value}")
    return default_value


def append(inputs: Union[Any, List[Any]]) -> List[Any]:
    """ Merge provided input(s) in a single list.
    """
    result = []
    for input in inputs:
        if isinstance(input, list):
            result.extend(input)
        else:
            result.append(input)

    logger.info(f"Returning appended result: {result}")
    return result


def merge_sequences(
    image_sequences: Union[ImageSequence, List[ImageSequence]]
    ) -> ImageSequence:
    if not image_sequences:
        raise RuntimeError("Cannot merge: no sequence provided.")

    if isinstance(image_sequences, ImageSequence):
        return image_sequences

    ref_sequence = image_sequences.pop(0)
    for img_sequence in image_sequences:
        ref_str, _ = ref_sequence.format().rsplit(" ", 1)
        img_str, _ = img_sequence.format().rsplit(" ", 1)
        if ref_str != img_str:
            raise RuntimeError(
                f"Cannot merge {img_sequence} into {ref_sequence}."
            )

        ref_fr = ref_sequence.frame_range
        img_fr = img_sequence.frame_range
        ref_sequence.frame_range = FrameRange(
            first_frame=min(ref_fr.first_frame, img_fr.first_frame),
            last_frame=max(ref_fr.last_frame, img_fr.last_frame),
            step=ref_fr.step,
        )

    return ref_sequence
