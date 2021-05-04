import textwrap
from collections import OrderedDict
from pathlib import Path
import struct
from typing import Optional, Union, List, Tuple

import numpy as np
import pandas as pd


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

    _encoding_header_specification: List[Tuple[str, str, int]] = [
        ("LeastSignificantBits", '<B', 1),
        ("EveryNthByte", '<H', 2),
        ("MessageSizeInBytes", '<I', 4),
    ]

    def __init__(self, filename: Path):
        """
        :param filename: path to WAV audio file
        """
        self._parse_file(filename)

    def _parse_file(self, filename: Union[Path, str]):
        self.header = h = OrderedDict()
        with open(filename, 'rb') as wav_file:

            # Parse according to specification
            for name, formatting, byte_count, allowed_values in self._wav_header_specification:
                h[name] = struct.unpack(formatting, wav_file.read(byte_count))[0]
                if allowed_values is not None:
                    assert h[name] in allowed_values, f"{name} is {h[name]}, not among {allowed_values}!"
                print(f"{name} parsed as {h[name]}")

            # Make assertions about expected size
            assert h["BlockAlign"] == h['NumChannels'] * h['BitsPerSample'] // 8
            assert h["ByteRate"] == h['SampleRate'] * h['NumChannels'] * h['BitsPerSample'] // 8
            assert h["ChunkSize"] == h["Subchunk2Size"] + 36

            # Parse the actual data
            data_arr = np.array(struct.unpack(self._get_data_format(), wav_file.read(h['Subchunk2Size'])))
            self.data = pd.DataFrame(data={
                f"channel_{i}": data_arr[i::h['NumChannels']].flatten()
                for i in range(0, h['NumChannels'])
            })
            print(self.data)

    def _get_data_format(self) -> str:
        """ Returns the data format string required for struct (e.g. "<88200h") """
        endianness = ('<' if self.header["ChunkID"] == b"RIFF" else ">")
        integer_count = self.header['Subchunk2Size'] * 8 // self.header['BitsPerSample']
        integer_size = {8: 'b', 16: 'h', 32: 'i'}[self.header['BitsPerSample']]
        return f"{endianness}{integer_count}{integer_size}"

    def write(self, filename: Union[Path, str]):
        with open(filename, 'wb') as file:
            for name, formatting, byte_count, allowed_values in self._wav_header_specification:
                assert name in self.header, f"Parameter {name} not found in header!"
                print(self.header[name])
                file.write(struct.pack(formatting, self.header[name]))
            data = list(self.data.to_numpy().flatten())
            file.write(struct.pack(self._get_data_format(), *data))

    def time_to_index(self, at_time_s: float) -> int:
        """ Returns index of data, given as second, if None then returns len """
        if at_time_s is None:
            return len(self.data)
        return round(at_time_s * len(self.data))

    def slice(self, from_s: float = 0.0, to_s: Optional[float] = None) -> np.array:
        """ Returns a slice of the given data between interval in seconds """
        from_i = self.time_to_index(from_s)
        to_i = self.time_to_index(to_s)
        assert from_i < to_i, f"Invalid interval, {from_i} >= {to_i}!"
        return self.data[from_i:to_i]

    def plot(self, from_s: float = 0.0, to_s: Optional[float] = 0.1, filename: Union[Path, str] = None):
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
            message: Union[bytes, str],
            least_significant_bits: int = 2,
            every_nth_byte: int = 1,
            password: Optional[str] = None
    ):
        if isinstance(message, str):
            message = bytes(message, encoding="utf-8")

        assert least_significant_bits <= self.header["BitsPerSample"]

        lookup = {
            "LeastSignificantBits": least_significant_bits,
            "EveryNthByte": every_nth_byte,
            "MessageSizeInBytes": len(message),
        }
        encoded_header = b''.join(
            struct.pack(formatting, lookup[name])
            for name, formatting, byte_count in self._encoding_header_specification
        )

        encrypted_header = encoded_header
        encrypted_message = message
        if password is not None:
            pass  # TODO add encryption

        print(encrypted_header, encrypted_message)
        byte_data = encrypted_header + encrypted_message
        binary_data = ''.join(map(lambda b: f"{b:#010b}"[2:], byte_data))
        print(binary_data)
        binary_data_split_up = map(lambda b: int(b, 2), textwrap.wrap(binary_data, 2))
        #for channel in self.header['NumChannels']:
            #self.data[0:, channel] =




