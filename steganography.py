#!/usr/bin/python3

import argparse

from wav_steganography.wav_file import WAVFile


def main():
    parser = argparse.ArgumentParser(description="Encode message into a WAV file.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("-o", "--output", type=str, help="output file path")
    parser.add_argument("-e", "--encode", type=str, help="encode message into wav file")
    parser.add_argument("-d", "--decode", type=bool, help="decode message from wav file")
    parser.add_argument("-p", "--password", type=bool, help="encrypt message with a password (will ask for password)")
    args = parser.parse_args()
    wav_file = WAVFile(args.input)
    wav_file.encode(args.encode)


if __name__ == "__main__":
    main()
