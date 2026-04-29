from typing import Dict, Any, Optional, Union, List
import os

import ayon_api

from ayon_core.pipeline.load import get_representation_path_with_anatomy

from ayon_workflow import _utils
from ayon_workflow.datatypes import (
    ContextItem,
    FrameRange,
    Image,
    ImageSequence,
    MediaType,
    VersionItem,
    Video,
)


def get_product_version_repre(
        context: ContextItem,
        representation_name: str,
        product_id: Optional[str] = None,
        product_version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
    """ Get a specific representation for the latest version of a product.
    """
    if not product_id and not product_version_id:
        raise ValueError(
            "Either product_id or product_version_id must be provided"
        )

    # Specific version ID is not provided,
    # get the latest version from product_id.
    if not product_version_id:
        latest_version = list(
            ayon_api.get_versions(
                context.project_name,
                product_ids=[product_id],
                latest=True,
            )
        )[0]
        product_version_id = latest_version["id"]

    return ayon_api.get_representation_by_name(
        context.project_name,
        representation_name,
        version_id=product_version_id
    )


def get_latest_product_path(
        context: ContextItem,
        representation_name: str,
        product_id: Optional[str] = None,
        product_version_id: Optional[str] = None,
    ) -> Union[str, Video, Image, ImageSequence]:
    """ Get the path of a specific representation for a version of a product.
    """
    repre = get_product_version_repre(
        context,
        representation_name,
        product_id=product_id,
        product_version_id=product_version_id,
    )
    if repre is None:
        raise ValueError(
            f"Could not find representation {representation_name} "
            f"for product_id {product_id} "
            f"and product_version_id {product_version_id}"
        )
    repre_path = get_representation_path_with_anatomy(
        repre,
        _utils.get_project_anatomy(context.project_name),
    )
    repre_context = repre["context"]

    repre_path = _utils.remap_to_path(repre_path, context.project_name)
    _, ext = os.path.splitext(repre_path)

    from ayon_core.lib.transcoding import VIDEO_EXTENSIONS, IMAGE_EXTENSIONS
    if ext in VIDEO_EXTENSIONS:
        return Video(path=repre_path)
    elif ext in IMAGE_EXTENSIONS:
        frame = repre_context.get("frame")
        if frame:
            head, tail = repre_path.split(frame)
            padding = len(frame)
            return ImageSequence(
                directory=os.path.dirname(repre_path),
                head=head,
                tail=tail,
                padding=padding,
                frame_range=FrameRange(
                    first_frame=int(frame),
                    last_frame=int(frame) + len(repre["files"]) - 1
                )
            )
        return Image(path=repre_path)
    return repre_path


def upload_reviewable(
        context: ContextItem,
        product_version_id: str,
        reviewable_media: Union[str, MediaType],
        label: Optional[str] = None,
        content_type: Optional[str] = None,
        filename: Optional[str] = None,
):
    """ Upload a reviewable file for a product version.
    """
    # Extract the file path from the reviewable media.
    if isinstance(reviewable_media, str):
        file_path = reviewable_media
    elif isinstance(reviewable_media, (Video, Image)):
        file_path = reviewable_media.path
    elif isinstance(reviewable_media, ImageSequence):
        frame_paths = list(reviewable_media)
        # if an image sequence is provided, use the first frame
        file_path = frame_paths[0]
    else:
        raise ValueError(
            f"Not a valid reviewable media type: {reviewable_media}"
        )

    mapped_path = _utils.remap_to_path(file_path, context.project_name)

    ayon_api.upload_reviewable(
        context.project_name,
        product_version_id,
        mapped_path,
        label=label,
        content_type=content_type,
        filename=filename,
    )


def append_version_to_server_list(
    context: ContextItem,
    input_versions: Union[VersionItem, List[VersionItem]],
    list_label: str,
    create_list: bool = True,
):
    """ Append a version to a server list.
    """
    if not isinstance(input_versions, list):
        input_versions = [input_versions]

    # Get or create list
    all_lists = list(ayon_api.get_entity_lists(context.project_name))
    for project_list in all_lists:
        if project_list["label"] == list_label:
            list_id = project_list["id"]
            break
    else:
        if create_list:
            list_id = ayon_api.create_entity_list(
                context.project_name,
                entity_type="version",
                label=list_label,
            )
        else:
            raise ValueError(f"List not found: {list_label}")

    # Append versions to list
    for version in input_versions:
        ayon_api.create_entity_list_item(
            context.project_name,
            list_id,
            data={"entityId": version.version_id},
        )
