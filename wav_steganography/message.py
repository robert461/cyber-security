import struct
from dataclasses import dataclass
from typing import Union, Optional, List, Tuple


@dataclass
class DataChunk:
    data: bytes
    least_significant_bits: int
    every_nth_byte: int


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

    class Encoder:
        """ Creates header and encrypted data """
        @staticmethod
        def message_as_bytes(message: Union[bytes, str]):
            if isinstance(message, str):
                message = message.encode("UTF-8")
            return message

        def __init__(
                self,
                data: Union[bytes, str],
                least_significant_bits: int,
                every_nth_byte: int,
                password: Optional[str] = None
        ):
            data: bytes = self.message_as_bytes(data)
            data = Message._encrypt(data, password)
            data = Message._encode_error_correction(data)
            header_data = struct.pack(Message.HEADER_FORMAT, least_significant_bits, every_nth_byte, len(data))
            self.header = DataChunk(header_data, Message.HEADER_LSB_COUNT, Message.HEADER_EVERY_NTH_BYTE)
            self.data = DataChunk(data, least_significant_bits, every_nth_byte)

    class Decoder:
        """ Decodes header and encrypted data """
        def __init__(self, header_data: bytes, password: Optional[str] = None):
            self.least_significant_bits, self.every_nth_byte, self.data_size = struct.unpack(
                Message.HEADER_FORMAT, header_data
            )
            self.password = password

        def decode(self, data: bytes) -> bytes:
            data = Message._decode_error_correction(data)
            return Message._decrypt(data, self.password)

    @staticmethod
    def _encrypt(data: bytes, password: Optional[str]) -> bytes:
        if password is None:
            return data
        # TODO Add encryption here
        return data

    @staticmethod
    def _decrypt(data: bytes, password: Optional[str]) -> bytes:
        if password is None:
            return data
        # TODO Add decryption here
        return data

    @staticmethod
    def _encode_error_correction(data: bytes) -> bytes:
        # TODO Add error correction (possibly add parameters, e.g. hamming distance)
        return data

    @staticmethod
    def _decode_error_correction(data: bytes) -> bytes:
        # TODO Add error correction (possibly add parameters, e.g. hamming distance)
        return data
