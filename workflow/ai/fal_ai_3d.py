""" Text/image to 3D model generation using fal.ai
    https://fal.ai integration
"""
import enum
import logging
import os
import tempfile

from dataclasses import dataclass
from typing import Optional, Union

import fal_client
import httpx

from ayon_workflow.datatypes import (
    ContextItem,
    Image,
)
from ayon_workflow._utils import (
    remap_to_path,
    get_staging_dir,
)

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class _Model3DInfo:
    endpoint_id: str
    label: str
    description: str
    cost_per_generation: str
    supports_text: bool
    supports_image: bool
    output_format: str  # native output format


class TextTo3DModel(enum.Enum):
    HYPER3D_RODIN = _Model3DInfo(
        "fal-ai/hyper3d/rodin",
        "Hyper3D Rodin",
        "Text or image to 3D, supports USDZ/GLB/FBX, PBR",
        "$0.40",
        supports_text=True,
        supports_image=True,
        output_format="usdz",
    )
    MESHY_6 = _Model3DInfo(
        "fal-ai/meshy/v6/text-to-3d",
        "Meshy 6",
        "Text to 3D, GLB, PBR maps, topology control",
        "$0.10",
        supports_text=True,
        supports_image=False,
        output_format="glb",
    )
    TRELLIS = _Model3DInfo(
        "fal-ai/trellis",
        "Trellis",
        "Image to 3D, GLB, fast and cheap",
        "$0.02",
        supports_text=False,
        supports_image=True,
        output_format="glb",
    )
    TRELLIS_2 = _Model3DInfo(
        "fal-ai/trellis-2",
        "Trellis 2",
        "Image to 3D, GLB, higher quality",
        "$0.25-0.35",
        supports_text=False,
        supports_image=True,
        output_format="glb",
    )

    @property
    def endpoint_id(self) -> str:
        return self.value.endpoint_id

    @property
    def label(self) -> str:
        return self.value.label

    def __str__(self) -> str:
        return (
            f"{self.label} — {self.value.description} "
            f"({self.value.cost_per_generation}/gen)"
        )

    @classmethod
    def from_str(cls, model_str: str) -> "TextTo3DModel":
        for model in cls:
            if (
                model.endpoint_id == model_str
                or str(model) == model_str
            ):
                return model
        raise ValueError(f"No 3D model found for {model_str}")


def _build_arguments(
    model: TextTo3DModel,
    prompt: Optional[str],
    image_url: Optional[str],
) -> dict:
    """Build model-specific arguments."""
    if model == TextTo3DModel.HYPER3D_RODIN:
        args = {
            "geometry_file_format": "usdz",
            "material": "PBR",
            "quality": "medium",
        }
        if image_url:
            args["input_image_urls"] = image_url
        elif prompt:
            args["prompt"] = prompt
        else:
            raise ValueError(
                "Hyper3D Rodin requires either a prompt or an image input."
            )
        return args

    if model == TextTo3DModel.MESHY_6:
        if not prompt:
            raise ValueError("Meshy 6 requires a text prompt.")
        return {"prompt": prompt, "art_style": "realistic", "enable_pbr": True}

    if model in (TextTo3DModel.TRELLIS, TextTo3DModel.TRELLIS_2):
        if not image_url:
            raise ValueError(f"{model.label} requires an image input.")
        return {"image_url": image_url}

    raise ValueError(f"Unsupported model: {model}")


def _get_mesh_url(model: TextTo3DModel, result: dict) -> str:
    """Extract mesh URL from model-specific result structure."""
    if model == TextTo3DModel.HYPER3D_RODIN:
        return result["model_mesh"]["url"]
    if model == TextTo3DModel.MESHY_6:
        return result["model_urls"]["glb"]
    if model == TextTo3DModel.TRELLIS:
        return result["model_mesh"]["url"]
    if model == TextTo3DModel.TRELLIS_2:
        return result["model_glb"]["url"]

    raise ValueError(f"Unsupported model: {model}")


def text_image_to_3d_model(
    context: ContextItem,
    prompt: Optional[str] = None,
    image: Optional[Image] = None,
    model: Union[str, TextTo3DModel] = TextTo3DModel.HYPER3D_RODIN,
    fal_api_key: Optional[str] = None,
    output_directory: Optional[str] = None,
) -> str:
    """Generate a 3D model from a text prompt and/or image using fal.ai.
    """
    if not prompt and not image:
        raise ValueError("At least one of prompt or image must be provided.")

    if isinstance(model, str):
        model = TextTo3DModel.from_str(model)

    fal_api_key = fal_api_key or os.getenv("FAL_KEY")
    client = fal_client.SyncClient(key=fal_api_key)

    # Check inputs against model capabilities.
    if image and not model.value.supports_image:
        logger.warning(
            f"{model.label} does not support image, input will be ignored."
        )
    if prompt and not model.value.supports_text:
        logger.warning(
            f"{model.label} does not support text, input will be ignored."
        )

    logger.info("Uploading reference image...")
    image_url = client.upload_file(image.path) if image else None
    logger.info("Generating 3D model...")
    result = client.run(
        model.endpoint_id,
        arguments=_build_arguments(model, prompt, image_url)
    )
    mesh_url = _get_mesh_url(model, result)

    output_directory = output_directory or get_staging_dir(
        context,
        # TODO: rework this
        "model",  # product_type
        "model",  # product_name
        "model",  # product_base_type
    )

    logger.info("Saving 3D model...")
    response = httpx.get(mesh_url)
    response.raise_for_status()

    suffix = f".{model.value.output_format}"
    with tempfile.NamedTemporaryFile(
        dir=output_directory,
        delete=False,
        suffix=suffix,
    ) as file_path:
        file_path.write(response.content)

    if not os.path.exists(file_path.name):
        raise FileNotFoundError(f"Failed to download 3D model from {mesh_url}")

    # TODO convert input to USD.
    remap_model_path = remap_to_path(str(file_path.name), context.project_name)
    return remap_model_path
