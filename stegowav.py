#!/usr/bin/python3

import argparse
from pathlib import Path

from encryption.encryption_provider import EncryptionProvider
from encryption.encryption_type import EncryptionType
from wav_steganography.wav_file import WAVFile


def main():
    parser = argparse.ArgumentParser(description="Encode message into a WAV file.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("-o", "--output", type=str, help="output file path")
    parser.add_argument("--overwrite", action="store_true",
                        help="if the file specified as output should be overwritten")
    parser.add_argument("-e", "--encode", type=str, help="encode text message into wav file")
    parser.add_argument("-d", "--decode", action="store_true", help="decode text message from wav file")
    parser.add_argument("-t", "--encryption_type", type=int, help="encryption type to use/used")
    parser.add_argument("-r", "--redundant_bits", type=int, help="number of redundant bits for hamming code")
    parser.add_argument("-c", "--compare", type=bool,
                        help="use argument 'True' for error correction using hamming codes")

    args = parser.parse_args()

    wav_file = WAVFile(args.input)

    if args.encryption_type:
        encryption_type = EncryptionType(args.encryption_type)
    else:
        encryption_type = EncryptionType.NONE

    if args.redundant_bits:
        redundant_bits = args.redundant_bits
    else:
        redundant_bits = 4

    if args.encode:
        wav_file.encode(args.encode.encode("UTF-8"), redundant_bits=redundant_bits, encryption_type=encryption_type)

    # TODO Encryption Type workaround
    if args.decode:
        encryptor = EncryptionProvider.get_encryptor(encryption_type=encryption_type)
        if encryptor:
            encryptor.configure(True)

        decoded_message = wav_file.decode(redundant_bits=redundant_bits, encryptor=encryptor).decode("UTF-8")

        print(f"Decoded message (len={len(decoded_message)}):")
        print(decoded_message)

    if args.output:
        wav_file.write(Path(args.output), overwrite=args.overwrite)
        print(f"Written to {args.output}!")

    if args.compare:
        encryptor = EncryptionProvider.get_encryptor(encryption_type)
        if encryptor:
            encryptor.configure(True)

        corrected_message = wav_file.correct_errors_hamming(
                wav_file, redundant_bits=redundant_bits, encryptor=encryptor).decode("UTF-8")

        print(f"Corrected decoded message (len={len(corrected_message)}):")
        print(corrected_message)


if __name__ == "__main__":
    main()
