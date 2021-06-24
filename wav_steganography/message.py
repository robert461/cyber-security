import struct
from typing import Union, Optional

from encryption.generic_encryptor import GenericEncryptor
from encryption.none_encryptor import NoneEncryptor
from wav_steganography.data_chunk import DataChunk
from error_correction.hamming_error_correction import HammingErrorCorrection


class Message:
    """ A message class implementing an Encoder and an Decoder

    This header is used to encode the meta information for the message before the actual data part.
    Currently, this is 3 integers, 7 bytes:
        * The least significant bits used in the data
        * The nth bits used in the data
        * The length in data in bytes (excluding the header)
    For the header, the values are defined below.
    """
    HEADER_FORMAT = "<BHI"
    HEADER_BYTE_SIZE = struct.calcsize(HEADER_FORMAT)
    HEADER_LSB_COUNT = 1
    HEADER_EVERY_NTH_BYTE = 1

    def __init__(self):
        self.header = None
        self.data = None

    def encode_message(
            self,
            data: Union[bytes, str],
            least_significant_bits: int,
            every_nth_byte: int,
            redundant_bits: int,
            encryptor: Optional[GenericEncryptor] = NoneEncryptor(),
            error_correction: bool = False):

        data: bytes = Message.__message_as_bytes(data)

        if error_correction:
            data = Message.__encode_error_correction(data, redundant_bits)

        data = Message.__encrypt(data, encryptor)

        header_data = struct.pack(Message.HEADER_FORMAT, least_significant_bits, every_nth_byte, len(data))
        self.header = DataChunk(header_data, Message.HEADER_LSB_COUNT, Message.HEADER_EVERY_NTH_BYTE)
        self.data = DataChunk(data, least_significant_bits, every_nth_byte)

    def decode_message(
            self,
            data: bytes,
            encryptor: Optional[GenericEncryptor] = NoneEncryptor(),
            redundant_bits: int = 4,
            error_correction: bool = False):

        data = self.__decrypt(data, encryptor)

        if error_correction:
            data = self.__decode_error_correction(data, redundant_bits)

        return data

    def __decode_error_correction(self, data: bytes, redundant_bits: int):

        data = self.__correct_errors_hamming(data, redundant_bits)

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

        data = HammingErrorCorrection.encode_hamming_error_correction(data, redundant_bits)

        return data

    @staticmethod
    def __decode_hamming_error_correction(data: bytes, redundant_bits: int) -> bytes:

        data = HammingErrorCorrection.decode_hamming_error_correction(data, redundant_bits)

        return data

    @staticmethod
    def __message_as_bytes(message: Union[bytes, str]):
        if isinstance(message, str):
            message = message.encode("UTF-8")

        return message
