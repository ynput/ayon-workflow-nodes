from typing import Union

import enum
import logging
import subprocess

from ayon_core.lib import get_ffmpeg_tool_args

from ayon_workflow import _utils
from ayon_workflow.datatypes import (
    ContextItem,
    ImageSequence,
    Image,
    MediaType,
    Video,
)


logger = logging.getLogger(__name__)


_CODECS = {
    'H264': {
        'codec': 'libx264',
        'additionalArgs': (
            '-crf', '20',
            '-pix_fmt', 'yuv420p',
            '-vf', 'colormatrix=bt601:bt709',
        ),
    },
    'H265': {
        'codec': 'libx265',
        # -tag:v hvc1 is required for QuickTime player on iOS/OSX. https://support.apple.com/en-ca/HT207022
        # https://brandur.org/fragments/ffmpeg-h265
        'additionalArgs': (
            '-crf', '20',
            '-tag:v', 'hvc1',
            '-pix_fmt', 'yuv420p',
        ),
    },
    'PhotoJPEG': {
        'codec': 'mjpeg',
        'additionalArgs': (
            '-qscale:v', '1',
            '-pix_fmt', 'yuvj420p',
        ),
    },
}


VideoCodecs = enum.Enum("VideoCodecs", {key: key for key in _CODECS})


def encode(
    context: ContextItem,
    input_media: Union[str, MediaType],
    output_media: Video,
    codec: VideoCodecs,
    fps: float = 24.0,
) -> Video:
    """ Encode the input media into the output media.
    """
    remapped_output_media = _utils.remap_input(
        output_media,
        context.project_name
    )

    kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "encoding": "utf-8",
        "errors": "replace",
    }
    encode_args = [subprocess.list2cmdline(get_ffmpeg_tool_args("ffmpeg"))]
    if isinstance(input_media, (Video, Image)):
        input_path = input_media.path
    elif isinstance(input_media, ImageSequence):
        if input_media.frame_range:
            encode_args.extend([
                "-start_number",
                str(input_media.frame_range.first_frame)
            ])
        input_path, _ = input_media.format().split(" ")
    elif isinstance(input_media, str):
        input_path = input_media
    else:
        raise ValueError(f"Unsupported input media type: {type(input_media)}")

    encode_args.extend(
        ('-y', '-r', str(fps), '-i', input_path)
    )

    data = _CODECS[codec]
    encode_args.extend(["-c:v", data["codec"]])
    encode_args.extend(data["additionalArgs"])
    encode_args.append(remapped_output_media)

    # Run ffmpeg command
    cmd_line = " ".join(encode_args)
    logger.debug(f"Running encode command line: {cmd_line}\n")
    process = subprocess.run(cmd_line, **kwargs, check=True)

    if bool(process.returncode):
        logger.error(f"Failed with returncode: {process.returncode}\n")
        raise RuntimeError(
            f"Command line failed: {cmd_line} "
            f"with return code: {process.returncode}"
        )

    logger.debug(process.stdout)
    return output_media
