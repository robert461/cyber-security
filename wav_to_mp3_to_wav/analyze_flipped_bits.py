from pathlib import Path
from tempfile import TemporaryDirectory

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


def find_matching_audio_file(substring_of_filename: str):
    for stem, path in all_audio_files.items():
        if substring_of_filename in stem:
            return path


def comparison_pre_and_after_mp3_conversion(file_path, bitrate="312k", print_=False):
    with TemporaryDirectory() as tmp_dir:
        audio_file = AudioSegment.from_file(file_path)
        mp3_file_path = Path(tmp_dir) / "converted.mp3"
        audio_file.export(mp3_file_path, format="mp3", bitrate=bitrate)

        mp3_file = AudioSegment.from_file(mp3_file_path)
        mp3_file.export(mp3_file_path.with_suffix(".wav"), format="wav")

        pre_conversion = WAVFile(file_path)
        after_conversion = WAVFile(mp3_file_path.with_suffix(".wav"))

        pre_data = pre_conversion.data
        after_data = after_conversion.data

        total = len(pre_data)
        percentages = []
        for bit in range(16):
            power = 1 << bit
            correct = np.sum(pre_data & power == after_data & power)
            percent = correct / total
            percentages.append(percent)
            if print_:
                print(f"Bit {bit+1} ({power}): {correct:,d} are the same out of {total:,d} ({percent:.1%})")
        return percentages


def plot_bit_percentages_for_file(curr_file_path: Path, show=False):
    if curr_file_path:
        possible_bitrates = ["64k", "92k", "128k", "256k", "312k"]
        data = {}
        for bitrate in possible_bitrates:
            percentages = comparison_pre_and_after_mp3_conversion(curr_file_path, bitrate=bitrate)
            percentages.reverse()
            data[bitrate] = percentages
        dataframe = pd.DataFrame.from_dict(data, orient="index", columns=range(16, 0, -1))
        # dataframe = (dataframe - 0.5) * 2
        # dataframe = dataframe.clip(0, 1)
        # dataframe = np.clip(dataframe, 0, 1)
        print(dataframe)
        # dataframe.plot(kind="scatter")
        matplotlib.rcParams["font.size"] = "5"
        plt.imshow(dataframe, vmin=0.5, vmax=1)
        for (j, i), label in np.ndenumerate(dataframe.round(2)):
            plt.text(i, j, label, ha='center', va='center')
            plt.text(i, j, label, ha='center', va='center')
        plt.xticks(*list(zip(*enumerate(dataframe.columns))))
        plt.xlabel("bit")
        plt.yticks(*list(zip(*enumerate(dataframe.index.values))))
        plt.ylabel("MP3 bitrate")
        plt.title(f"Comparison of Equal Bits in WAv -> MP3 -> WAV Conversion for File {curr_file_path.name}")
        # f"The numbers show the percentage of equal bits pre/post comparison. "
        # f"1.0 means all bits are the same, 0.5 means that it is essentially random."
        figure_path = Path(__file__).parent / "figures" / curr_file_path.with_suffix(".png").name
        print(f"Saving figure {figure_path}")
        figure_path.parent.mkdir(exist_ok=True)
        plt.savefig(figure_path, dpi=300)
        if show:
            plt.show()
        plt.close()


def main():
    # curr_file_substring = "jetengine1"
    for path in all_audio_files.values():
        plot_bit_percentages_for_file(path)


if __name__ == "__main__":
    main()
