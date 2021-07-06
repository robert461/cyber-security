from pathlib import Path
from tempfile import TemporaryDirectory

from wav_steganography.wav_file import WAVFile
from wav_to_mp3_to_wav.analyze_flipped_bits import find_matching_audio_file, convert_to_mp3_and_back


def compare_headers(file_path):
    with TemporaryDirectory() as tmp_dir:
        wav_file = WAVFile(file_path)
        wav_file.encode(b"ABCDEF", redundant_bits=0)
        encoded_file_path = Path(tmp_dir) / "encoded_file.wav"
        wav_file.write(encoded_file_path)
        pre_conversion, post_conversion = convert_to_mp3_and_back(encoded_file_path)
    print("=== Pre conversion ===")
    print(pre_conversion.decode())
    print("=== Post conversion ===")
    print("This crashes no matter what when using mp3")
    print(post_conversion.decode())


def main():
    compare_headers(find_matching_audio_file("sine"))


if __name__ == "__main__":
    main()