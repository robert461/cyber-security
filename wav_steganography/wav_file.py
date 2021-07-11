import textwrap
from collections import OrderedDict
from pathlib import Path
import struct
from typing import Optional, Union, List, Tuple
import math

import numpy as np
import pandas as pd

from error_correction.generic_error_correction import GenericErrorCorrection
from error_correction.reed_solomon_error_correction import ReedSolomonErrorCorrection
from security.encryptors.generic_encryptor import GenericEncryptor
from security.encryptors.none_encryptor import NoneEncryptor
from wav_steganography.data_chunk import DataChunk
from wav_steganography.message import Message


class WAVFile:
    """ Basic WAV Audio File Parser

    Reference: http://soundfile.sapp.org/doc/WaveFormat/
    Helpful video: https://www.youtube.com/watch?v=udbA7u1zYfc

    The WAV header specification was created based on the reference above.
    Each entry is formatted as follows:

        (name, format, byte_count, [allowed_values])

    * `name` will be used to store the variable in the WAVFile.header dictionary.
    * `format` is the byte format required for struct: https://docs.python.org/3/library/struct.html
    * `bytes` is the number of bytes to read from the file
    * `[allowed_values]` is a list of allowed values for this entry, if None, no check is made
    """

    _wav_header_specification: List[Tuple[str, str, int, Optional[List]]] = [
        # === RIFF Chunk ===
        ("ChunkID", '>4s', 4, [b"RIFF", b"RIFX"]),
        ("ChunkSize", '<i', 4, None),
        ("Format", '>4s', 4, [b"WAVE"]),

        # === FORMAT Subchunk ===
        ("Subchunk1ID", '>4s', 4, [b"fmt "]),
        ("Subchunk1Size", '<i', 4, [16]),
        ("AudioFormat", '<h', 2, [1]),
        ("NumChannels", '<h', 2, [1, 2]),
        ("SampleRate", '<i', 4, None),
        ("ByteRate", '<i', 4, None),
        ("BlockAlign", '<h', 2, None),
        ("BitsPerSample", '<h', 2, [8, 16, 32]),

        # === DATA Subchunk ===
        ("Subchunk2ID", '>4s', 4, [b"data"]),
        ("Subchunk2Size", '<i', 4, None),
    ]

    def __init__(self, filename: Union[Path, str]):
        """ Parse WAV file given a path to audio file """
        self._created_from_filename = filename
        self.header = h = OrderedDict()
        with open(filename, 'rb') as wav_file:

            # Parse according to specification
            for name, formatting, byte_count, allowed_values in self._wav_header_specification:
                h[name] = struct.unpack(formatting, wav_file.read(byte_count))[0]
                if allowed_values is not None:
                    if "ID" in name:
                        while h[name] not in allowed_values:
                            subchunk_size = struct.unpack("<i", wav_file.read(4))[0]
                            wav_file.read(subchunk_size)
                            h[name] = struct.unpack(formatting, wav_file.read(byte_count))[0]

                    assert h[name] in allowed_values, f"{name} is {h[name]}, not among {allowed_values}!"

            # Make assertions about expected size
            assert h["BlockAlign"] == h['NumChannels'] * h['BitsPerSample'] // 8
            assert h["ByteRate"] == h['SampleRate'] * h['NumChannels'] * h['BitsPerSample'] // 8

            # Parse the actual data
            self.data = np.array(struct.unpack(self._get_data_format(), wav_file.read(h['Subchunk2Size'])))

    def _data_as_channel_data_frame(self, data_arr: np.ndarray) -> pd.DataFrame:
        return pd.DataFrame(data={
            f"channel_{i}": data_arr[i::self.header['NumChannels']].flatten()
            for i in range(0, self.header['NumChannels'])
        })

    def _get_data_format(self) -> str:
        """ Returns the data format string required for struct (e.g. "<88200h") """
        endianness = ('<' if self.header["ChunkID"] == b"RIFF" else ">")
        integer_count = self.header['Subchunk2Size'] * 8 // self.header['BitsPerSample']
        integer_size = {8: 'b', 16: 'h', 32: 'i'}[self.header['BitsPerSample']]
        return f"{endianness}{integer_count}{integer_size}"

    def write(self, filename: Union[Path, str], overwrite: bool = False):
        """ Create a WAVFile with given filename """
        if not overwrite and filename.exists():
            raise FileExistsError
        with open(filename, 'wb') as file:
            for name, formatting, byte_count, allowed_values in self._wav_header_specification:
                assert name in self.header, f"Parameter {name} not found in header!"
                file.write(struct.pack(formatting, self.header[name]))
            file.write(struct.pack(self._get_data_format(), *list(self.data)))

    def time_to_index(self, at_time_s: float) -> int:
        """ Returns index of data, given as second, if None then returns len """
        if at_time_s is None:
            return len(self.data)
        return round(at_time_s * len(self.data))

    def slice(self, from_s: float = 0.0, to_s: Optional[float] = None) -> np.ndarray:
        """ Returns a slice of the given data between interval in seconds """
        from_i = self.time_to_index(from_s)
        to_i = self.time_to_index(to_s)
        assert from_i < to_i, f"Invalid interval, {from_i} >= {to_i}!"
        return self.data[from_i:to_i]

    def plot(self, from_s: float = 0.0, to_s: Optional[float] = 0.1, *, filename: Union[Path, str] = None, show=False):
        """ Create a plot of the audio with the given time-frame """
        import seaborn as sns
        from matplotlib import pyplot as plt
        sns.set_theme()
        sns.relplot(data=self.slice(from_s, to_s), kind="line")
        if show:
            plt.show()
        if filename is not None:
            plt.savefig(filename)

    def get_channel_data(self, channel1based: int = 1):
        """ Get the data for the given channel (1 indexed). Raises a ValueError if not enough channels """
        channels = self.num_channels
        if not (1 <= channel1based <= channels):
            raise ValueError(f"Non-existent channel: {channel1based} (#num channels: {channels})")
        # E.g. start at 0, take every 2 number
        return self.data[channel1based-1::channels]

    def spectrogram(self, *, filename: Union[Path, str] = None, ax=None, show=True) -> np.ndarray:
        """ Plot a spectrogram, if filename supplied save it, if show supplied then display interactively """
        from matplotlib import pyplot as plt
        if ax is None:
            _, ax = plt.subplots()
        spectrum, freqs, t, im = ax.specgram(self.get_channel_data(1), Fs=self.header["SampleRate"])
        ax.set_ylabel("Frequency (Hz)")
        ax.set_xlabel("Time (s)")
        if show:
            plt.title(f"Spectrogram for file {self._created_from_filename}")
            plt.show()
        if filename is not None:
            plt.savefig(filename)
        return spectrum

    @property
    def sample_rate(self):
        return self.header["SampleRate"]

    @property
    def num_channels(self):
        return self.header["NumChannels"]

    def play(self):
        from pydub import AudioSegment, playback
        from tempfile import TemporaryDirectory
        with TemporaryDirectory(prefix="wav_steganography") as tmp_dir:
            file_path = Path(tmp_dir) / "tmp_audio_segment.wav"
            self.write(file_path, overwrite=True)
            audio_segment = AudioSegment.from_file(file_path)
            playback.play(audio_segment)

    def encode(
            self,
            data: bytes,
            least_significant_bits: int = 2,
            every_nth_byte: int = 1,
            redundant_bits: int = 0,
            encryptor: GenericEncryptor = NoneEncryptor(),
            error_correction: GenericErrorCorrection = ReedSolomonErrorCorrection(),
            repeat_data: bool = False,
    ):
        """ Encode a message in the given WAVFile

        This is done by writing to every nth bytes some number of least significant bits.
        A short header is written first, then the message.
        """
        assert least_significant_bits <= self.header["BitsPerSample"]

        # The loop will run once if repeat_data = False, and twice if it is True. The loop is used
        # to avoid code duplication. Calculating the needed data size in advance when repeating is hard,
        # (would have to account for redundancy, encryption, etc.), therefore the first iteration is
        # used as an estimate for the needed size in the second run.
        while True:
            header_chunk, data_chunk = Message.encode_message(
                data,
                least_significant_bits,
                every_nth_byte,
                redundant_bits,
                encryptor,
                error_correction,
            )

            amplitudes_available = len(self.data) - header_chunk.amplitudes_required
            if repeat_data:
                data *= amplitudes_available // data_chunk.amplitudes_required
                repeat_data = False
            else:
                break

        if amplitudes_available < data_chunk.amplitudes_required:
            raise ValueError(
                f"ERROR: File not large enough for the given message! "
                f"Required amplitudes: header = {header_chunk.amplitudes_required}, "
                f"data = {data_chunk.amplitudes_required}.\n\tAmplitudes available in total: {len(self.data)}. "
                f"After encoding header not enough amplitudes left: "
                f"{amplitudes_available} < {data_chunk.amplitudes_required}."
            )

        self._write_chunks([header_chunk, data_chunk])

        decoded_message = self.decode(encryptor=encryptor, error_correction = error_correction)

        assert decoded_message == data,\
            f'Cannot decode encrypted message: "{decoded_message}" != "{data}"'

    def _write_chunks(self, chunks: List[DataChunk], at_byte: int = 0):
        """ Encode the given chunks on after another, starting at at_byte """
        for chunk in chunks:
            at_byte = self._write_chunk(chunk, at_byte)

    def _write_chunk(self, chunk: DataChunk, at_byte: int) -> int:
        """ Encode a given chunk at the specified byte index """
        nth = chunk.every_nth_byte

        binary_data = ''.join(map(lambda b: f"{b:08b}", chunk.data))  # e.g. "0010101011101100"
        lsb_bits = textwrap.wrap(binary_data, chunk.least_significant_bits)  # e.g. ["00", "10", ...]
        binary_data_split_up = list(map(lambda b: int(b, 2), lsb_bits))  # e.g. [0, 2, ...]
        end_byte_index = len(binary_data_split_up) * nth + at_byte  # e.g. 32 on first iteration

        self.data[at_byte:end_byte_index:nth] = self._set_last_n_bits_in_array(
            self.data[at_byte:end_byte_index:nth],
            binary_data_split_up,
            chunk.least_significant_bits,
        )
        return end_byte_index

    @staticmethod
    def _set_last_n_bits_in_array(data_slice: np.ndarray, binary_data_split_up, n_bits_to_set: int):
        """ Set n bits in data_bits to 0, then set them equal to message_bits

        Say LSBs = 2, data_bits = 0b10111001, message_bits = 0b10, then:
        ones   =   (2**n_bits_to_set - 1)   =   0b100 - 1   =   0b11

        Now get the LSBs bits from data_bits:
        lsb_data_bits  =  data_bits & ones  =  0b10111001 & 0b11  =  0b01

        Using lsb_data_bits set LSBs bits in data_bits to zero:
        data_bits_with_zeros  =  data_bits ^ lsb_data_bits  =  0b10111001 ^ 0b01  =  0b10111000

        Now that the LSBs bits are zero, just flip them to whatever is in message_bits:
        data_bits_with_zeros ^ message_bits  =  0b10111000 ^ 0b10 = 0b10111010

        The LSBs bits have been set to message_bits after this operation.
        """
        below_power_of_two = np.full_like(data_slice, 2**n_bits_to_set - 1)
        flipped_last_n_bits = data_slice & below_power_of_two
        data_slice_with_zeroed_n_last_bits = data_slice ^ flipped_last_n_bits
        data_slice_with_message_bits_set = data_slice_with_zeroed_n_last_bits ^ binary_data_split_up
        return data_slice_with_message_bits_set

    def _get_bytes(self, from_amplitude: int, bits: int, lsb_count: int, nth_byte: int) -> Tuple[int, bytes]:
        """ Return bytes by reading every lsb_count bits from every nth_byte from from_amplitude """

        # Calculate number of amplitudes required for entire message (account for possible remainder)
        divisor, remainder = divmod(bits, lsb_count)
        amplitudes_required = divisor + (remainder != 0)

        # Get an array of size amplitudes_required, such that each number is 1 below a power of 2, e.g. 0b111
        ones = np.full(amplitudes_required, 2**lsb_count - 1)
        if remainder > 0:
            ones[-1] = 2**remainder - 1

        # Calculate last byte position with the given message account for nth_byte as well
        to_amplitude = from_amplitude + len(ones) * nth_byte

        # &-ing with ones will get only the relevant bits required for saving the message
        relevant_bits = self.data[from_amplitude:to_amplitude:nth_byte] & ones

        # Convert relevant_bits to a large string of bits by formatting the relevant number of bits as a string
        bits_to_format = (np.log2(ones + 1)).astype(int)
        bits_as_str = ''.join(f"{data:0{format_bits}b}" for data, format_bits in zip(relevant_bits, bits_to_format))

        # Wrap the string every 8 bits and cast each to an integer, which is then converted to bytes
        message_wrapped_as_bytes = bytes(map(lambda b: int(b, 2), textwrap.wrap(bits_as_str, 8)))
        return to_amplitude, message_wrapped_as_bytes

    def _get_message(self):
        """ Decode message from this WAVFile """
        header_bits = Message.header_byte_size() * 8
        to_byte, header_bytes = self._get_bytes(0, header_bits, Message.HEADER_LSB_COUNT, Message.HEADER_EVERY_NTH_BYTE)

        least_significant_bits, every_nth_byte, *_, data_size = Message.decode_header(header_bytes)

        message_bits = data_size * 8
        _, message_bytes = self._get_bytes(to_byte, message_bits, least_significant_bits, every_nth_byte)

        return header_bytes, message_bytes

    def decode(
            self,
            encryptor: Optional[GenericEncryptor] = None,
            error_correction: Optional[GenericErrorCorrection] = None
    ) -> bytes:
        """Decode message, getting all parameters from internal header

        Encryptor is optional, can be supplied to avoid asking for password twice when verifying.
        If Encryptor is not supplied, then it will extract the used encryptor from the header in the message.
        """

        header_bytes, data_bytes = self._get_message()

        decoded_message = Message.decode_message(header_bytes, data_bytes, encryptor, error_correction)

        return decoded_message
