""" usd turntable implementation
"""
from typing import Union

import os
import enum
import logging
import shutil
import subprocess
import tempfile

from ayon_workflow.datatypes import ContextItem, ImageSequence, FrameRange
from ayon_workflow.plugins.workflow.applications import _base
from ayon_workflow._utils import remap_input


logger = logging.getLogger(__name__)


class TurntableRenderer(enum.Enum):
    BLENDER = "blender"
    USDRECORD = "usdrecord"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_str(cls, value: str) -> "TurntableRenderer":
        for renderer in cls:
            if renderer.value == value:
                return renderer
        raise ValueError(f"Invalid renderer: {value}")


def _run_usd_record(
    usd_record_path: str,
    turntable_usd: str,
    output_media: ImageSequence,
    image_width: int,
):
    """ Render a turntable USD scene using usdrecord.
    """
    frame_range_str = (
        f"{output_media.frame_range.first_frame}:"
        f"{output_media.frame_range.last_frame}"
    )
    out_seq = os.path.join(
        output_media.directory,
        f"{output_media.head}{'#' * output_media.padding}{output_media.tail}"
    )
    cmd = [
        usd_record_path,
        "--frames", frame_range_str,
        "--camera", "/root/turntable/cam",
        "--imageWidth", str(image_width),
        turntable_usd,
        out_seq,
    ]

    subprocess.run(
        cmd,
        text=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _run_blender(
    context: ContextItem,
    turntable_usd: str,
    output_media: ImageSequence,
    image_width: int,
):
    """ Render a turntable USD scene using Blender.
    """
    BLENDER_EXTS = {
        '.png': 'PNG',
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG',
        '.exr': 'OPEN_EXR',
        '.tiff': 'TIFF',
        '.tga': 'TARGA',
    }

    out_seq = os.path.join(
        output_media.directory,
        f"{output_media.head}{'#' * output_media.padding}{output_media.tail}"
    )
    _, out_ext = os.path.splitext(out_seq)
    try:
        out_seq_ext = BLENDER_EXTS[out_ext.lower()]
    except KeyError:
        raise ValueError(f"Unsupported output extension in Blender: {out_ext}")

    python_expr = f"""
import bpy
import math

# Reset scene content
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Render settings
scene = bpy.context.scene
scene.frame_start = {output_media.frame_range.first_frame}
scene.frame_end = {output_media.frame_range.last_frame}
scene.render.resolution_x = {image_width}
scene.render.resolution_y = int({image_width} * 9 / 16)  # match usdrecord
scene.render.filepath = {repr(out_seq)}
scene.render.image_settings.file_format = {repr(out_seq_ext)}
scene.render.engine = 'BLENDER_EEVEE'

# Import turntable USD
bpy.ops.wm.usd_import(filepath={repr(turntable_usd)})

# Setup camera
cam_obj = bpy.data.objects.get("cam")
if cam_obj:
    bpy.context.scene.camera = cam_obj

bpy.ops.render.render(animation=True)
"""

    app_args = [
        "--background",
        "--python-exit-code", "1",
        "--python-expr", python_expr,
    ]
    _ = _base.run_application(
        "blender",
        context,
        app_args=app_args,
        app_application_variant=None,
    )


def prepare_turntable_usd(
    asset_usd_path: str,
    output_directory: str,
    frame_range: FrameRange,
) -> str:
    """Prepare turntable USD file ready for recording."""

    frames = frame_range.last_frame - frame_range.first_frame + 1
    rotation_samples = "\n            ".join(
        f"{fra}: {(fra - 1) * 360.0 / frames},"
        for fra in range(
            frame_range.first_frame,
            frame_range.last_frame + 1
        )
    )

    usda_content = f"""#usda 1.0
(
    startTimeCode = {frame_range.first_frame}
    endTimeCode = {frame_range.last_frame}
    defaultPrim = "root"
    upAxis = "Y"
)

def Xform "root"
{{
    def "asset" (
        references = @{asset_usd_path}@
    )
    {{
    }}

    def DomeLight "dome"
    {{
        float inputs:intensity = 1.0
        color3f inputs:color = (1, 1, 1)
    }}

    def RectLight "key_light"
    {{
        float inputs:intensity = 10.0
        float inputs:width = 2.0
        float inputs:height = 2.0
        color3f inputs:color = (1.0, 0.98, 0.95)
        double3 xformOp:translate = (2.0, 2.0, 2.0)
        float3 xformOp:rotateXYZ = (-45, 45, 0)
        uniform token[] xformOpOrder = [
            "xformOp:translate", "xformOp:rotateXYZ"
        ]
    }}

    def RectLight "fill_light"
    {{
        float inputs:intensity = 3.0
        float inputs:width = 2.0
        float inputs:height = 2.0
        color3f inputs:color = (0.8, 0.9, 1.0)
        double3 xformOp:translate = (-2.0, 1.0, 1.0)
        float3 xformOp:rotateXYZ = (-20, -45, 0)
        uniform token[] xformOpOrder = [
            "xformOp:translate", "xformOp:rotateXYZ"
        ]
    }}

    def Xform "turntable"
    {{
        float xformOp:rotateY.timeSamples = {{
            {rotation_samples}
        }}
        uniform token[] xformOpOrder = ["xformOp:rotateY"]

        def Camera "cam"
        {{
            float focalLength = 50
            float horizontalAperture = 36
            float verticalAperture = 24
            token projection = "perspective"

            double3 xformOp:translate = (0, 0.3, 2.5)
            float3 xformOp:rotateXYZ = (-10, 0, 0)
            uniform token[] xformOpOrder = [
                "xformOp:translate", "xformOp:rotateXYZ"
            ]
        }}
    }}
}}
    """

    with tempfile.NamedTemporaryFile(
        dir=output_directory,
        suffix="_turntable.usda",
        delete=False,
    ) as output_turn_path:
        output_turn_path.write(usda_content.encode())
        return output_turn_path.name


def run_turntable_with_record(
    context: ContextItem,
    usd_record_path: str,
    usd_input: str,
    output_media: ImageSequence,
    image_width: int = 1920,
    renderer: Union[str, TurntableRenderer] = TurntableRenderer.BLENDER,
):
    if output_media.frame_range is None:
        output_media.frame_range = FrameRange(
            first_frame=1,
            last_frame=1,  # TODO: change 80
        )

    if isinstance(renderer, str):
        renderer = TurntableRenderer.from_str(renderer)

    output_directory = tempfile.mkdtemp()
    try:
        # Prepare turntable USD file ready for recording
        logger.info(f"Preparing turntable USD file: {usd_input}")
        turntable_path = prepare_turntable_usd(
            usd_input,
            output_directory,
            output_media.frame_range,
        )

        # Run USD record
        remapped_output_media = remap_input(output_media, context.project_name)
        if renderer == TurntableRenderer.USDRECORD:
            # TODO: usd-record exe is OS specific right now
            # register it as an AYON application.
            logger.info(f"Rendering turn with usdrecord: {usd_record_path}")
            _run_usd_record(
                usd_record_path,
                turntable_path,
                remapped_output_media,
                image_width,
            )
        elif renderer == TurntableRenderer.BLENDER:
            logger.info(f"Rendering turn with Blender: {turntable_path}")
            _run_blender(
                context,
                turntable_path,
                remapped_output_media,
                image_width,
            )
        else:
            raise ValueError(f"Invalid renderer: {renderer}")

    finally:
        shutil.rmtree(output_directory)

    return output_media
