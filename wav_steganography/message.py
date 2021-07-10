import struct
from typing import Union, Optional, Tuple

from error_correction.generic_error_correction import GenericErrorCorrection
from error_correction.none_error_correction import NoneErrorCorrection
from security.encryption_provider import EncryptionProvider
from security.encryptors.aes_encryptor import AesEncryptor
from security.encryptors.generic_encryptor import GenericEncryptor
from security.encryptors.none_encryptor import NoneEncryptor
from security.enums.encryption_type import EncryptionType
from security.enums.hash_type import HashType
from security.hashing.salted_hash import SaltedHash
from wav_steganography.data_chunk import DataChunk
from error_correction.hamming_error_correction import HammingErrorCorrection


class Message:
    """ A message class implementing an Encoder and an Decoder

    This header is used to encode the meta information for the message before the actual data part.
    Currently, this consists of 8 values:
        * The least significant bits used in the data
        * The nth bits used in the data
        * The number of redundant bits per byte used in the data (4 means a byte becomes 12 bits in size)
        * The encryption type (0 to 3, as defined in EncryptionType)
        * The hash type (0 to 2, as defined in HashType)
        * The password hash salt (hardcoded as 16 bytes, only used if encryption is used)
        * The nonce (hardcoded as 16 bytes, only used if encryption is AES)
        * The length of the data in bytes (excluding the header)
    For the header, the values are defined below.
    """
    HEADER_FORMAT = f"<BHHBB{SaltedHash.SALT_LENGTH}s{AesEncryptor.NONCE_LENGTH}sI"
    HEADER_LSB_COUNT = 8
    HEADER_EVERY_NTH_BYTE = 1
    HEADER_REDUNDANT_BITS = 40
    assert HEADER_REDUNDANT_BITS % 8 == 0, "header must have full bytes as redundancy"

    @staticmethod
    def header_byte_size() -> int:
        return len(Message.__encode_error_correction(b'a' * struct.calcsize(Message.HEADER_FORMAT),
                                                     Message.HEADER_REDUNDANT_BITS))

    @staticmethod
    def encode_message(
            data: Union[bytes, str],
            least_significant_bits: int,
            every_nth_byte: int,
            redundant_bits: int,
            encryptor: GenericEncryptor = NoneEncryptor(),
            error_correction: GenericErrorCorrection = NoneErrorCorrection(),
    ) -> Tuple[DataChunk, DataChunk]:

        data: bytes = Message.__message_as_bytes(data)

        # Encrypt first, then add error correction in this order
        data = Message.__encrypt(data, encryptor)
        data = Message.__encode_error_correction(data, redundant_bits)

        # Get salt/nonce values if the given encryptor has these values, otherwise use all 0 default salt/nonce
        salt = getattr(encryptor, "salt", b"0" * SaltedHash.SALT_LENGTH)
        nonce = getattr(encryptor, "nonce", b"0" * AesEncryptor.NONCE_LENGTH)
        hash_type = getattr(encryptor, "hash_type", HashType.PBKDF2)

        # Pack header data according to structure described in message
        header_data = struct.pack(
            Message.HEADER_FORMAT,
            least_significant_bits,
            every_nth_byte,
            redundant_bits,
            error_correction.error_correction_type.value,
            encryptor.encryption_type.value,
            hash_type.value,
            salt,
            nonce,
            len(data),
        )
        header_data = Message.__encode_error_correction(header_data, Message.HEADER_REDUNDANT_BITS)
        header_chunk = DataChunk(header_data, Message.HEADER_LSB_COUNT, Message.HEADER_EVERY_NTH_BYTE)
        data_chunk = DataChunk(data, least_significant_bits, every_nth_byte)
        return header_chunk, data_chunk

    @staticmethod
    def decode_header(header_bytes):
        header_bytes = Message.__decode_error_correction(header_bytes, Message.HEADER_REDUNDANT_BITS)
        return struct.unpack(Message.HEADER_FORMAT, header_bytes)

    @staticmethod
    def decode_message(
            header_bytes: bytes,
            data_bytes: bytes,
            encryptor: Optional[GenericEncryptor] = None,
            error_correction: Optional[GenericErrorCorrection] = NoneErrorCorrection(),
    ):
        *_, redundant_bits, error_correction_type, encryption_type, hash_type, salt, nonce, data_size = \
            Message.decode_header(header_bytes)

        if encryptor is None:
            encryptor = EncryptionProvider.get_encryptor(
                EncryptionType(encryption_type),
                HashType(hash_type),
                decryption=True,
                salt=salt,
                nonce=nonce,
            )

        data = Message.__decode_error_correction(data_bytes, redundant_bits, error_correction)
        data = Message.__decrypt(data, encryptor)

        return data

    @staticmethod
    def __decode_error_correction(
            data: bytes,
            redundant_bits: int,
            error_correction: Optional[GenericErrorCorrection] = NoneErrorCorrection()):

        data = error_correction.decode(data, redundant_bits)

        return data

    @staticmethod
    def __correct_errors_hamming(data: bytes, redundant_bits: int):

        data = HammingErrorCorrection.correct_errors_hamming(data, redundant_bits)

        return data

    @staticmethod
    def __encrypt(data: bytes, encryptor: Optional[GenericEncryptor]) -> bytes:

        encrypted_data = encryptor.encrypt(data)

        return encrypted_data

    @staticmethod
    def __decrypt(data: bytes, encryptor: Optional[GenericEncryptor]) -> bytes:

        data = encryptor.decrypt(data)
        return data

    @staticmethod
    def __encode_error_correction(
            data: bytes,
            redundant_bits: int,
            error_correction: Optional[GenericErrorCorrection] = NoneErrorCorrection()) -> bytes:

        data_error_corrected = error_correction.encode(data, redundant_bits)
        assert len(data_error_corrected) != 0, f"data is empty after error correction: {data_error_corrected}"

        return data_error_corrected

    @staticmethod
    def __message_as_bytes(message: Union[bytes, str]):
        if isinstance(message, str):
            message = message.encode("UTF-8")

        return message
