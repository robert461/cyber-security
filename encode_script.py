import os
import argparse

from wav_steganography.wav_file import WAVFile
from pathlib import Path

audiofiles = []
filenames = []

parser = argparse.ArgumentParser(description="start the encode script")
parser.add_argument("encode", type=str, help="name of the encode txt-file")
parser.add_argument("--single", action="store_true",
                    help="encode a txt file into all samples, with a specific number of LSBs converted")
parser.add_argument("-l", "--lsb", type=int, help="sets the number of LSBs used for single file encoding")
parser.add_argument("-o", "--output", type=str, help="name of the output directory")
parser.add_argument("--all", action="store_true",
                    help="encode a txt file into all samples, iterate over all possible LSBs")

args = parser.parse_args()

encode_directory = Path("audio") / "txt_files" / args.encode

for entry in Path("audio/1min_files").glob("*.wav"):
    audiofiles.append(entry)
    filenames.append(entry.name)


# encode a file into all audio files with a specific number of LSBs converted
def encode_single_lsb(out, lsb):
    count = 0
    for element in audiofiles:
        encode_file(element, str(out) + "/modified_" + filenames[count], lsb)
        count = count + 1


# encode a file into all audio files, iterate over all LSBs possible
def encode_all_lsb():
    number_of_lsb = 1
    while number_of_lsb <= 15:
        print(f"\n----- Number of LSBs used for encoding: {number_of_lsb} -----\n")

        lsb_directory = "lsb_" + str(number_of_lsb)
        output = Path("audio") / "evaluation_samples" / lsb_directory
        if not Path.exists(output):
            output.mkdir()

        encode_single_lsb(output, number_of_lsb)
        number_of_lsb = number_of_lsb + 1


def encode_file(input_dir, output, lsb):
    print(f"I: {input_dir}")
    print(f"O: {output}")
    print(f"E: {encode_directory}\n")
    wav_file = WAVFile(input_dir)
    wav_file.encode(open(encode_directory, 'r').read().encode("UTF-8"), least_significant_bits=lsb)
    wav_file.write(output, True)


if args.single:
    output_directory = Path("audio") / "evaluation_samples" / args.output
    if not Path.exists(output_directory):
        output_directory.mkdir()
    encode_single_lsb(output_directory, args.lsb)
if args.all:
    encode_all_lsb()
