from collections import OrderedDict
from pathlib import Path
import struct
from typing import Optional, Union

import numpy as np
import pandas as pd


class WAVFile:
    """ Basic WAV Audio File Parser

    Reference: http://soundfile.sapp.org/doc/WaveFormat/
    Helpful video: https://www.youtube.com/watch?v=udbA7u1zYfc

    The WAV header specification was created based on the reference above.
    Each entry is formatted as follows:

        (name, format, byte_count, [allowed_values])

    If instead of `[allowed_values]` `None` is supplied, then no check is made.
    """

    _wav_header_specification: list[tuple[str, str, int, Optional[list]]] = [
        # === RIFF Chunk ===
        ("ChunkID", '>c', 4, [b"RIFF", b"RIFX"]),
        ("ChunkSize", '<i', 4, None),
        ("Format", '>c', 4, [b"WAVE"]),

        # === FORMAT Subchunk ===
        ("Subchunk1ID", '>c', 4, [b"fmt "]),
        ("Subchunk1Size", '<i', 4, [16]),
        ("AudioFormat", '<h', 2, [1]),
        ("NumChannels", '<h', 2, [1, 2]),
        ("SampleRate", '<i', 4, None),
        ("ByteRate", '<i', 4, None),
        ("BlockAlign", '<h', 2, None),
        ("BitsPerSample", '<h', 2, [8, 16, 32]),

        # === DATA Subchunk ===
        ("Subchunk2ID", '>c', 4, [b"data"]),
        ("Subchunk2Size", '<i', 4, None),
    ]

    def __init__(self, filename: Path):
        """
        :param filename: path to WAV audio file
        :return: numpy array of data
        """
        self._parse_file(filename)

    def _parse_file(self, filename: Path):
        self.header = h = OrderedDict()
        with open(filename, 'rb') as wav_file:

            # Parse according to specification
            for name, formatting, byte_count, allowed_values in self._wav_header_specification:
                value_as_list = [e[0] for e in struct.iter_unpack(formatting, wav_file.read(byte_count))]
                value = (value_as_list[0] if len(value_as_list) == 1 else b''.join(value_as_list))
                h[name] = value
                if allowed_values is not None:
                    assert value in allowed_values, f"{name} is {value}, not among {allowed_values}!"
                print(f"{name} parsed as {value}")

            # Make assertions about expected size
            num_channels = h['NumChannels']
            bits_per_sample = h['BitsPerSample']
            sample_rate = h['SampleRate']
            assert h["BlockAlign"] == num_channels * bits_per_sample // 8, "BlockAlign mismatch."
            assert h["ByteRate"] == sample_rate * num_channels * bits_per_sample // 8, "ByteRate mismatch."
            assert h["ChunkSize"] == h["Subchunk2Size"] + 36, "Size mismatch."

            # Parse the actual data
            data_formatting = ('<' if h["ChunkID"] == b"RIFF" else ">")
            data_formatting += {8: 'b', 16: 'h', 32: 'i'}[bits_per_sample]
            data_arr = np.array(list(struct.iter_unpack(data_formatting, wav_file.read(h['Subchunk2Size']))))
            data_dict = {}
            step_size = h["Subchunk2Size"] * 8 // num_channels // bits_per_sample
            for i in range(0, num_channels):
                at = i * step_size
                data_dict[f"channel_{i}"] = data_arr[at:at+step_size].flatten()
            self.data = pd.DataFrame(data=data_dict)
            print(self.data)

    def time_to_index(self, second: float) -> int:
        """ Returns index of data, given as second, if None then returns len """
        if second is None:
            return len(self.data)
        return round(second * len(self.data))

    def slice(self, from_s: float = 0.0, to_s: float = None) -> np.array:
        """ Returns a slice of the given data between interval in seconds """
        assert from_s < to_s, f"Invalid interval, {from_s} >= {to_s}!"
        from_i = self.time_to_index(from_s)
        to_i = self.time_to_index(to_s)
        return self.data[from_i:to_i]

    def plot(self, from_s: float = 0.0, to_s: float = 0.1, filename: Union[Path, str] = None):
        assert from_s < to_s, f"Invalid interval, {from_s} >= {to_s}!"
        import seaborn as sns
        from matplotlib import pyplot as plt

        sns.set_theme()
        sns.relplot(data=self.slice(from_s, to_s), kind="line")
        if filename is None:
            plt.show()
        else:
            plt.savefig(filename)
