import enum
import logging
import json
import os
import subprocess
import shutil
import tempfile

from typing import Union, Optional

from ayon_core.lib import (
    get_ffmpeg_tool_args,
    filter_profiles,
    get_datetime_data,
    run_ayon_launcher_process
)
from ayon_core.lib.execute import clean_envs_for_ayon_process
from ayon_core.pipeline.template_data import get_template_data_with_names
from ayon_core.settings.lib import get_project_settings

from ayon_workflow import _utils
from ayon_workflow.datatypes import (
    ContextItem,
    FolderItem,
    Image,
    ImageSequence,
    MediaType,
    TaskItem,
    Video,
)

logger = logging.getLogger(__name__)


_CODECS = {
    "H264": {
        "codec": "libx264",
        "additionalArgs": (
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-g",
            "1",
            "-movflags",
            "faststart",
            "-color_range",
            "tv",
            "-colorspace",
            "bt709",
            "-color_primaries",
            "bt709",
            "-color_trc",
            "bt709",
        ),
    },
    "H265": {
        "codec": "libx265",
        # -tag:v hvc1 is required for QuickTime player on iOS/OSX. https://support.apple.com/en-ca/HT207022
        # https://brandur.org/fragments/ffmpeg-h265
        "additionalArgs": (
            "-crf",
            "18",
            "-tag:v",
            "hvc1",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "faststart",
            "-color_range",
            "tv",
            "-colorspace",
            "bt709",
            "-color_primaries",
            "bt709",
            "-color_trc",
            "bt709",
        ),
    },
    "PhotoJPEG": {
        "codec": "mjpeg",
        "additionalArgs": (
            "-qscale:v",
            "1",
            "-pix_fmt",
            "yuvj420p",
        ),
    },
}


VideoCodecs = enum.Enum("VideoCodecs", {key: key for key in _CODECS})


