import hashlib
import random
import string
from pathlib import Path

import pytest

from security.encryption_provider import EncryptionProvider
from security.encryptors.none_encryptor import NoneEncryptor
from security.encryptors.rsa_encryptor import RsaEncryptor
from security.enums.encryption_type import EncryptionType
from security.enums.hash_type import HashType
from wav_steganography.wav_file import WAVFile

audio_path = Path("audio")


def get_random_string(position_of_element: int) -> str:
    return ''.join(random.choice(string.ascii_letters) for _ in
                   range(random.randint(position_of_element, position_of_element)))


def get_file_path(filename):
    encoded_dir_path = audio_path / "encoded"
    encoded_dir_path.mkdir(exist_ok=True)
    encoded_file_path = encoded_dir_path / filename

    return encoded_file_path


def test_loading_and_plotting_wav_file():
    for audio_file in audio_path.glob("*.wav"):
        print(f"Loading audio file {audio_file}")
        file = WAVFile(audio_file, NoneEncryptor())
        plots_path = audio_path / 'plots'
        plots_path.mkdir(exist_ok=True)
        file.plot(to_s=None, filename=plots_path / audio_file.name.replace(".wav", ".png"))


def test_loading_and_writing_wav_file():
    for audio_file in audio_path.glob("*.wav"):
        md5checksum = hashlib.md5(open(audio_file, 'rb').read()).hexdigest()
        print(f"Loading audio file {audio_file}")
        file = WAVFile(audio_file, NoneEncryptor())
        written_path = audio_path / 'copied'
        written_path.mkdir(exist_ok=True)
        copied_file_path = written_path / audio_file.name
        file.write(copied_file_path, overwrite=True)
        copied_md5checksum = hashlib.md5(open(copied_file_path, 'rb').read()).hexdigest()
        assert md5checksum == copied_md5checksum, "Checksums mismatch!"


def test_encoding_decoding():
    for audio_file in audio_path.glob("*.wav"):
        file = WAVFile(audio_file, NoneEncryptor())

        data_string = get_random_string(10000)
        data = data_string.encode("UTF-8")

        file.encode(data)

        encoded_file_path = get_file_path(audio_file.name)

        file.write(encoded_file_path, overwrite=True)

        encoded_file = WAVFile(encoded_file_path, NoneEncryptor())

        decoded_data = encoded_file.decode()

        assert \
            decoded_data == data, "Decoded message is not the same as the encoded one!"


def single_test_encoding_decoding_with_error_correction(audio_file, data, encryptor):
    file = WAVFile(audio_file, encryptor)
    encoded_file_path = get_file_path(audio_file.name)

    file.encode(data, redundant_bits=9)
    file.write(encoded_file_path, overwrite=True)

    encoded_file = WAVFile(encoded_file_path, NoneEncryptor())
    decoded_data = encoded_file.decode()

    return decoded_data


def test_multiple_encoding_decoding_with_error_correction():
    for audio_file in audio_path.glob("*.wav"):
        data_string = get_random_string(1000)
        data = data_string.encode("UTF-8")

        decoded_data = single_test_encoding_decoding_with_error_correction(audio_file, data, NoneEncryptor())

        assert \
            decoded_data == data, "Decoded and corrected message is not the same as the encoded one!"


def test_multiple_encoding_with_error_correction_and_encryption():
    fernet_pbkdf2_encryptor = EncryptionProvider.get_encryptor(EncryptionType.FERNET, HashType.PBKDF2, is_test=True)
    fernet_scrypt_encryptor = EncryptionProvider.get_encryptor(EncryptionType.FERNET, HashType.SCRYPT, is_test=True)
    aes_pbkdf2_encryptor = EncryptionProvider.get_encryptor(EncryptionType.AES, HashType.PBKDF2, is_test=True)
    aes_scrypt_encryptor = EncryptionProvider.get_encryptor(EncryptionType.AES, HashType.SCRYPT, is_test=True)
    rsa_encryptor = EncryptionProvider.get_encryptor(EncryptionType.RSA, is_test=True)

    encryptors = [fernet_pbkdf2_encryptor, fernet_scrypt_encryptor,
                  aes_pbkdf2_encryptor, aes_scrypt_encryptor, rsa_encryptor]

    for encryptor in encryptors:

        for audio_file in audio_path.glob("*.wav"):

            if type(encryptor) == RsaEncryptor:
                data_length = 100
            else:
                data_length = 1000

            data_string = get_random_string(data_length)
            data = data_string.encode("UTF-8")

            file = WAVFile(audio_file, encryptor)
            file.encode(data, redundant_bits=8)


def test_multiple_encoding_decoding_with_error_correction_and_oversized_data():
    with pytest.raises(ValueError):
        for audio_file in audio_path.glob("*.wav"):
            data_string = get_random_string(10000)
            data = data_string.encode("UTF-8")

            single_test_encoding_decoding_with_error_correction(audio_file, data, NoneEncryptor())
