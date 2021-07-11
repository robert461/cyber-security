from reedsolo import RSCodec

from error_correction.error_correction_type import ErrorCorrectionType
from error_correction.generic_error_correction import GenericErrorCorrection


class ReedSolomonErrorCorrection(GenericErrorCorrection):
    """Reed solomon wrapper for the reedsolo pip package

    redundant_bits show the number of bits to add for error correction for each byte. This has
    to be converted to the total number of redundant bytes for the entire message to be able to
    use the reedsolo package.

    https://pypi.org/project/reedsolo/
    """

    def __init__(self):
        super().__init__(ErrorCorrectionType.REED_SOLOMON)

    @staticmethod
    def _get_ecc_byte_count_per_chunk(redundant_bits):
        reed_solomon_chunk_size = 255
        if not (0 <= redundant_bits < reed_solomon_chunk_size * 8):
            raise ValueError(f"ERROR: Too many redundant bits: {redundant_bits},"
                             f" must be less than {reed_solomon_chunk_size * 8}.")
        redundant_bytes = redundant_bits // 8
        data_bytes = reed_solomon_chunk_size // (redundant_bytes + 1)
        ecc_bits = max(1, reed_solomon_chunk_size - data_bytes)
        if reed_solomon_chunk_size <= ecc_bits:
            raise ValueError(f"ERROR: Cannot apply error correction with {redundant_bits=}.")
        return ecc_bits

    @staticmethod
    def encode(data: bytes, redundant_bits: int) -> bytes:

        if redundant_bits == 0:
            return data

        ecc_byte_count_per_chunk = ReedSolomonErrorCorrection._get_ecc_byte_count_per_chunk(redundant_bits)

        rsc = RSCodec(ecc_byte_count_per_chunk)
        encoded_data = rsc.encode(data)

        return bytes(encoded_data)

    @staticmethod
    def decode(data: bytes, redundant_bits: int) -> bytes:

        if redundant_bits == 0:
            return data

        ecc_byte_count_per_chunk = ReedSolomonErrorCorrection._get_ecc_byte_count_per_chunk(redundant_bits)

        rsc = RSCodec(ecc_byte_count_per_chunk)

        decoded_msg = rsc.decode(data)[0]

        # important to return bytes, as rsc returns a bytearray, which causes errors in various encryptors
        return bytes(decoded_msg)
