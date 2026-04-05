from typing import Dict, Any, Optional

import ayon_api

from ayon_core.pipeline.load import get_representation_path_with_anatomy

from ayon_workflow import _utils
from ayon_workflow.datatypes import (
    ContextItem,
)


def get_latest_product_repre(
        context: ContextItem,
        product_id: Optional[str],
        product_version_id: Optional[str],
        representation_name: str,
    ) -> Dict[str, Any]:
    if not product_id and not product_version_id:
        raise ValueError(
            "Either product_id or product_version_id must be provided"
        )

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
        product_id: Optional[str],
        product_version_id: Optional[str],
        representation_name: str,
    ) -> str:
    repre = get_latest_product_repre(
        context,
        product_id,
        product_version_id,
        representation_name,
    )
    return get_representation_path_with_anatomy(
        repre,
        _utils.get_project_anatomy(context.project_name),
    )
