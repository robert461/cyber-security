import hashlib
import random
import string
from pathlib import Path

from wav_steganography.wav_file import WAVFile

audio_path = Path("audio")


def test_loading_and_plotting_wav_file():
    for audio_file in audio_path.glob("*.wav"):
        print(f"Loading audio file {audio_file}")
        file = WAVFile(audio_file)
        plots_path = audio_path / 'plots'
        plots_path.mkdir(exist_ok=True)
        file.plot(to_s=None, filename=plots_path / audio_file.name.replace(".wav", ".png"))


def test_loading_and_writing_wav_file():
    for audio_file in audio_path.glob("*.wav"):
        md5checksum = hashlib.md5(open(audio_file, 'rb').read()).hexdigest()
        print(f"Loading audio file {audio_file}")
        file = WAVFile(audio_file)
        written_path = audio_path / 'copied'
        written_path.mkdir(exist_ok=True)
        copied_file_path = written_path / audio_file.name
        file.write(copied_file_path, overwrite=True)
        copied_md5checksum = hashlib.md5(open(copied_file_path, 'rb').read()).hexdigest()
        assert md5checksum == copied_md5checksum, "Checksums mismatch!"


def test_encoding_decoding():
    def get_random_string() -> str:
        return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(100, 1000)))
    for audio_file in audio_path.glob("*.wav"):
        file = WAVFile(audio_file)
        message = get_random_string()
        file.encode(message, least_significant_bits=4)
        encoded_file_path = audio_path / "encoded" / audio_file.name
        file.write(encoded_file_path, overwrite=True)
        encoded_file = WAVFile(encoded_file_path)
        assert encoded_file.decode() == message, "Decoded message is not the same as the encoded one!"
