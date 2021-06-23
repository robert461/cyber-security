import os
import argparse

from wav_steganography.wav_file import WAVFile


input_path = ""
output_path = ""
encode_path = ""

audiofiles = []
filenames = []
count = 0


parser = argparse.ArgumentParser(description="start the encode script")
parser.add_argument("encode", type=str, help="name of the encode txt-file")
parser.add_argument("output", type=str, help="name of the output directory")
args = parser.parse_args()

encode_filename = str(args.encode)
output_directory = str(args.output)

directory = "audio\\1min_files"
for entry in os.scandir(directory):
    if entry.path.endswith(".wav") and entry.is_file():
        audiofiles.append(entry.path)
        filenames.append(os.path.basename(entry.path))

for element in audiofiles:
    input_path = element
    print("I: " + input_path)
    if not os.path.exists("audio\\evaluation_samples\\" + output_directory):
        os.makedirs("audio\\evaluation_samples\\" + output_directory)
    output_path = "audio\\evaluation_samples\\" + output_directory + "\\modified_" + filenames[count]
    print("O: " + output_path)
    encode_path = "audio\\txt_files\\" + encode_filename
    print("E: " + encode_path + "\n")

    wav_file = WAVFile(input_path)
    wav_file.encode(open(encode_path, 'r').read().encode("UTF-8"), )
    wav_file.write(output_path, True)

    count = count + 1