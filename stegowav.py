#!/usr/bin/python3

import argparse
from pathlib import Path
import cProfile

from security.encryption_provider import EncryptionProvider
from security.enums.encryption_type import EncryptionType
from security.enums.hash_type import HashType
from wav_steganography.wav_file import WAVFile


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Encode message into a WAV file.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("-o", "--output", type=str, help="output file path to be written to")
    parser.add_argument("-e", "--encode", type=str, help="encode given text message into wav file")
    parser.add_argument("-d", "--decode", action="store_true", help="decode a text message from wav file if possible")

    parser.add_argument("--overwrite", action="store_true",
                        help="if the file specified as output should be overwritten")

    possible_encryption_values = ', '.join(f"{enc.value}: {enc.name}" for enc in EncryptionType)
    parser.add_argument("-t", "--encryption_type", type=int, default=EncryptionType.NONE,
                        help=f"encryption type as number to use ({possible_encryption_values}). "
                             f"Certain encryptors require certain hashes!")

    possible_hash_values = ', '.join(f"{ht.value}: {ht.name}" for ht in HashType)
    parser.add_argument("-a", "--hash_type", type=int, default=HashType.PBKDF2,
                        help=f"hash type as number to use ({possible_hash_values})")

    parser.add_argument("-r", "--redundant_bits", type=int, default=0,
                        help="number of redundant bits for hamming code")

    parser.add_argument("-l", "--lsb", type=int, default=2,
                        help="number of least significant bits to use while encoding")

    parser.add_argument("--use_nth_byte", type=int, default=1,
                        help="use only every nth byte (e.g. if 4: 1 byte will be used for data, 3 will be skipped)")

    parser.add_argument("--profile", action="store_true", help="profile code (show which parts are taking long)")

    return parser.parse_args()


def handle_args(args):

    encryption_type = EncryptionType(args.encryption_type)
    hash_type = HashType(args.hash_type)

    wav_file = WAVFile(args.input)

    encryptor = EncryptionProvider.get_encryptor(encryption_type, hash_type, decryption=args.decode)

    if args.encode:
        wav_file.encode(
            args.encode.encode("UTF-8"),
            least_significant_bits=args.lsb,
            every_nth_byte=args.use_nth_byte,
            redundant_bits=args.redundant_bits,
            encryptor=encryptor,
        )

    if args.decode:
        decoded_message = wav_file.decode(encryptor=encryptor)

        decoded_string = decoded_message.decode("UTF-8")

        print(f"Decoded message (len={len(decoded_string)}):")
        print(decoded_string)

    if args.output:
        wav_file.write(Path(args.output), overwrite=args.overwrite)
        print(f"Written to {args.output}!")


def main():
    args = parse_arguments()
    if args.profile:
        with cProfile.Profile() as pr:
            handle_args(args)
        pr.print_stats()
    else:
        handle_args(args)


if __name__ == "__main__":
    main()
