#!/usr/bin/python3

import argparse
from pathlib import Path

from security.encryption_provider import EncryptionProvider
from security.enums.encryption_type import EncryptionType
from security.enums.hash_type import HashType
from wav_steganography.wav_file import WAVFile


def main():
    parser = argparse.ArgumentParser(description="Encode message into a WAV file.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("-o", "--output", type=str, help="output file path")
    parser.add_argument("--overwrite", action="store_true",
                        help="if the file specified as output should be overwritten")
    parser.add_argument("-e", "--encode", type=str, help="encode text message into wav file")
    parser.add_argument("-d", "--decode", action="store_true", help="decode text message from wav file")

    possible_encryption_values = ', '.join(f"{enc.value}: {enc.name}" for enc in EncryptionType)
    possible_hash_values = ', '.join(f"{ht.value}: {ht.name}" for ht in HashType)
    parser.add_argument("-t", "--encryption_type", type=int, default=EncryptionType.NONE,
                        help=f"encryption type as number to use ({possible_encryption_values}). "
                             f"Certain encryptors require certain hashes!")
    parser.add_argument("-a", "--hash_type", type=int, default=HashType.PBKDF2,
                        help=f"hash type as number to use ({possible_hash_values})")

    parser.add_argument("-r", "--redundant_bits", type=int, default=4,
                        help="number of redundant bits for hamming code")
    parser.add_argument("-c", "--error_correction", action="store_true",
                        help="add error correction using hamming codes")

    args = parser.parse_args()

    encryption_type = EncryptionType(args.encryption_type)
    hash_type = HashType(args.hash_type)

    decryption = False
    if args.decode:
        decryption = True

    encryptor = EncryptionProvider.get_encryptor(encryption_type, hash_type, decryption)

    wav_file = WAVFile(args.input, encryptor)

    redundant_bits = args.redundant_bits
    error_correction = args.error_correction

    if args.encode:
        wav_file.encode(
            args.encode.encode("UTF-8"),
            redundant_bits = redundant_bits,
            error_correction = error_correction)

    if args.decode:
        decoded_message = wav_file.decode(
            redundant_bits=redundant_bits,
            error_correction=error_correction)

        decoded_string = decoded_message.decode("UTF-8")

        print(f"Decoded message (len={len(decoded_string)}):")
        print(decoded_string)

    if args.output:
        wav_file.write(Path(args.output), overwrite=args.overwrite)
        print(f"Written to {args.output}!")


if __name__ == "__main__":
    main()
