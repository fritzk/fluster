import os
from functools import lru_cache
import pathlib
import shlex
import subprocess
import tempfile

from fluster.codec import Codec, OutputFormat
from fluster.decoder import Decoder, register_decoder
from fluster.utils import file_checksum, run_command

PLATFORM_TPL = '{} --file {} --single {}'
FFMPEG_TPL = 'ffmpeg -y -i {} -c:v copy -f ivf {}'

class V4L2StatefulDecoder(Decoder):
    '''Generic class for V4L2 platform decoder'''
    binary = 'v4l2_stateful_decoder'
    description = ""
    cmd = ""

    def __init__(self) -> None:
        super().__init__()
        self.cmd = self.binary
        self.name = f'V4L2Stateful-{self.codec.value}'
        self.description = f'V4L2Stateful {self.codec.value} HW decoder'

    def decode(
        self,
        input_filepath: str,
        output_filepath: str,
        output_format: OutputFormat,
        timeout: int,
        verbose: bool,
    ) -> str:
        '''Decodes input_filepath in output_filepath'''
        if pathlib.Path(input_filepath).suffix == '.webm':
            tmpIVF = tempfile.NamedTemporaryFile(delete = False)
            try:
                cmd = shlex.split(FFMPEG_TPL.format(
                    input_filepath, tmpIVF.name))
                run_command(cmd, timeout=timeout, verbose=verbose)
                cmd = shlex.split(PLATFORM_TPL.format(
                    self.cmd, tmpIVF.name, output_filepath))
                run_command(cmd, timeout=timeout, verbose=verbose)
            finally:
                os.remove(tmpIVF.name)
        else:
            cmd = shlex.split(PLATFORM_TPL.format(
                self.cmd, input_filepath, output_filepath))
            run_command(cmd, timeout=timeout, verbose=verbose)
        return file_checksum(output_filepath)

@register_decoder
class V4L2StatefulDecoderH264Decoder(V4L2StatefulDecoder):
    '''V4L2 Stateful HW decoder for H.264'''
    codec = Codec.H264
    hw_acceleration = True


@register_decoder
class V4L2StatefulDecoderH265Decoder(V4L2StatefulDecoder):
    '''V4L2 Stateful HW decoder for H.265'''
    codec = Codec.H265
    hw_acceleration = True


@register_decoder
class V4L2StatefulDecoderVP8Decoder(V4L2StatefulDecoder):
    '''V4L2 Stateful HW decoder for VP8'''
    codec = Codec.VP8
    hw_acceleration = True


@register_decoder
class V4L2StatefulDecoderVP9Decoder(V4L2StatefulDecoder):
    '''V4L2 Stateful HW decoder for VP9'''
    codec = Codec.VP9
    hw_acceleration = True
