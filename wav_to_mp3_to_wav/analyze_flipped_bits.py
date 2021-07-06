from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Tuple, List, Optional

import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pydub import AudioSegment

from wav_steganography.wav_file import WAVFile

audio_files = Path(__file__).parent.parent / "audio"

all_audio_files = {}
for glob in ["*.wav", "1min_files/*.wav"]:
    for curr_path in audio_files.glob(glob):
        all_audio_files[curr_path.stem] = curr_path


def find_matching_audio_file(substring_of_filename: str) -> Path:
    for stem, path in all_audio_files.items():
        if substring_of_filename in stem:
            return path


def convert_to_file_format_and_back(file_path, bitrate=None, file_format="mp3") -> Tuple[WAVFile, WAVFile]:
    with TemporaryDirectory() as tmp_dir:
        audio_file = AudioSegment.from_file(file_path)
        mp3_file_path = Path(tmp_dir) / f"converted.{file_format}"
        audio_file.export(mp3_file_path, format=file_format, bitrate=bitrate)

        mp3_file = AudioSegment.from_file(mp3_file_path)
        mp3_file.export(mp3_file_path.with_suffix(".wav"), format="wav")

        pre_conversion = WAVFile(file_path)
        after_conversion = WAVFile(mp3_file_path.with_suffix(".wav"))
        return pre_conversion, after_conversion


def comparison_pre_and_after_mp3_conversion(file_path, bitrate=None, print_=False) -> Optional[List[float]]:
    pre_conversion, after_conversion = convert_to_file_format_and_back(file_path, bitrate)

    pre_data = pre_conversion.data
    after_data = after_conversion.data

    total = len(pre_data)
    percentages = []
    if len(pre_data) != len(after_data):
        print(f"Shape mismatch pre-conversion: {len(pre_data)} with post-conversion: {len(after_data)}, skipping!")
        return None
    print(f"Average difference (bitrate={bitrate}): {np.average(np.abs(pre_data - after_data)):.1f}")
    for bit in range(16):
        power = 1 << bit

        correct = np.sum(pre_data & power == after_data & power)
        percent = correct / total
        percentages.append(percent)
        if print_:
            print(f"Bit {bit + 1} ({power}): {correct:,d} are the same out of {total:,d} ({percent:.1%})")
    return percentages


def plot_bit_percentages_for_file(curr_file_path: Path, show=False):
    if curr_file_path:
        figure_path = Path(__file__).parent / "figures" / curr_file_path.with_suffix(".png").name
        print(f"Saving figure {figure_path}")
        possible_bitrates = ["64k", "92k", "128k", "256k", "312k"]
        data = {}
        for bitrate in possible_bitrates:
            percentages = comparison_pre_and_after_mp3_conversion(curr_file_path, bitrate=bitrate)
            if percentages is None:
                return
            percentages.reverse()
            data[bitrate] = percentages
        dataframe = pd.DataFrame.from_dict(data, orient="index", columns=range(16, 0, -1))
        matplotlib.rcParams["font.size"] = "5"
        plt.imshow(dataframe, vmin=0.5, vmax=1)
        for (j, i), label in np.ndenumerate(dataframe.round(2)):
            plt.text(i, j, label, ha='center', va='center')
            plt.text(i, j, label, ha='center', va='center')
        plt.xticks(*zip(*enumerate(dataframe.columns)))
        plt.xlabel("bit")
        plt.yticks(*zip(*enumerate(dataframe.index.values)))
        plt.ylabel("MP3 bitrate")
        plt.title(f"Comparison of Equal Bits in WAV -> MP3 -> WAV Conversion for File '{curr_file_path.name}'")
        # f"The numbers show the percentage of equal bits pre/post comparison. "
        # f"1.0 means all bits are the same, 0.5 means that it is essentially random."
        print(dataframe)
        plt.tight_layout()
        figure_path.parent.mkdir(exist_ok=True)
        plt.savefig(figure_path, dpi=300, pad_inches=0)
        if show:
            plt.show()
        plt.close()


def main():
    for path in all_audio_files.values():
        plot_bit_percentages_for_file(path)


if __name__ == "__main__":
    main()
