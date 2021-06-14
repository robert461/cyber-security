import textwrap
from collections import OrderedDict
from pathlib import Path
import struct
from typing import Optional, Union, List, Tuple

import numpy as np
import pandas as pd

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

    def plot(self, from_s: float = 0.0, to_s: Optional[float] = 0.1, filename: Union[Path, str] = None):
        """ Create a plot of the audio with the given time-frame """
        import seaborn as sns
        from matplotlib import pyplot as plt
        sns.set_theme()
        sns.relplot(data=self.slice(from_s, to_s), kind="line")
        if filename is None:
            plt.show()
        else:
            plt.savefig(filename)

    def encode(
            self,
            message: bytes,
            least_significant_bits: int = 2,
            every_nth_byte: int = 1,
            password: Optional[str] = None
    ):
        """ Encode a message in the given WAVFile

        This is done by writing to every nth bytes some number of least significant bits.
        A short header is written first, then the message.
        """
        assert least_significant_bits <= self.header["BitsPerSample"]
        message_encoder = Message.Encoder(least_significant_bits, every_nth_byte, password)
        byte_index = 0
        header, data = message_encoder.encode(message)
        for chunk in [header, data]:
            nth = chunk.every_nth_byte
            binary_data = ''.join(map(lambda b: f"{b:08b}", chunk.data))  # e.g. "0010101011101100"
            lsb_bits = textwrap.wrap(binary_data, chunk.least_significant_bits)  # e.g. ["00", "10", ...]
            binary_data_split_up = list(map(lambda b: int(b, 2), lsb_bits))  # e.g. [0, 2, ...]
            end_byte_index = len(binary_data_split_up) * nth + byte_index  # e.g. 32 on first iteration
            self.data[byte_index:end_byte_index:nth] = [
                self._set_last_n_bits(data_bits, message_bits, chunk.least_significant_bits)
                for message_bits, data_bits in zip(binary_data_split_up, self.data[byte_index:end_byte_index:nth])
            ]
            byte_index = end_byte_index
        assert self.decode() == message, f'Cannot decode encrypted message: "{self.decode()}" != "{message}"'

    @staticmethod
    def _set_last_n_bits(data_bits: int, message_bits: int, n_bits_to_set: int) -> int:
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
        return data_bits ^ (data_bits & (2 ** n_bits_to_set - 1)) ^ message_bits

    def _get_bytes(self, from_byte: int, to_byte: int, lsb_count: int, nth_byte: int) -> bytes:
        """ Return bytes by reading every lsb_count bits from every nth_byte from from_byte to to_byte """
        ones = 2 ** lsb_count - 1
        bits_as_str = ''.join(f"{b & ones:0{lsb_count}b}" for b in self.data[from_byte:to_byte:nth_byte])
        return bytes(map(lambda b: int(b, 2), textwrap.wrap(bits_as_str, 8)))

    def decode(self, password: Optional[str] = None) -> bytes:
        """ Decode message from this WAVFile """
        header_bit_count = Message.HEADER_BYTE_SIZE * 8
        header_bytes = self._get_bytes(0, header_bit_count, 1, 1)

        decoder = Message.Decoder(header_bytes, password=password)
        message_end_bit = (
            decoder.every_nth_byte * decoder.data_size * 8 // decoder.least_significant_bits
            + header_bit_count
        )
        message_bytes = self._get_bytes(header_bit_count, message_end_bit, decoder.least_significant_bits,
                                        decoder.every_nth_byte)
        return decoder.decode(message_bytes)
