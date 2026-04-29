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

from ayon_workflow import _utils
from ayon_workflow.datatypes import (
    ContextItem,
    Image,
)
from ayon_workflow._utils import (
    remap_to_path,
    get_staging_dir,
)
from ayon_workflow.plugins.workflow.applications import _base


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
        "Text or image to 3D, top quality, PBR",
        "$0.40",
        supports_text=True,
        supports_image=True,
        output_format="glb",
    )
    MESHY_6 = _Model3DInfo(
        "fal-ai/meshy/v6/text-to-3d",
        "Meshy 6",
        "Text to 3D, PBR maps, topology control",
        "$0.10",
        supports_text=True,
        supports_image=False,
        output_format="glb",
    )
    TRELLIS = _Model3DInfo(
        "fal-ai/trellis",
        "Trellis",
        "Image to 3D, fast and cheap",
        "$0.02",
        supports_text=False,
        supports_image=True,
        output_format="glb",
    )
    TRELLIS_2 = _Model3DInfo(
        "fal-ai/trellis-2",
        "Trellis 2",
        "Image to 3D, higher quality",
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
            "geometry_file_format": "glb",
            "material": "PBR",
            "quality": "medium",
        }
        if image_url:
            args["input_image_urls"] = [image_url]
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

    if image:
        remapped_img_path = remap_to_path(image.path, context.project_name)
        logger.info("Uploading reference image...")
        image_url = client.upload_file(remapped_img_path)
    else:
        image_url = None

    logger.info(f"Generating 3D model using {model.label}...")
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

    output_directory = _utils.remap_input(
        output_directory,
        context.project_name,
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
        out_path = file_path.name

    if not os.path.exists(out_path):
        raise FileNotFoundError(f"Failed to download 3D model from {mesh_url}")

    # Convert input to USD with Blender if needed.
    if not out_path.endswith("usdz"):
        logger.info("Converting to USD...")
        usd_path = os.path.splitext(out_path)[0] + ".usdz"
        python_exr = f"""
import bpy
import mathutils

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(
    filepath={repr(out_path)},
)


# Normalize scale to 1.0
imported = [
    obj for obj in bpy.context.scene.objects
    if obj.type == 'MESH'
]

min_co = [float('inf')] * 3
max_co = [float('-inf')] * 3
for obj in imported:
    for corner in obj.bound_box:
        world = obj.matrix_world @ mathutils.Vector(corner)
        for i, co in enumerate(world):
            min_co[i] = min(min_co[i], co)
            max_co[i] = max(max_co[i], co)

scale = 1.0 / max(max_co[i] - min_co[i] for i in range(3))

for obj in imported:
    obj.scale *= scale

bpy.ops.object.select_all(action='DESELECT')
for obj in imported:
    obj.select_set(True)
bpy.context.view_layer.objects.active = imported[0]
bpy.ops.object.transform_apply(scale=True)

bpy.ops.wm.usd_export(
    filepath={repr(usd_path)},
    relative_paths=True,
    convert_orientation=True,
)
"""
        app_args = [
            "--background",
            "--python-exit-code", "1",  # ensure any exception in python raises
            "--python-expr",
            python_exr,
        ]
        _ = _base.run_application(
            "blender",
            context,
            app_args=app_args,
            app_application_variant=None,
        )
        out_path = usd_path

    remap_model_path = remap_to_path(out_path, context.project_name)
    return remap_model_path
