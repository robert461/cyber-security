import struct
from typing import Union, Optional, Tuple

from error_correction.reed_solomon import ReedSolomon
from security.encryption_provider import EncryptionProvider
from security.encryptors.generic_encryptor import GenericEncryptor
from security.encryptors.none_encryptor import NoneEncryptor
from security.enums.encryption_type import EncryptionType
from wav_steganography.data_chunk import DataChunk
from error_correction.hamming_error_correction import HammingErrorCorrection


class Message:
    """ A message class implementing an Encoder and an Decoder

    This header is used to encode the meta information for the message before the actual data part.
    Currently, this consists of 7 values:
        * The least significant bits used in the data
        * The nth bits used in the data
        * The number of redundant bits per byte used in the data (4 means a byte becomes 12 bits in size)
        * The encryption type (0 to 3, as defined in EncryptionType)
        * The password hash salt (hardcoded as 16 bytes, only used if encryption is used)
        * The nonce (hardcoded as 16 bytes, only used if encryption is AES)
        * The length of the data in bytes (excluding the header)
    For the header, the values are defined below.
    """
    HEADER_FORMAT = "<BHHB16s16sI"
    HEADER_LSB_COUNT = 8
    HEADER_EVERY_NTH_BYTE = 1
    HEADER_REDUNDANT_BITS = 0
    assert HEADER_REDUNDANT_BITS % 8 == 0, "header must have full bytes as redundancy"
    HEADER_BYTE_SIZE = struct.calcsize(HEADER_FORMAT) * (1 + HEADER_REDUNDANT_BITS // 8)

    @staticmethod
    def encode_message(
            data: Union[bytes, str],
            least_significant_bits: int,
            every_nth_byte: int,
            redundant_bits: int,
            encryptor: GenericEncryptor = NoneEncryptor(),
    ) -> Tuple[DataChunk, DataChunk]:

        data: bytes = Message.__message_as_bytes(data)

        # Encrypt first, then add error correction in this order
        data = Message.__encrypt(data, encryptor)
        data = Message.__encode_error_correction(data, redundant_bits)

        header_data = struct.pack(
            Message.HEADER_FORMAT,
            least_significant_bits,
            every_nth_byte,
            redundant_bits,
            encryptor.encryption_type.value,
            b"0" * 16,  # salt TODO: encryptor.salt
            b"0" * 16,  # nonce TODO: encryptor.nonce
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
    ):
        *_, redundant_bits, encryption_type, salt, nonce, data_size = Message.decode_header(header_bytes)
        encryptor = EncryptionProvider.get_encryptor(EncryptionType(encryption_type), decryption=True)
        data = Message.__decode_error_correction(data_bytes, redundant_bits)
        data = Message.__decrypt(data, encryptor)

        return data

    @staticmethod
    def __decode_error_correction(data: bytes, redundant_bits: int):

        # if redundant_bits > 0:
        #    data = Message.__correct_errors_hamming(data, redundant_bits)

        data = Message.__decode_rs_hamming_error_correction(data)

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
    def __encode_error_correction(data: bytes, redundant_bits: int) -> bytes:

        # if redundant_bits > 0:
        #    data = HammingErrorCorrection.encode_hamming_error_correction(data, redundant_bits)

        data = Message.__encode_rs_error_correction(data)

        return data

    @staticmethod
    def __decode_hamming_error_correction(data: bytes, redundant_bits: int) -> bytes:

        data = HammingErrorCorrection.decode_hamming_error_correction(data, redundant_bits)

        return data

    @staticmethod
    def __encode_rs_error_correction(data: bytes) -> bytes:

        data = ReedSolomon.encode(data)

        return data

    @staticmethod
    def __decode_rs_hamming_error_correction(data: bytes) -> bytes:

        data = ReedSolomon.decode(data)

        return data

    @staticmethod
    def __message_as_bytes(message: Union[bytes, str]):
        if isinstance(message, str):
            message = message.encode("UTF-8")

        return message