def _run_logged_subprocess(command: list[str]) -> tuple[int, str]:
    """Run a subprocess and stream combined output through the workflow logger."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
    )
    output_lines: list[str] = []

    assert process.stdout is not None
    for raw_line in process.stdout:
        line = raw_line.rstrip("\r\n")
        if not line:
            continue
        output_lines.append(line)
        logger.info(line)

    return process.wait(), "\n".join(output_lines)


def encode(
    context: ContextItem,
    input_media: Union[str, MediaType],
    output_media: Union[Video, str],
    codec: VideoCodecs,
    fps: float = 24.0,
    slate: Optional[Image] = None,
) -> Video:
    """Encode the input media into the output media."""
    remapped_input_media = _utils.remap_input(
        input_media, context.project_name
    )

    if isinstance(output_media, str):
        output_media = Video(path=output_media)
    remapped_output_media = _utils.remap_input(
        output_media.path,
        context.project_name
    )

    encode_args = []
    if isinstance(remapped_input_media, (Video, Image)):
        input_path = remapped_input_media.path
    elif isinstance(remapped_input_media, ImageSequence):
        if remapped_input_media.frame_range:
            encode_args.extend(
                [
                    "-start_number",
                    str(remapped_input_media.frame_range.first_frame),
                ]
            )
        input_path, _ = remapped_input_media.format().split(" ")
    else:
        input_path = remapped_input_media

    encode_args.extend(
        ("-y", "-r", str(fps), "-apply_trc", "gamma22", "-i", input_path)
    )

    if slate:
        remapped_slate_path = _utils.remap_input(
            slate.path,
            context.project_name
        )
        encode_args.insert(0, remapped_slate_path)
        encode_args.insert(0, "-i")
        encode_args.extend(
            (
                "-filter_complex",
                "[0:v]setsar=1[v0];[1:v]setsar=1[v1];[v0][v1]concat=n=2:v=1:a=0[v]",
                "-map", "[v]"
            )
        )

    data = _CODECS[codec]
    encode_args.extend(["-c:v", data["codec"]])
    encode_args.extend(data["additionalArgs"])
    encode_args.append(remapped_output_media)
    encode_args = get_ffmpeg_tool_args("ffmpeg") + encode_args


    # Run ffmpeg command
    cmd_line = " ".join(encode_args)
    logger.info(
        "Running encode command line: %s",
        cmd_line,
    )
    returncode, combined_output = _run_logged_subprocess(encode_args)

    if bool(returncode):
        logger.error(
            "Failed with returncode: %s",
            returncode,
        )
        raise RuntimeError(
            f"Command line failed: {cmd_line} "
            f"with return code: {returncode}"
        )

    if not combined_output:
        logger.info(
            "Encode completed without ffmpeg console output.",
        )
    return output_media


def generate_slate(
    context: ContextItem,
    input_sequence: ImageSequence,
    product_base_type: Optional[str] = None,
    product_name: Optional[str] = None,
    host_name: Optional[str] = None,
    output_directory: Optional[str] = None,
    comment: Optional[str] = ""
) -> Image:
    """ Generate a slate through ayon-slater.
    """
    # DISCLAIMER: This implementation is really a first version.
    # A lot of this code should be factorized within ayon-slater.
    # Do not use in production.
    project_settings = get_project_settings(context.project_name)
    publish_settings = project_settings["slater"]["publish"]
    profiles = publish_settings["ExtractGeneratedSlates"]["profiles"]

    filtering_criteria = {
        "host_names": host_name,
        "product_base_types": product_base_type,
        "product_names": product_name,
    }
    profile = filter_profiles(profiles, filtering_criteria)
    if not profile:
        raise RuntimeError(
            "Could not find any configured slater profile for provided inputs."
        )

    # Compute output slate path.
    output_directory = output_directory or _utils.get_staging_dir(
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
    slate_path = tempfile.NamedTemporaryFile(
        dir=output_directory,
        prefix="slater_",
        suffix=input_sequence.tail
    ).name

    # Generate replacement data
    folder_data = {"host_name": "workflow"}
    if isinstance(context, FolderItem):
        folder_data["folder_path"] = context.folder_path()
    if isinstance(context, TaskItem):
        folder_data["task_name"] = context.task_name

    fill_data = get_template_data_with_names(
        context.project_name,
        **folder_data,
    )

    # TODO: rework this to get closer to ayon-slater values.
    fill_data.update({
        "comment": comment or "",
        "frame_start": input_sequence.frame_range.first_frame,
        "frame_end": input_sequence.frame_range.last_frame,
        "file_extension": input_sequence.tail,
        "timecode": "00:00:00:00",
        "colorspaceData": {},
        "version": "",
        "fps": "",
        "product": {
            "type": product_base_type or "",
            "name": product_name or "",
        },
    })
    fill_data.update(get_datetime_data())

    num_of_frames = (
        input_sequence.frame_range.last_frame
        - input_sequence.frame_range.first_frame + 1
    )
    fill_data["frames"] = (
        f'{fill_data["frame_start"]}-{fill_data["frame_end"]} '
        f"({num_of_frames})"
    )
    fill_data["submission_date"] = (
        f"{fill_data['yyyy']}-{fill_data['mm']}-"
        f"{fill_data['dd']}"
    )

    # Generate thumbnail if provided
    thumbnail_path = tuple(input_sequence)[0]
    fill_data["thumbnail"] = _utils.remap_to_path(
        thumbnail_path,
        context.project_name,
    )

    # Run slater command
    import ayon_slater
    from ayon_slater.plugins.publish.extract_generate_slate import (
        ExtractGeneratedSlates
    )
    slater_core_dir = os.path.dirname(ayon_slater.__file__)
    slater_scriptpath = os.path.join(
        slater_core_dir,
        "slate_editor",
        "slate_editor.py"
    )

    temp_dir = tempfile.mkdtemp()
    def create_json_temp_file(data):
        with tempfile.NamedTemporaryFile(
            dir=temp_dir,
            mode="w",
            suffix=".json",
            delete=False
        ) as tmp:
            tmp.write(json.dumps(data))
            return str(tmp.name)

    data_path = create_json_temp_file(fill_data)

    slate_defs = ExtractGeneratedSlates.get_slate_definitions(
        profile, [], repre_custom_tags=None,
    )

    slate_def = tuple(slate_defs.values())[0]
    layout_path = create_json_temp_file(slate_def)

    args = [
        "--headless",
        "run", slater_scriptpath,
        "-d", data_path,
        "-l", layout_path,
        "-o", slate_path
    ]

    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    logger.debug("Command line: %s", " ".join(args))
    try:
        run_ayon_launcher_process(
            *args,
            add_sys_paths=False,
            env=clean_envs_for_ayon_process(env),
        )
    finally:
        shutil.rmtree(temp_dir)

    return Image(path=slate_path)
