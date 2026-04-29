""" Text to image generation using fal.ai
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

from ayon_workflow import _utils
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
class _ModelInfo:
    endpoint_id: str
    label: str
    description: str
    cost_per_image: str


class TextToImageModel(enum.Enum):
    FLUX_SCHNELL = _ModelInfo(
        "fal-ai/flux/schnell",
        "FLUX Schnell",
        "Fast, cheap, great for prototyping",
        "$0.003",
    )
    FLUX_PRO = _ModelInfo(
        "fal-ai/flux-pro/v1.1",
        "FLUX.2 Pro",
        "Max quality, photorealism",
        "$0.04",
    )
    RECRAFT_V4 = _ModelInfo(
        "fal-ai/recraft-v4",
        "Recraft V4",
        "Logos, vectors, typography, brand assets",
        "$0.04",
    )
    SEEDREAM = _ModelInfo(
        "fal-ai/seedream-v4-5",
        "Seedream 4.5",
        "Complex prompts, ByteDance",
        "$0.04",
    )
    IMAGEN3 = _ModelInfo(
        "fal-ai/imagen3",
        "Imagen 3",
        "Text rendering in image, Google",
        "$0.05",
    )
    NANO_BANANA = _ModelInfo(
        "fal-ai/nano-banana",
        "Nano Banana 2",
        "Speed + quality, ~1-3s per image",
        "$0.06",
    )

    @property
    def endpoint_id(self) -> str:
        return self.value.endpoint_id

    @property
    def label(self) -> str:
        return self.value.label

    @property
    def cost(self) -> str:
        return self.value.cost_per_image

    def __str__(self) -> str:
        return f"{self.label} — ({self.cost}/image)"

    @classmethod
    def from_str(cls, model_str: str) -> "TextToImageModel":
        for model in cls:
            if (
                str(model) == model_str
                or model.endpoint_id == model_str
            ):
                return model

        raise ValueError(f"No model found for {model_str}")


def text_to_image(
    context: ContextItem,
    prompt: str,
    model: Union[str, TextToImageModel] = "fal-ai/flux/schnell",
    image_size: str = "landscape_4_3",
    fal_api_key: Optional[str] = None,
    output_directory: Optional[str] = None,
) -> Image:
    """ Generate an image from a text prompt using fal.ai.
    """
    # Configure client from fal.ai API key.
    fal_api_key = fal_api_key or os.getenv("FAL_KEY")
    client = fal_client.SyncClient(key=fal_api_key)

    # Check provided model.
    if isinstance(model, str):
        model = TextToImageModel.from_str(model)

    # Query image from online model.
    logger.info(f"Generating image using {model.label}...")
    result = client.run(
        model.endpoint_id,
        arguments={
            "prompt": prompt,
            "image_size": image_size,
            "num_images": 1,
        },
    )

    image_url = [image["url"] for image in result["images"]][0]
    output_directory = output_directory or get_staging_dir(
        context,
        # TODO: rework this
        "image",  # product_type
        "image",  # product_name
        "image",  # product_base_type
    )

    output_directory = _utils.remap_input(
        output_directory,
        context.project_name,
    )

    # Download and save image locally.
    logger.info("Downloading image...")
    response = httpx.get(image_url)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(
        dir=output_directory,
        delete=False,
        suffix=".png",
    ) as file_path:
        file_path.write(response.content)

    if not os.path.exists(file_path.name):
        raise FileNotFoundError(f"Failed to download image from {image_url}")

    remap_img_path = remap_to_path(
        str(file_path.name),
        context.project_name,
    )
    return Image(path=remap_img_path)
