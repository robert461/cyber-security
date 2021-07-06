from reedsolo import RSCodec

from error_correction.generic_error_correction import GenericErrorCorrection


class NoneErrorCorrection(GenericErrorCorrection):
    """
        No actual error correction
    """

    @staticmethod
    def encode(data: bytes, redundant_bits: int) -> bytes:

        return data

    @staticmethod
    def decode(data: bytes, redundant_bits: int) -> bytes:

        return data
