from typing import Dict, Any, Optional, Union

import ayon_api

from ayon_core.pipeline.load import get_representation_path_with_anatomy

from ayon_workflow import _utils
from ayon_workflow.datatypes import (
    ContextItem,
    MediaType,
    Image,
    ImageSequence,
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

    repre = ayon_api.get_representation_by_name(
        context.project_name,
        representation_name,
        version_id=product_version_id
    )
    return repre


def get_latest_product_path(
        context: ContextItem,
        representation_name: str,
        product_id: Optional[str] = None,
        product_version_id: Optional[str] = None,
    ) -> str:
    """ Get the path of a specific representation for a version of a product.
    """
    repre = get_product_version_repre(
        context,
        representation_name,
        product_id=product_id,
        product_version_id=product_version_id,
    )
    return get_representation_path_with_anatomy(
        repre,
        _utils.get_project_anatomy(context.project_name),
    )


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

    ayon_api.upload_reviewable(
        context.project_name,
        product_version_id,
        file_path,
        label=label,
        content_type=content_type,
        filename=filename,
    )
